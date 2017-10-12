Author: Nicholas Morton

---Explain your baseline in words---

The baseline chosen for this project was to compare the TIMEX3 and T6 entities produced by a different system (HeidelTime) than the one used in our project (SUTime).  Heidel time was developed at Heidelberg University, like SUTime it extracts temporal expressions into the TIMEX3 format.  

Similar to how SUTime was used, we generated T6 Entities from the list of HeidelTime Entities and computed results from the AnaforaTools. Each input file was ran with HeidelTime's standalone system and the results were parsed into a HeidTime list (see Baseline code for more details).  Once the HeidTime List was generated, using similar methods from SUTime_To_T6.py. T6 Entites were generated for the Year, Month, Day, Hour, Second, and Minute.

---Explain your evaluation metric---

Based on the results SUTime performed better in generating the best Anafora output, when comparing the outputs of the anaforatools evaluation script.  However, this is really not a good baseline comparision.  Given that Heidel Time does not return the SPANS like SUTime does, the precision and recall values were much worse. There really is not a good 'baseline' to compare our results too, however, in the future a better baseline could be used to truly compare to our system. 

---Put your results and the baseline results in a table---

| Implementation                   | Precision | Recall |   F1  |
| -------------------------------- | --------- | ------ | ----- |
| T6 - 100% Entity Correct         |  0.269    | 0.253  | 0.260 |
| HeidelTime - 100% Entity Correct |  0.003    | 0.002  | 0.002 |
| -------------------------------- | --------- | ------ | ----- |
| T6 - Corrent Spans               |  0.606    | 0.522  | 0.561 |   
| HeidelTime - Correct Spans       |  0.013    | 0.007  | 0.009 |

---Explain your table---

Based on the results, our implementation was significantly better than our baseline.  However, this is to be expected given that there really was not another available program to perform our task the same way we implemented it.  As stated earlier in the future, we hope to develop a better comparison method to truly test our system.
