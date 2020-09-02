# Determination of Ventilatory/Gas Exchange Threshold from a cardiopulmonary exercise test

The Gas Exchange Threshold (GET), also called as Lactate Threshold (LT), Ventilatory threshold (VT), and Anaerobic Threshold (AT) is used as an effective indicator of physical fitness in patients suffering from cardiovascular disease and healthy people including athletes [1]. The GET may be a better indicator of aerobic fitness than the peak oxygen uptake (VO2peak) [2]. The GET is the point at which lactate begins to accumulate in the blood [3]. Hence, any delay in the accumulation of blood lactate that can be attributed to an intervention (medical- drug or surgical, exercise, etc.) may yield a better understanding into the effectiveness of the intervention [3]. Therefore, medical practitioners, coaches, athletes, and researchers can gain insights by determining the GET before and after their interventions. The most widely used method to determine the GET non-invasively was proposed by Beaver and colleagues [1]. The method comprises of fitting curves to the VCO<sub>2</sub> vs VO<sub>2</sub> plots from a cardiopulmonary exercise test to determine the GET point. This process of curve fitting can be automated using Python. 

## What are VO<sub>2</sub>, VCO<sub>2</sub>, and GET?
For a layperson, these terms can be defined as follows:
VO<sub>2</sub> is volume of Oxygen inhaled per minute during exercise usually expressed as ml/min (milli-litre per minute)
VCO<sub>2</sub> is the volume of Carbon dioxide exhaled per minute during exercise, ml/min.
GET is the point during the exercise at which there is a change in the ratio of VCO<sub>2</sub>/VO<sub>2</sub>. It can be loosely understood as the point at which the muscles start transitioning into anaerobic respiration from aerobic respiration. For a more technical explanation of these terms read the article by Mezzani [4].

## What is a cardiopulmonary exercise test?
The Cardiopulmonary Exercise Test (CPET) involves the measurement of VO<sub>2</sub> and VCO<sub>2</sub> while a participant exercises at progressively increasing intensities. For example, a cyclist will pedal on an exercise bicycle where the resistance is incrementally increasing. Similarly, a runner will run on a treadmill where the speed is incrementally increasing. Hence, this test is also called the graded exercise test or GXT. A schematic of the GXT is shown below where the test starts with a warmup, after which, the intensity increases incrementally. The athlete exercises till they are no longer able to continue. The test is terminated and the athlete exercises at a very low intensity to cool down.

<div align="center">
   <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure1.png" width=500 alt="centered image" />
</div>

A picture of the CPET being conducted on a cyclist is shown below, where the cyclist is on his bicycle which is mounted on a bicycle ergometer. The cyclist is made to wear a mask which comprises of tubes that measure the VO<sub>2</sub> and VCO<sub>2</sub> when he inhales and exhales during the test respectively.

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure2.png" width=400 alt="centered image" />
</div>

The CPET apparatus outputs measured values of time elapsed, breath-by-breath data of VO<sub>2</sub>, VCO<sub>2</sub>, and a few other parameters. Due to the noise in the data, all the outputs are saved as 10 second averages. A plot of VCO<sub>2</sub> against VO<sub>2</sub> looks like the following:

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure3.png" width=400 alt="centered image" />
</div>
 
## Beaver and colleagues’ [1] method of determining the GET:
Beaver and colleagues’ [1] called GET as Anaerobic threshold (AT). They proposed that the GET can be determined by the following method:
Step 1: A tentative GET is chosen, and the data is divided into two regions. Each regions is fit with a separate linear regressions.

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure4.png" width=400 alt="centered image" />
</div>
 
Step 2: A new linear regression (LRN) is fit to the entire data. 
 
<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure5.png" width=400 alt="centered image" />
</div>

Step 3: The tentative GET point is then systematically moved until the ratio of the distance between LRN and the GET point to the mean square error of regression of the LRN is maximised (i.e. d/MSE<sub>LRN</sub> is maximised).

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure6.png" width=400 alt="centered image" />
</div>
 
Step 4: The data is separated into two regions using the new GET point and two new linear regressions are fit to them. This new GET is accepted if the change in slope between the lower and upper segments is >0.1.

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure7.png" width=400 alt="centered image" />
</div>

This difference in slopes condition is rarely violated. In which case, a neighbouring point is chosen and Step 4 is repeated till the condition is satisfied.
The most important aspects in this method are:
  * Ensuring that the ratio of the distance between the tentative GET point and the LRN and the LRN’s mean square error is maximise, and
  * The difference in slopes between the upper and lower segments should be >0.1.

## Minor modifications to the method to enable automatic determination of GET
To accomplish the first task, the distance between the LRN and the tentative GET point needs to be maximised. Instead of choosing a tentative GET point, which is subjective, we can find the point of maximum perpendicular distance from the LRN. The mean square error of the LRN is a constant, hence maximising the perpendicular distance will lead to the ratio being maximised. After finding this point of maximum perpendicular distance (PDmax), the entire data can be divided into two regions: lower segment (points before the PDmax) and upper segment (points after the PDmax). The slopes of the two regressions can then be compared to satisfy the second condition. These steps are described below:
 
Step 1: A linear regression and a quadratic regression are fit to the entire data.

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure8.png" width=400 alt="centered image" />
</div>
 
Step 2: The point of maximum perpendicular distance, PD<sub>max</sub> is determined by differentiating the quadratic curve and equating it to the slope of the linear regression. PD<sub>max</sub> would be the point at which the tangent to the curve is parallel to the linear regression.
 	 
<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure9.png" width=700 alt="centered image" />
</div>
 
Step 3: The data is separated into two regions using PDmax and each region is fit with a separate linear regression. This PD<sub>max</sub> is accepted as GET if the change in slope between the lower and upper segments is >0.1.

<div align="center">
    <img src="https://github.com/vj-sarthy/get_GET/blob/master/Figure10.png" width=400 alt="centered image" />
</div>
 
If the difference in slopes in <0.1, a neighbouring point should be chosen, and Step 3 should be repeated. However, the difference in slopes is rarely <0.1 after Step 3.
## The python program
From the CPET software, the data is saved as 10 seconds averages in an excel file. The data is further processed as by clipping the warmup and cool down data and extracting the columns related to time, VO<sub>2</sub>, and VCO<sub>2</sub>. The python program reads this pre-processed data from the excel file and outputs the GET value, its timestamp, and the corresponding difference in slopes. Additionally, the program outputs visualisations similar to the one shown in the previous section. The program outputs a visualisation with two linear regressions (lower and upper) which guides researchers better in determining the GET point, and its corresponding exercise intensity. Furthermore, multiple files can be analysed at the same time by disabling the plot function.

In summary, the python program reduces the subjectivity involved in determining the GET by removing the need for an initial guess. It provides a faster way to analyse the data from a CPET to determine the GET point, and its timestamp by allowing multiple files (multiple participant date) to be analysed parallelly.

## References:
1. W. L. Beaver, K. Wasserman, and B. J. Whipp, “A new method for detecting anaerobic threshold by gas exchange,” J. Appl. Physiol., vol. 60, no. 6, pp. 2020–2027, 1986.
2. S. E. Gaskill, B. C. Ruby, A. J. Walker, O. A. Sanchez, R. C. Serfass, and A. S. Leon, “Validity and reliability of combining three methods to determine ventilatory threshold,” Med. Sci. Sports Exerc., vol. 33, no. 11, pp. 1841–1848, 2001.
3. J. Myers and E. Ashley, “Dangerous curves: A perspective on exercise, lactate, and the anaerobic threshold,” Chest, vol. 111, no. 3, pp. 787–795, 1997.
4. A. Mezzani, “Cardiopulmonary exercise testing: Basics of methodology and measurements,” Ann. Am. Thorac. Soc., vol. 14, pp. S3–S11, 2017.
