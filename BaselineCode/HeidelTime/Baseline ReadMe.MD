# Baseline HeidelTime Readme

When implementing a baseline, it became apperant that there wasn't a good tool to use as a baseline based off of our task.  Therefore we decided to simply compare our temporal text analyzer (SUTime) with another 3rd party tool (HeidelTime).  Unfortunately, HeidelTime does not provide the start/end spans of the temporal expressions it reads, this made it difficult to compare to SUTime.  Ultimately, we used a similar method to our main program implementation to create T6Entities parsed from HeidelTimes' output.  The Spans were calculated based off of reference spans to produce a somewhat accurate test.  The code provided in this folder is not meant to be run with the rest of our code, but is more to serve a reference on how our baseline results were achieved.

Several methods were modified/reused from the main implmentation so the authorship will be similar to that of the main code files.

Two 3rd party applications which were required: (1) HeidelTime and (2) TreeTagger are not provided but were used in this implementation.  Links to both can be found in the sources section below.
