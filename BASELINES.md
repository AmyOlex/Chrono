Author: Nicholas Morton

# Baseline Description

The baseline chosen for this project was to compare the TIMEX3 and Chrono entities produced by a different system (HeidelTime and GUTime) than the one used in our project (SUTime).  Heidel time was developed at Heidelberg University, like SUTime it extracts temporal expressions into the TIMEX3 format.  GUTime also extracts temporal expressions into the TIMEX3 format.

Similar to how SUTime was used, we generated Chrono Entities from the list of HeidelTime Entities and computed results from the AnaforaTools. Each input file was ran with HeidelTime's standalone system and the results were parsed into a HeidTime list (see BaselineCode/HeidelTime for more details).  Once the HeidTime List was generated, using similar methods from SUTime_To_Chrono.py. Chrono Entites were generated for the Year, Month, Day, Hour, Second, and Minute.

Similar to how SUTime was used, we generated Chrono Entities from the list of GUTime Entities and computed results from the AnaforaTools. Each input file was ran with the TARSQI toolkit which incorporates GUTime system.  This was done so the files could be in the proper GUTime format to generate our GUTimeList. The results were parsed into a GUTime list (see BaselineCode/GUTime for more details).  Once the GUTime List was generated, using similar methods from SUTime_To_Chrono.py. Chrono Entites were generated for the Year, Month, Day, Hour, Second, and Minute.

# Baseline Evaluation

Based on the results SUTime performed better in generating the best Anafora output, when comparing the outputs of the anaforatools evaluation script.  However, this is really not a good baseline comparision.  Given that Heidel Time does not return the SPANS like SUTime does, the precision and recall values were much worse. 

When Run with GUTime, the results were better than Heidel Time but still worse than SUTime's overall results.

See the table below for more details.

# Baseline Results

## STAGE 1 RESULTS:

| Implementation                   | Precision | Recall |   F1  |
| -------------------------------- | --------- | ------ | ----- |
| Chrono - 100% Entity Correct         |  0.269    | 0.253  | 0.260 |
| HeidelTime - 100% Entity Correct |  0.003    | 0.002  | 0.002 |
| -------------------------------- | --------- | ------ | ----- |
| Chrono - Corrent Spans               |  0.606    | 0.522  | 0.561 |
| HeidelTime - Correct Spans       |  0.013    | 0.007  | 0.009 |

## STAGE 2 RESULTS (Training Data - 67 files):

| Implementation                   | Precision | Recall |   F1  |
| -------------------------------- | --------- | ------ | ----- |
| ChronoNB - 100% Entity Correct         |  0.489    | 0.436  | 0.461 |
| ChronoNN - 100% Entity Correct         |  0.490    | 0.437  | 0.462 |
| ChronoDT - 100% Entity Correct         |  0.488    | 0.435  | 0.460 |
| GUTime - 100% Entity Correct     |  0.086    | 0.025  | 0.38 |
| -------------------------------- | --------- | ------ | ----- |
| ChronoNB - Corrent Spans               |  0.787    | 0.590  | 0.674 |
| ChronoNN - Corrent Spans               |  0.787    | 0.590  | 0.674 |
| ChronoDT - Corrent Spans               |  0.782    | 0.586  | 0.670 |
| GUTime - Correct Spans           |  0.736    | 0.171  | 0.278 |

## STAGE 2 RESULTS (Test Data - 11 files):

See Table in README.

# Conclusion

Based on the results, our implementation was significantly better than our HeidelTime baseline and marginally better than GUTime.  
