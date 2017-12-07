Author: Nicholas Morton

---Explain your baseline in words---

The baseline chosen for this project was to compare the TIMEX3 and T6 entities produced by a different system (HeidelTime and GUTime) than the one used in our project (SUTime).  Heidel time was developed at Heidelberg University, like SUTime it extracts temporal expressions into the TIMEX3 format.  GUTime also extracts temporal expressions into the TIMEX3 format.

Similar to how SUTime was used, we generated T6 Entities from the list of HeidelTime Entities and computed results from the AnaforaTools. Each input file was ran with HeidelTime's standalone system and the results were parsed into a HeidTime list (see BaselineCode/HeidelTime for more details).  Once the HeidTime List was generated, using similar methods from SUTime_To_T6.py. T6 Entites were generated for the Year, Month, Day, Hour, Second, and Minute.

Similar to how SUTime was used, we generated T6 Entities from the list of GUTime Entities and computed results from the AnaforaTools. Each input file was ran with the TARSQI toolkit which incorporates GUTime system.  This was done so the files could be in the proper GUTime format to generate our GUTimeList. The results were parsed into a GUTime list (see BaselineCode/GUTime for more details).  Once the GUTime List was generated, using similar methods from SUTime_To_T6.py. T6 Entites were generated for the Year, Month, Day, Hour, Second, and Minute.

---Explain your evaluation metric---

Based on the results SUTime performed better in generating the best Anafora output, when comparing the outputs of the anaforatools evaluation script.  However, this is really not a good baseline comparision.  Given that Heidel Time does not return the SPANS like SUTime does, the precision and recall values were much worse. 

When Run with GUTime, the results were better than Heidel Time but still worse than SUTime's overall results.

See the table below for more details.

---Put your results and the baseline results in a table---

STAGE 1 RESULTS:

| Implementation                   | Precision | Recall |   F1  |
| -------------------------------- | --------- | ------ | ----- |
| T6 - 100% Entity Correct         |  0.269    | 0.253  | 0.260 |
| HeidelTime - 100% Entity Correct |  0.003    | 0.002  | 0.002 |
| -------------------------------- | --------- | ------ | ----- |
| T6 - Corrent Spans               |  0.606    | 0.522  | 0.561 |
| HeidelTime - Correct Spans       |  0.013    | 0.007  | 0.009 |

STAGE 2 RESULTS:

| Implementation                   | Precision | Recall |   F1  |
| -------------------------------- | --------- | ------ | ----- |
| ChronoNB - 100% Entity Correct   |  0.439    | 0.420  | 0.429 |
| ChronoNN - 100% Entity Correct   |  0.430    | 0.411  | 0.420 |
| ChronoDT - 100% Entity Correct   |  0.434    | 0.416  | 0.425 |
| GUTime - 100% Entity Correct     |  0.534    | 0.169  | 0.260 |
| -------------------------------- | --------- | ------ | ----- |
| ChronoNB - Corrent Spans         |  0.648    | 0.550  | 0.595 | 
| ChronoNN - Corrent Spans         |  0.643    | 0.545  | 0.590 |
| ChronoDT - Corrent Spans         |  0.663    | 0.563  | 0.609 |
| GUTime - Correct Spans           |  0.923    | 0.260  | 0.405 |

---Explain your table---

Based on the results, our implementation was significantly better than our HeidelTime baseline and marginally better than GUTime.  
