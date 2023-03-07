*************************************************************************;
* create_dementia_risk_indicators.sas                          			*;
*************************************************************************;
options nocenter nodate nonumber pagesize=max linesize=150;

* Location of SAS data sets ;
libname nhanes 'd:\nhanes\data' ;

* Read in combined NHANES data ;
data analysis ;
	set nhanes.nhanes_combined ;

	/* The depression inventory for 1999-2003 was only given to peopl ages 20-39,
	   so let's drop the variable since all values are missing for our sample.
	*/
	drop ciddscor ;

	* Set don't know and refused to missing ;
	if alq130 in (777,999) then alq130 = . ;

	* Hearing ;
	array _auq auq:;
	do over _auq;
		if (_auq >= 7) then call missing(_auq);
	end ;

	* Diabetes self-report ;
	array _diq diq:;
	do over _diq;
		if (_diq >= 7) then call missing(_diq);
	end ;
	* Recode "borderline" responses as "No" ;
	if (diq010 eq 3) then diq010 = 2 ;

	* PHQ-9 depression items ;
	array _dpq dpq:;
	do over _dpq;
		if (_dpq >= 7) then call missing(_dpq);
	end;

	* Smoking ;
	array _smq smq:;
	do over _smq;
		if (_smq >= 7) then call missing(_smq);
	end;

	* Social support ;
	array _ssq ssq:;
	do over _ssq;
		if (_ssq >= 7) then call missing(_ssq);
	end;
	* Recode 3=don't need help to 1=Yes ;
	if ssq010 eq 3 then ssq010 = 1 ;	* 1999 used ssq010 ;
	if ssq011 eq 3 then ssq011 = 1 ;	* 2001-2007 used ssq011 ;

	* Physical activity ;
	if (pad320 >= 7) then pad320 = .;
	* Recode 3=unable to do activity as 2=No ;
	if pad320 eq 3 then pad320 = 2 ;
	if pad675 ge 7777 then pad675 = . ;
run ;
data risk_factors ;
	set analysis ;
	* 14+ alcohol drinks per week = "excess" alcohol use ;
	if alq130 ge 14 then alcohol_risk = 1 ;
	else if (0 le alq130 lt 14) then alcohol_risk = 0 ;

	* hearing impairment ;
	if (auq130 ge 3) or (auq131 ge 4) or (auq054 ge 4) then hearing_risk = 1 ;
	else if (auq130 in(1, 2)) or (auq131 in(1, 2, 3)) or (auq054 in(1, 2,3)) then hearing_risk = 0 ;

	* blood pressure ;
	* 2005-2017 omitted average bp, so we have to calculate it first ;
	bpxsar = mean(bpxsy1, bpxsy2, bpxsy3, bpxsy4) ;
	bxpdar = mean(bpxdi1, bpxdi2, bpxdi3, bpxdi4) ;
	if bpxsar gt 130 then bp_risk = 1 ;
	else if (0 le bpxsar le 130) then bp_risk = 0 ;

	* diabetes (self-report or lab) ;
	if (diq010 eq 1) or (lbxglu ge 126) then diabetes_risk = 1 ;
	else if (diq010 eq 2) or (0 le lbxglu lt 126) then diabetes_risk = 0 ;

	* depression ;
  	depression_score = dpq010+dpq020+dpq030+dpq040+dpq050+dpq060+dpq070+dpq080+dpq090;
	if (depression_score ge 10) then depression_risk = 1 ;
	else if (0 le depression_score lt 10) then depression_risk = 0 ;

	* smoking ;
	if (smq020 eq 1) then smoking_risk = 1 ;
	else if (smq020 eq 2) then smoking_risk = 0 ;

	* social support ;
	if (ssq010 eq 1) or (ssq011 eq 1) then social_risk = 0 ;
	else if (ssq010 eq 2) or (ssq011 eq 2) then social_risk = 1 ;

	* obesity ;
	if (bmxbmi ge 30) then obesity_risk = 1 ;
	else if (0 le bmxbmi lt 30) then obesity_risk = 0 ;

	* physical inactivity ;
	if (pad320 eq 2) or (0 le pad675 lt 150) then sedentary_risk = 1 ;
	else if (pad320 eq 1) or (pad675 ge 150) then sedentary_risk = 0 ;
run ;
proc freq data = risk_factors ;
	tables alq130*alcohol_risk / list missing ;
	tables auq130*auq131*auq054*hearing_risk / list missing ;
	tables bpxsar*bp_risk / list missing ;
	tables diq010*lbxglu*diabetes_risk / list missing ;
	tables depression_score*depression_risk / list missing ;
	tables smq020*smoking_risk / list missing ;
	tables ssq010*ssq011*social_risk / list missing ;
	tables bmxbmi*obesity_risk / list missing ;
	tables pad320*pad675*sedentary_risk / list missing ;
run ;
data nhanes.risk_factors ;
	set risk_factors ;
	keep seqn--year alcohol_risk hearing_risk bp_risk diabetes_risk depression_risk
	smoking_risk social_risk obesity_risk sedentary_risk ;
run ;
* Export to CSV file ;
proc export data = nhanes.risk_factors
    outfile = "D:\NHANES\Data\nhanes_dementia_risk_factors.csv"
    dbms = csv
    replace ;
run ;
* Calculate descriptive statistics (with and without missing values) ;
ods pdf file='D:\NHANES\Output\nhanes_descriptives.pdf' ;
proc univariate plot data = nhanes.risk_factors ;
	var ridageyr ;
run ;
proc freq data = nhanes.risk_factors ;
	tables riagendr ridreth1 dmdeduc2 year alcohol_risk bp_risk diabetes_risk
	depression_risk smoking_risk social_risk obesity_risk sedentary_risk ;
	title1 'Frequencies of demographic characteristics and risk factors' ;
	title2 'Excluding missing from totals' ;
run ;
proc freq data = nhanes.risk_factors ;
	tables riagendr ridreth1 dmdeduc2 year alcohol_risk bp_risk diabetes_risk
	depression_risk smoking_risk social_risk obesity_risk sedentary_risk / missing ;
	title1 'Frequencies of demographic characteristics and risk factors' ;
	title2 'Including missing in totals' ;
run ;
ods pdf close ;




