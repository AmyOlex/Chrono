__author__ = 'bethard'

import argparse
import collections
import copy
import functools
import glob
import logging
import os
import re

import anafora
import anafora.select


class Scores(object):

    def __init__(self):
        self.reference = 0
        self.predicted = 0
        self.correct = 0

    def add(self, reference, predicted):
        """
        :param set reference: the reference annotations
        :param set predicted: the predicted annotations
        """
        self.reference += len(reference)
        self.predicted += len(predicted)
        self.correct += len(reference & predicted)

    def update(self, other):
        """
        :param Scores other: scores to merge into this one
        """
        self.reference += other.reference
        self.predicted += other.predicted
        self.correct += other.correct

    def precision(self):
        """
        :return float: the fraction of predicted annotations that were correct
        """
        return 1.0 if self.predicted == 0 else self.correct / float(self.predicted)

    def recall(self):
        """
        :return float: the fraction of reference annotations that were found
        """
        return 1.0 if self.reference == 0 else self.correct / float(self.reference)

    def f1(self):
        """
        :return float: the harmonic mean of precision and recall
        """
        p = self.precision()
        r = self.recall()
        return 0.0 if p + r == 0.0 else 2 * p * r / (p + r)

    def __repr__(self):
        return "{0}(reference={1}, predicted={2}, correct={3})".format(
            self.__class__.__name__, self.reference, self.predicted, self.correct
        )


class DebuggingScores(Scores):
    def __init__(self):
        Scores.__init__(self)
        self.errors = []

    def add(self, reference, predicted):
        """
        :param set reference: the reference annotations
        :param set predicted: the predicted annotations
        """
        Scores.add(self, reference, predicted)
        errors = []
        for item in reference - predicted:
            errors.append((item, "not in predicted"))
        for item in predicted - reference:
            errors.append((item, "not in reference"))
        errors.sort()
        self.errors.extend(errors)

    def update(self, other):
        """
        :param DebuggingScores other: scores to merge into this one
        """
        Scores.update(self, other)
        self.errors.extend(other.errors)


class TemporalClosureScores(object):
    def __init__(self):
        self.reference = 0
        self.predicted = 0
        self.precision_correct = 0
        self.recall_correct = 0

    @property
    def correct(self):
        return self.precision_correct, self.recall_correct

    def add(self, reference, predicted):
        """
        :param set reference: the reference annotations
        :param set predicted: the predicted annotations
        """
        reference = {a for a in reference if self._is_valid(a)}
        predicted = {a for a in predicted if self._is_valid(a)}
        reference = self._remove_duplicate_relations(reference)
        predicted = self._remove_duplicate_relations(predicted)
        self.reference += len(reference)
        self.predicted += len(predicted)
        self.precision_correct += len(self._closure(reference) & predicted)
        self.recall_correct += len(reference & self._closure(predicted))

    def update(self, other):
        """
        :param TemporalClosureScores other: scores to merge into this one
        """
        self.reference += other.reference
        self.predicted += other.predicted
        self.precision_correct += other.precision_correct
        self.recall_correct += other.recall_correct

    def precision(self):
        """
        :return float: the fraction of predicted annotations that were correct (or inferable)
        """
        return 1.0 if self.predicted == 0 else self.precision_correct / float(self.predicted)

    def recall(self):
        """
        :return float: the fraction of reference annotations that were found (or inferable)
        """
        return 1.0 if self.reference == 0 else self.recall_correct / float(self.reference)

    def f1(self):
        """
        :return float: the harmonic mean of precision and recall
        """
        p = self.precision()
        r = self.recall()
        return 0.0 if p + r == 0.0 else 2 * p * r / (p + r)

    def __repr__(self):
        return "{0}(reference={1}, predicted={2}, precision_correct={3}, recall_correct={4})".format(
            self.__class__.__name__, self.reference, self.predicted, self.precision_correct, self.recall_correct
        )

    def _is_valid(self, annotation):

        # temporal closure only makes sense on a single property, not an entire annotation
        if not isinstance(annotation, _AnnotationView):
            raise RuntimeError("temporal closure cannot be applied to {0}".format(annotation))

        # temporal closure only makes sense with binary relations
        if len(annotation.spans) != 2:
            logging.warning("invalid spans for temporal closure {0}".format(annotation))
            return False

        # temporal closure only works on a defined set of temporal relations
        if annotation.value not in self._interval_to_point:
            logging.warning("invalid relation for temporal closure {0}".format(annotation))
            return False

        # otherwise, temporal closure should work
        return True

    def _remove_duplicate_relations(self, annotations):
        seen_point_relations = set()
        result_annotations = set()
        for annotation in annotations:

            # only include this annotation if no previous annotation expanded to the same point relations
            point_relations = frozenset(self._to_point_relations(annotation))
            if point_relations not in seen_point_relations:
                seen_point_relations.add(point_relations)
                result_annotations.add(annotation)

        # return the filtered annotations
        return result_annotations

    def _to_point_relations(self, annotation):
        start = self._start
        end = self._end

        # converts an interval relation to point relations
        point_relations = set()
        intervals = annotation.spans
        interval1, interval2 = intervals

        # the start of an interval is always before its end
        point_relations.add(((interval1, start), "<", (interval1, end)))
        point_relations.add(((interval2, start), "<", (interval2, end)))

        # use the interval-to-point lookup table to add the necessary point relations
        for index1, side1, relation, index2, side2 in self._interval_to_point[annotation.value]:
            point1 = (intervals[index1], side1)
            point2 = (intervals[index2], side2)
            point_relations.add((point1, relation, point2))

            # for reflexive point relations, add them in the other direction too
            if relation == "=":
                point_relations.add((point2, relation, point1))

        # return the collected relations
        return point_relations

    def _to_interval_relations(self, point_relations, annotations):

        # map intervals to names
        interval_names = collections.defaultdict(set)
        for annotation in annotations:
            for span in annotation.spans:
                interval_names[span].add(annotation.name)

        # find all pairs of intervals that have some point relation between them (and whose names match)
        pair_names = {}
        for ((interval1, _), _, (interval2, _)) in point_relations:
            names = interval_names[interval1] & interval_names[interval2]
            if names:
                pair_names[(interval1, interval2)] = names
                pair_names[(interval2, interval1)] = names

        # for each interval pair, see if it satisfies the point-wise requirements for any interval relations
        interval_relations = set()
        for pair in pair_names:
            names = pair_names[pair]
            for relation, requirements in self._interval_to_point.items():
                if all(((pair[i1], s1), r, (pair[i2], s2)) in point_relations
                       for i1, s1, r, i2, s2 in requirements):
                    for name in names:
                        interval_relations.add(_AnnotationView(pair, name, relation))

        # return the collected relations
        return interval_relations

    def _closure(self, annotations):

        # convert interval relations to point relations
        new_relations = {r for a in annotations for r in self._to_point_relations(a)}

        # repeatedly apply point transitivity rules until no new relations can be inferred
        point_relations = set()
        point_relations_index = collections.defaultdict(set)
        while new_relations:

            # update the result and the index with any new relations found on the last iteration
            point_relations.update(new_relations)
            for point_relation in new_relations:
                point_relations_index[point_relation[0]].add(point_relation)

            # infer any new transitive relations, e.g., if A < B and B < C then A < C
            new_relations = set()
            for point1, relation12, point2 in point_relations:
                for _, relation23, point3 in point_relations_index[point2]:
                    relation13 = self._point_transitions[relation12][relation23]
                    new_relation = (point1, relation13, point3)
                    if new_relation not in point_relations:
                        new_relations.add(new_relation)

        # convert the point relations back to interval relations
        return self._to_interval_relations(point_relations, annotations)

    # constants representing the start point and end point of an interval
    _start = 0
    _end = 1

    # mapping from interval relation names to point relations
    # for example, BEFORE means that the first interval's end is before the second interval's start
    _interval_to_point = {
        "BEFORE": [(0, _end, "<", 1, _start)],
        "AFTER": [(1, _end, "<", 0, _start)],
        "IBEFORE": [(0, _end, "=", 1, _start)],
        "IAFTER": [(0, _start, "=", 1, _end)],
        "CONTAINS": [(0, _start, "<", 1, _start), (1, _end, "<", 0, _end)],
        "INCLUDES": [(0, _start, "<", 1, _start), (1, _end, "<", 0, _end)],
        "IS_INCLUDED": [(1, _start, "<", 0, _start), (0, _end, "<", 1, _end)],
        "BEGINS-ON": [(0, _start, "=", 1, _start)],
        "ENDS-ON": [(0, _end, "=", 1, _end)],
        "BEGINS": [(0, _start, "=", 1, _start), (0, _end, "<", 1, _end)],
        "BEGUN_BY": [(0, _start, "=", 1, _start), (1, _end, "<", 0, _end)],
        "ENDS":  [(1, _start, "<", 0, _start), (0, _end, "=", 1, _end)],
        "ENDED_BY":  [(0, _start, "<", 1, _start), (0, _end, "=", 1, _end)],
        "SIMULTANEOUS": [(0, _start, "=", 1, _start), (0, _end, "=", 1, _end)],
        "IDENTITY": [(0, _start, "=", 1, _start), (0, _end, "=", 1, _end)],
        "DURING": [(0, _start, "=", 1, _start), (0, _end, "=", 1, _end)],
        "DURING_INV": [(0, _start, "=", 1, _start), (0, _end, "=", 1, _end)],
        "OVERLAP": [(0, _start, "<", 1, _end), (1, _start, "<", 0, _end)],
    }

    # transitivity table for point relations
    _point_transitions = {
        "<": {"<": "<", "=": "<"},
        "=": {"<": "<", "=": "="},
    }


# This is basically a hack to redefine span hashing and equality for all annotations
@functools.total_ordering
class _OverlappingWrapper(object):
    def __init__(self, annotation, seen=None):
        self.annotation = annotation
        self.type = self.annotation.type
        self.parents_type = self.annotation.parents_type
        self.spans = tuple(self._to_overlapping_spans(self.annotation.spans))
        if seen is None:
            seen = set()
        self.properties = {}
        for name, value in self.annotation.properties.items():
            if id(value) not in seen:
                seen.add(id(value))
                if isinstance(value, anafora.AnaforaAnnotation):
                    self.properties[name] = _OverlappingWrapper(value, seen)
                else:
                    self.properties[name] = value

    def _to_overlapping_spans(self, items):
        if isinstance(items, tuple) and isinstance(items[0], tuple) and isinstance(items[0][0], int):
            yield _OverlappingSpans(items)
        else:
            for item in items:
                for overlapping_spans in self._to_overlapping_spans(item):
                    yield overlapping_spans

    @property
    def __class__(self):
        return anafora.AnaforaAnnotation

    def _key(self):
        return self.spans, self.type, self.parents_type, self.properties

    def __eq__(self, other):
        return (
            isinstance(other, _OverlappingWrapper) and
            self.spans == other.spans and
            self.type == other.type and
            self.parents_type == other.parents_type and
            self.properties == other.properties)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        result = 0
        for item in self.properties.items():
            result += hash(item)
        return result

    def __lt__(self, other):
        return self.spans < other.spans

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.annotation)


# This is part of the hack above to redefine span hashing and equality for all annotations
@functools.total_ordering
class _OverlappingSpans(object):
    def __init__(self, spans):
        self.spans = spans

    def __iter__(self):
        return iter(self.spans)

    def __eq__(self, other):
        for self_start, self_end in self.spans:
            for other_start, other_end in other.spans:
                if self_start < other_end and other_start < self_end:
                    return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return 0

    def __lt__(self, other):
        return self.spans < other.spans

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.spans)


# A type used to capture just a part of an annotation, e.g., just its spans, or just a single property
_AnnotationView = collections.namedtuple("AnnotationView", ["spans", "name", "value"])


def score_data(reference_data, predicted_data, include=None, exclude=None,
               scores_type=Scores, annotation_wrapper=None):
    """
    :param AnaforaData reference_data: reference ("gold standard") Anafora data
    :param AnaforaData predicted_data: predicted (system-generated) Anafora data
    :param set include: types of annotations to include (others will be excluded); may be type names,
        (type-name, property-name) tuples, (type-name, property-name, property-value) tuples
    :param set exclude: types of annotations to exclude; may be type names, (type-name, property-name) tuples,
        (type-name, property-name, property-value) tuples
    :param type scores_type: type for calculating matches between predictions and reference
    :param type annotation_wrapper: wrapper type to apply to AnaforaAnnotations
    :return dict: mapping from (annotation type[, property name[, property value]]) to Scores object
    """

    # groups items from iterables by a key function
    def _group_by(reference_iterable, predicted_iterable, key_function):
        groups = collections.defaultdict(lambda: (set(), set()))
        for iterable, index in [(reference_iterable, 0), (predicted_iterable, 1)]:
            for item in iterable:
                groups[key_function(item)][index].add(item)
        return groups

    # returns true if this type:property:value is accepted by includes= and excludes=
    select = anafora.select.Select(include, exclude)

    # generates a view of just the annotation's spans, and of each of its selected properties
    def _views(annotations):
        views = set()
        for ann in annotations:
            spans = ann.spans
            if select(ann.type, "<span>"):
                views.add(_AnnotationView(spans, (ann.type, "<span>"), None))
            for view_name in ann.properties:
                view_value = ann.properties[view_name]
                if view_value is None:
                    view_value = '<none>'
                if select(ann.type, view_name):
                    views.add(_AnnotationView(spans, (ann.type, view_name), view_value))
                if select(ann.type, view_name, view_value) and not isinstance(view_value, anafora.AnaforaAnnotation):
                    views.add(_AnnotationView(spans, (ann.type, view_name, view_value), view_value))
        return views

    # get reference and predicted annotations
    reference_annotations = reference_data.annotations
    predicted_annotations = [] if predicted_data is None else predicted_data.annotations

    # FIXME: this avoids counting excluded properties, but modifies the data
    def _del_excluded_properties(annotations):
        for ann in annotations:
            if select(ann.type):
                for name in list(ann.properties):
                    if not select(ann.type, name):
                        del ann.properties[name]
    _del_excluded_properties(reference_annotations)
    _del_excluded_properties(predicted_annotations)

    # if necessary, wrap the annotations in a wrapper class
    if annotation_wrapper is not None:
        reference_annotations = map(annotation_wrapper, reference_annotations)
        predicted_annotations = map(annotation_wrapper, predicted_annotations)

    # fill a mapping from a name (type, type:property or type:property:value) to the corresponding scores
    result = collections.defaultdict(lambda: scores_type())
    results_by_type = _group_by(reference_annotations, predicted_annotations, lambda a: a.type)
    for ann_type in sorted(results_by_type):

        # update whole-annotation scores
        type_reference_annotations, type_predicted_annotations = results_by_type[ann_type]
        if select(ann_type):
            result["*"].add(type_reference_annotations, type_predicted_annotations)
            result[ann_type].add(type_reference_annotations, type_predicted_annotations)

        # update span and property scores
        reference_views = _views(type_reference_annotations)
        predicted_views = _views(type_predicted_annotations)
        results_by_view = _group_by(reference_views, predicted_views, lambda t: t.name)
        for view_name in sorted(results_by_view):
            view_reference_annotations, view_predicted_annotations = results_by_view[view_name]
            result[view_name].add(view_reference_annotations, view_predicted_annotations)
            if isinstance(view_name, tuple) and len(view_name) == 2 and view_name[1] == "<span>":
                result["*", "<span>"].add(view_reference_annotations, view_predicted_annotations)

    # return the collected scores
    return result


def _load(xml_path):
    """
    Tries to load data from an Anafora XML file, issuing errors on failure.

    :param xml_path: the path to an Anafora XML file
    :return AnaforaData: the data loaded from the XML, or None if there was a failure
    """
    if not os.path.exists(xml_path):
        logging.warn("%s: no such file", xml_path)
        return None
    try:
        data = anafora.AnaforaData.from_file(xml_path)
    except anafora.ElementTree.ParseError:
        logging.warn("%s: ignoring invalid XML", xml_path)
        return None
    else:
        return data


def score_dirs(reference_dir, predicted_dir, xml_name_regex="[.]xml$", text_dir=None,
               include=None, exclude=None, scores_type=Scores, annotation_wrapper=None):
    """
    :param string reference_dir: directory containing reference ("gold standard") Anafora XML directories
    :param string predicted_dir: directory containing predicted (system-generated) Anafora XML directories
    :param xml_name_regex: regular expression matching the files to be compared
    :param string text_dir: directory containing the raw texts corresponding to the Anafora XML
        (if None, texts are assumed to be in the reference dir)
    :param set include: types of annotations to include (others will be excluded); may be type names,
        (type-name, property-name) tuples, (type-name, property-name, property-value) tuples
    :param set exclude: types of annotations to exclude; may be type names, (type-name, property-name) tuples,
        (type-name, property-name, property-value) tuples
    :param type scores_type: type for calculating matches between predictions and reference
    :param type annotation_wrapper: wrapper object to apply to AnaforaAnnotations
    :return iter: an iterator of (file-name, name-to-scores) where name-to-scores is a mapping from
        (annotation type[, property name[, property value]]) to a Scores object
    """

    # walks through the reference Anafora XML directories, scoring each and adding those to the overall scores
    for sub_dir, text_name, reference_xml_names in anafora.walk(reference_dir, xml_name_regex):

        # load the reference data from its Anafora XML
        try:
            [reference_xml_name] = reference_xml_names
        except ValueError:
            logging.warn("expected one reference file for %s, found %s", text_name, reference_xml_names)
            if not reference_xml_names:
                continue
            reference_xml_name = reference_xml_names[0]
        reference_xml_path = os.path.join(reference_dir, sub_dir, reference_xml_name)
        reference_data = _load(reference_xml_path)

        # check for self-references in the annotations, which cause equality and hashing to fail
        self_reference = reference_data.annotations.find_self_referential()
        if self_reference is not None:
            msg = "skipping reference file %s with self-referential annotation %s"
            logging.warn(msg, reference_xml_path, self_reference.id)
            continue

        # find and load the corresponding predicted data from its Anafora XML
        predicted_xml_glob = os.path.join(predicted_dir, sub_dir, text_name + "*.xml")
        predicted_xml_paths = [f for f in glob.glob(predicted_xml_glob) if re.search(xml_name_regex, f) is not None]
        try:
            [predicted_xml_path] = predicted_xml_paths
            predicted_data = _load(predicted_xml_path)
        except ValueError:
            logging.warn("expected one predicted file at %s, found %s", predicted_xml_glob, predicted_xml_paths)
            if not predicted_xml_paths:
                predicted_xml_path = None
                predicted_data = anafora.AnaforaData()
            else:
                predicted_xml_path = predicted_xml_paths[0]
                predicted_data = _load(predicted_xml_path)

        # check for self-references in the annotations, which cause equality and hashing to fail
        self_reference = predicted_data.annotations.find_self_referential()
        if self_reference is not None:
            msg = "skipping predicted file %s with self-referential annotation %s"
            logging.warn(msg, predicted_xml_path, self_reference.id)
            predicted_data = anafora.AnaforaData()

        # determine the path for the raw text source file
        if text_dir is None:
            text_path = os.path.join(reference_dir, sub_dir, text_name)
        else:
            text_path = os.path.join(text_dir, text_name)

        # if no raw text was found, then asking for the text of an annotation is an error
        if not os.path.exists(text_path) or not os.path.isfile(text_path):
            def _span_text(_):
                raise RuntimeError("no text file found at {0}".format(text_path))

        # otherwise, the text of an annotation can be extracted based on its spans
        else:
            with open(text_path) as text_file:
                text = text_file.read()

            def _flatten(items):
                if isinstance(items, tuple) and isinstance(items[0], int):
                    yield items
                else:
                    for item in items:
                        for flattened_items in _flatten(item):
                            yield flattened_items

            def _span_text(spans):
                return "...".join(text[start:end] for start, end in _flatten(spans))

        # score this data and update the overall scores
        named_scores = score_data(reference_data, predicted_data, include, exclude,
                                  scores_type=scores_type, annotation_wrapper=annotation_wrapper)
        for name, scores in named_scores.items():

            # if there were some predictions, and if we're using scores that keep track of errors, log the errors
            if predicted_xml_paths:
                for annotation, message in getattr(scores, "errors", []):
                    logging.debug('%s: %s: "%s" %s"', text_name, message, _span_text(annotation.spans), annotation)

        # generate the file name and the resulting scores
        yield text_name, named_scores

def score_annotators(anafora_dir, xml_name_regex, include=None, exclude=None,
                     scores_type=Scores, annotation_wrapper=None):
    """
    :param anafora_dir: directory containing Anafora XML directories
    :param xml_name_regex: regular expression matching the annotator files to be compared
    :param include: types of annotations to include (others will be excluded); may be type names,
        (type-name, property-name) tuples, (type-name, property-name, property-value) tuples
    :param set exclude: types of annotations to exclude; may be type names, (type-name, property-name) tuples,
        (type-name, property-name, property-value) tuples
    :param type scores_type: type for calculating matches between predictions and reference
    :param type annotation_wrapper: wrapper object to apply to AnaforaAnnotations
    :return iter: an iterator of (file-name, name-to-scores) where name-to-scores is a mapping from
        (annotation type[, property name[, property value]]) to a Scores object
    """

    # pattern for extracting the annotator name from the Anafora XML file name
    annotator_name_regex = "([^.]*)[.][^.]*[.]xml$"

    # function for getting a canonical prefix corresponding to a pair of annotators
    def make_prefix(annotators):
        return "{0}-vs-{1}".format(*sorted(annotators))

    # walks through the Anafora XML directories, scoring each and adding those to the overall scores
    for sub_dir, text_name, xml_names in anafora.walk(anafora_dir, xml_name_regex):

        # load the data from each Anafora XML file
        annotator_data = []
        for xml_name in xml_names:

            # ignore in-progress annotations and automatic pre-annotations
            if '.inprogress.' in xml_name or '.preannotation.' in xml_name:
                continue

            # ignore empty files
            xml_path = os.path.join(anafora_dir, sub_dir, xml_name)
            if os.stat(xml_path).st_size == 0:
                continue

            # load the data and add it to the list
            data = _load(xml_path)
            annotator_name = re.search(annotator_name_regex, xml_name).group(1)
            annotator_data.append((annotator_name, data))

        # at least 2 annotators are needed for annotator agreement
        if len(annotator_data) < 2:
            logging.warn("%s: found fewer than 2 annotators: %s", text_name, xml_names)
            continue

        # pair each annotator with each other annotator
        annotator_named_scores = collections.defaultdict(lambda: scores_type())
        for i in range(len(annotator_data)):
            annotator1, data1 = annotator_data[i]
            for j in range(i + 1, len(annotator_data)):
                annotator2, data2 = annotator_data[j]

                # make a prefix for this specific pair of annotators
                prefix = make_prefix([annotator1, annotator2])

                # make a prefix where non-gold annotators are just called "annotator"
                general_prefix = make_prefix(
                    a if a == "gold" else "annotator" for a in [annotator1, annotator2])

                # perform the comparison of the two annotation sets and update the overall scores
                named_scores = score_data(data1, data2, include, exclude,
                                          scores_type=scores_type, annotation_wrapper=annotation_wrapper)

                # add annotators as prefixes
                for name, scores in named_scores.items():
                    if not isinstance(name, tuple):
                        name = name,
                    annotator_named_scores[(prefix,) + name].update(scores)
                    annotator_named_scores[(general_prefix,) + name].update(scores)

        # generate the filename and the resulting scores
        yield text_name, annotator_named_scores


def _print_document_scores(file_named_scores):

    def _score_name(x):
        return ":".join(x) if isinstance(x, tuple) else x

    print("{0:40}\t{1:40}\t{2:^5}\t{3:^5}\t{4:^5}\t{5:^5}\t{6:^5}\t{7:^5}".format(
        "", "", "ref", "pred", "corr", "P", "R", "F1"))
    for file_name, named_scores in file_named_scores:
        for name, scores in named_scores.items():
            print("{0!s:40}\t{1!s:40}\t{2!s:5}\t{3!s:5}\t{4!s:5}\t{5:5.3f}\t{6:5.3f}\t{7:5.3f}".format(
                file_name, _score_name(name), scores.reference, scores.predicted, scores.correct,
                scores.precision(), scores.recall(), scores.f1()))


def _print_merged_scores(file_named_scores, scores_type):
    all_named_scores = collections.defaultdict(lambda: scores_type())
    for _, named_scores in file_named_scores:
        for name, scores in named_scores.items():
            all_named_scores[name].update(scores)

    def _score_name(x):
        return ":".join(x) if isinstance(x, tuple) else x

    print("{0:40}\t{1:^5}\t{2:^5}\t{3:^5}\t{4:^5}\t{5:^5}\t{6:^5}".format(
        "", "ref", "pred", "corr", "P", "R", "F1"))
    for name in sorted(all_named_scores, key=_score_name):
        scores = all_named_scores[name]
        print("{0!s:40}\t{1!s:5}\t{2!s:5}\t{3!s:5}\t{4:5.3f}\t{5:5.3f}\t{6:5.3f}".format(
            _score_name(name), scores.reference, scores.predicted, scores.correct,
            scores.precision(), scores.recall(), scores.f1()))


if __name__ == "__main__":
    def split_tuple_on_colons(string):
        result = tuple(string.split(":"))
        return result[0] if len(result) == 1 else result

    parser = argparse.ArgumentParser(description="""%(prog)s compares one directory of Anafora XML annotations to
        another and prints statistics such as precision, recall and F-measure. It can also be used with a single
        Anafora XML directory to compute inter-annotator agreement.""")
    parser.set_defaults(scores_type=Scores)
    parser.add_argument("-r", "--reference", metavar="DIR", dest="reference_dir", required=True,
                        help="The root of a set of Anafora XML directories representing reference annotations.")
    parser.add_argument("-p", "--predicted", metavar="DIR", dest="predicted_dir",
                        help="The root of a set of Anafora XML directories representing system-predicted annotations.")
    parser.add_argument("-t", "--text", metavar="DIR", dest="text_dir",
                        help="A flat directory containing the raw text. By default, the reference directory is " +
                             "assumed to contain the raw text. (Text is typically only needed with --verbose.)")
    parser.add_argument("-i", "--include", metavar="EXPR", nargs="+", type=split_tuple_on_colons,
                        help="An expression identifying types of annotations to be included in the evaluation. " +
                             "The expression takes the form type[:property[:value]. For example, TLINK would only " +
                             "include TLINK annotations (and TLINK properties and property values) in the " +
                             "evaluation, while TLINK:Type:CONTAINS would only include TLINK annotations with a Type " +
                             "property that has the value CONTAINS.")
    parser.add_argument("-e", "--exclude", metavar="EXPR", nargs="+", type=split_tuple_on_colons,
                        help="An expression identifying types of annotations to be excluded from the evaluation. " +
                             "The expression takes the form type[:property[:value] (see --include).")
    parser.add_argument("-x", "--xml-name-regex", metavar="REGEX", default="[.]xml$",
                        help="A regular expression for matching XML files in the subdirectories, typically used to " +
                             "restrict the evaluation to a subset of the available files (default: %(default)r)")
    parser.add_argument("--temporal-closure", action="store_const", const=TemporalClosureScores, dest="scores_type",
                        help="Apply temporal closure on the reference annotations when calculating precision, and " +
                             "apply temporal closure on the predicted annotations when calculating recall. " +
                             "This must be combined with --include to restrict the evaluation to a Type:Property " +
                             "whose values are valid temporal relations (BEFORE, AFTER, INCLUDES, etc.)")
    parser.add_argument("--per-document", action="store_true",
                        help="Print out scores for each document, rather than overall scores")
    parser.add_argument("--verbose", action="store_const", const=DebuggingScores, dest="scores_type",
                        help="Include more information in the output, such as the reference expressions that were " +
                             "and the predicted expressions that were not in the reference.")
    parser.add_argument("--overlap", dest="annotation_wrapper", action="store_const", const=_OverlappingWrapper,
                        help="Count predicted annotation spans as correct if they overlap by one character or more " +
                             "with a reference annotation span. Not intended as a real evaluation method (since what " +
                             "to do with multiple matches is not well defined) but useful for debugging purposes.")
    args = parser.parse_args()
    basic_config_kwargs = {"format": "%(levelname)s:%(message)s"}
    if args.scores_type == DebuggingScores:
        basic_config_kwargs["level"] = logging.DEBUG
    logging.basicConfig(**basic_config_kwargs)

    if args.predicted_dir is not None:
        _file_named_scores = score_dirs(
            reference_dir=args.reference_dir,
            predicted_dir=args.predicted_dir,
            xml_name_regex=args.xml_name_regex,
            text_dir=args.text_dir,
            include=args.include,
            exclude=args.exclude,
            scores_type=args.scores_type,
            annotation_wrapper=args.annotation_wrapper)
    else:
        _file_named_scores = score_annotators(
            anafora_dir=args.reference_dir,
            xml_name_regex=args.xml_name_regex,
            include=args.include,
            exclude=args.exclude,
            scores_type=args.scores_type,
            annotation_wrapper=args.annotation_wrapper)

    if args.per_document:
        _print_document_scores(_file_named_scores)
    else:
        _print_merged_scores(_file_named_scores, scores_type=args.scores_type)
