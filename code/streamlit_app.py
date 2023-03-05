import altair as alt
import pandas as pd
import streamlit as st
import numpy as np

#### Check to see if we need to do all of the data processing in a function like PS3

# Read in the data containing the risk factors for dementia
dementia_df = pd.read_csv("https://raw.githubusercontent.com/dmc747/bmi706_project/code/nhanes_dementia_risk_factors.csv')

# Create age categories: mid-life (45-64), and late-life (> 65yrs)
ages = [ (dementia_df['RIDAGEYR']<= 64), (dementia_df['RIDAGEYR'] >= 65)]
categories = ['mid_life', 'later_life']
# Use np.select to assign ages to categories 
dementia_df['Age'] = np.select(ages, categories)

# Output the list of risk factors 
riskfactors = dementia_df.columns[dementia_df.columns.str.contains('risk')] 

# Calculate total risk factors per person
dementia_df['Total risk factors'] = dementia_df[riskfactors].sum(axis=1)

# Create a list of total risk categories
riskcategory = [ (dementia_df['Total risk factors'] <= 1), 
                (dementia_df['Total risk factors'] > 1)  & (dementia_df['Total risk factors'] <= 3), 
                (dementia_df['Total risk factors'] > 3)]
riskname = ['less than 1', '2 and 3', 'greater than 3']
dementia_df['Total risk category'] = np.select(riskcategory,riskname)

# Rearrange the df with one risk factor column
dementia_df_new = pd.melt(
     dementia_df, id_vars=['SEQN','RIAGENDR','RIDRETH1', 'DMDEDUC2','WTMEC2YR', 'SDMVPSU','SDMVSTRA','year','Age','Total risk factors','Total risk category'], value_vars=riskfactors, var_name='Risk factor', value_name='Present'
)

# Change numeric codes to character for Streamlit selections

# 1. Sex
# Create the dictionary and add sex column
gender_dictionary ={1 : 'male', 2 : 'female'}
dementia_df_new['Sex'] = dementia_df_new['RIAGENDR'].map(gender_dictionary)
 
# 2. Ethnicity
eth_dictionary = {1: 'Mexican American', 2:'Other Hispanic', 3:'Non-Hispanic White', 4:'Non-Hispanic Black', 5: 'Other'}
dementia_df_new['Ethnicity'] = dementia_df_new['RIDRETH1'].map(eth_dictionary)
 
# 3. Education
edu_dictionary = {1 : '<9th grade', 2: '9th-11th grade', 
                  3 : 'high school diploma/GED/Equivalent', 4: 'some college or Associate’s degree', 
                  5 : 'college graduate or higher', 7: 'Refused', 9: 'Don’t know'}
    
dementia_df_new['Education'] = dementia_df_new['DMDEDUC2'].map(edu_dictionary)  

# Visualization Tasks
# 
# a)	Temporal trends in prevalence of dementia risk factors
# b)	Prevalence of dementia risk factors by sex
# c)	Prevalence of dementia risk factors by race-ethnicity
# d)	Prevalence of dementia risk factors in two age groups: midlife (45-64 years) and later life (>= 65 years)
# e)	Prevalence of 3 or more risk factors in midlife and later life adults

st.write("## Key dementia risk factors in different populations")

# Task 1: line chart: risk factor prevalence over time
# 1.1 prepare df and calculate prevalence
df1 = dementia_df_new.groupby(['year','Risk factor']).size().reset_index(name='population')
df1_1 = dementia_df_new.groupby(['year','Risk factor','Present']).size().reset_index(name='count')
df1_new = df1_1.merge(df1, on=['year', 'Risk factor'], how ='left')
df1_new['Prevalence'] = df1_new.query("Present==1")['count']/df1_new['population']*100
df1_new.dropna(inplace=True)

# 1.2 Generate line chart of prevalence for risk factors over time

# set multiselect menu
riskfactors = df1_new['Risk factor'].unique()
risks = st.multiselect(
    label="Risk factor",
    options=riskfactors,
    default=riskfactors,
)

subset = df1_new[df1_new["Risk factor"].isin(risks)]
risk_select1 = alt.selection_single(encodings=["y"])

base = alt.Chart(subset).mark_line(point=True).properties(
    width=600
).encode(
    x=alt.X('year:O',axis=alt.AxisConfig(labelAngle=0)),
    y='Prevalence:Q',
    color='Risk factor:N'
)

chart = base.add_selection(
    risk_select1
).transform_filter(
    risk_select1
).properties(title="Prevalence of dementia risk factors over time")


# add brush to link line chart and bar chart 
brush = alt.selection_interval( encodings=['x'])
upper = chart.transform_filter(
    brush
).mark_line(point=True)

lower = chart.mark_bar(
).add_selection(brush)

lower = lower.properties(
    height=150
)

chart1 = upper & lower
chart1

# Task 2: Prevalence of dementia risk factors by sex 

# 2.1 calculate prevalence by sex, risk factor, and year
df2 = dementia_df_new.groupby(['year','Sex','Risk factor']).size().reset_index(name='population')
df2_1 = dementia_df_new.groupby(['year','Risk factor','Sex','Present']).size().reset_index(name='count')
df2_new = df2_1.merge(df2, on=['year', 'Risk factor','Sex'], how ='left')
df2_new['Prevalence'] = df2_new.query("Present==1")['count']/df2_new['population']*100
df2_new.dropna(inplace=True)

# 2.2 Generate bar chart of prevalence of risk factors in males and females by year
# set year as slider
year_slider = alt.binding_range(
    min=df2_new["year"].min(),
    max=df2_new["year"].max(),
    step=2,
    name="Year",
)

selector = alt.selection_single(
    fields=["year"],
    bind=year_slider,
    init={"year": df2_new["year"].min()},
)

# Generate bar graphs for each sex; add year as selector 
bar = alt.Chart(df2_new).mark_bar().encode(
    x=alt.X("Prevalence:Q", title='Prevalence [%]'),
    y=alt.Y("Risk factor", sort="-x"), # ranked by prevalence values in males
    color='Sex:N',
    column='Sex:N',
    tooltip=[
        alt.Tooltip('Prevalence:Q', title="Prevalence (%)"),'Risk factor','Sex'],
).add_selection(
    selector
).transform_filter(
    selector
).properties(
    width=300,
    title='Prevalence of dementia risk factors in adult males and females'
)

bar

# Task 3: Prevalence of dementia risk factors by ethnicity by year

# 3.1 calculate prevalence by ethnicity, risk factor, and year
df3 = dementia_df_new.groupby(['year','Ethnicity','Risk factor']).size().reset_index(name='population')
df3_1 = dementia_df_new.groupby(['year','Risk factor','Ethnicity','Present']).size().reset_index(name='count')
df3_new = df3_1.merge(df3, on=['year', 'Risk factor','Ethnicity'], how ='left')
df3_new['Prevalence'] = df3_new.query("Present==1")['count']/df3_new['population']*100
df3_new.dropna(inplace=True)

# 3.2 Generate bar chart of prevalences of risk factors in each ethnicity by year
# add year as slider
year_slider = alt.binding_range(
    min=df3_new["year"].min(),
    max=df3_new["year"].max(),
    step=2,
    name="Year",
)

selector_year = alt.selection_single(
    fields=["year"],
    bind=year_slider,
    init={"year": df3_new["year"].min()},
)

# Generate bar graphs in each ethnicity; add year as selector 
bar_ethnicity = alt.Chart(df3_new).mark_bar().encode(
    x=alt.X("Prevalence:Q", title='Prevalence [%]'),
    y=alt.Y("Risk factor", sort="-x"), 
    color='Ethnicity:N',
    column='Ethnicity:N',
    tooltip=[
        alt.Tooltip('Prevalence:Q', title="Prevalence (%)"),'Risk factor'],
).add_selection(
    selector_year
).transform_filter(
    selector_year
).properties(
    width=125,
    title='Prevalence of dementia risk factors by ethnicity'
)

bar_ethnicity

# Task 4: Prevalence of dementia risk factors by age group (mid-life and later life) by year 

# 4.1 calculate prevalence by Age group, risk factor, and year
df4 = dementia_df_new.groupby(['year','Age','Risk factor']).size().reset_index(name='population')
df4_1 = dementia_df_new.groupby(['year','Risk factor','Age','Present']).size().reset_index(name='count')
df4_new = df4_1.merge(df4, on=['year', 'Risk factor','Age'], how ='left')
df4_new['Prevalence'] = df4_new.query("Present==1")['count']/df4_new['population']*100
df4_new.dropna(inplace=True)

# 4.2 Generate bar chart of prevalences of risk factors in each ethnicity by year
# set year as slider
slider4 = alt.binding_range(
    min=df4_new["year"].min(),
    max=df4_new["year"].max(),
    step=2,
    name="Year",
)

selector4 = alt.selection_single(
    fields=["year"],
    bind=slider4,
    init={"year": df4_new["year"].min()},
)


# Generate bar graphs in each ethnicity; add year as selector 
bar_age = alt.Chart(df4_new).mark_bar().encode(
    x=alt.X("Prevalence:Q", title='Prevalence [%]'),
    y=alt.Y("Risk factor", sort="-x"), 
    color='Age:N',
    column='Age:N',
    tooltip=[
        alt.Tooltip('Prevalence:Q', title="Prevalence (%)"),'Risk factor'],
).add_selection(
    selector4
).transform_filter(
    selector4
).properties(
    width=350,
    title='Prevalence of dementia risk factors in mid-life and later-life adults'
)

bar_age

# Task 5: Prevalence of dementia risk factors by education by year 

# 5.1 calculate prevalence in each combination of education, risk factor, and year
df5 = dementia_df_new.groupby(['year','Education','Risk factor']).size().reset_index(name='population')
df5_1 = dementia_df_new.groupby(['year','Risk factor','Education','Present']).size().reset_index(name='count')
df5_new = df5_1.merge(df5, on=['year', 'Risk factor','Education'], how ='left')
df5_new['Prevalence'] = df5_new.query("Present==1")['count']/df5_new['population']*100
# data cleanup
# drop rows with NaN 
df5_new.dropna(inplace=True) 
# remove education categories that are not informative
df5_new = df5_new[df5_new.Education.isin(["Don’t know", "Refused"]) == False]

#5.2 Generate bar chart of prevalences of risk factors in education group by year
# set year as slider
slider5 = alt.binding_range(
    min=df5_new["year"].min(),
    max=df5_new["year"].max(),
    step=2,
    name="Year",
)

selector5 = alt.selection_single(
    fields=["year"],
    bind=slider5,
    init={"year": df5_new["year"].min()},
)


# generate bar graphs in each ethnicity; add year as selector 
bar_edu = alt.Chart(df5_new).mark_bar().encode(
    x=alt.X("Prevalence:Q", title='Prevalence [%]'),
    y=alt.Y("Risk factor", sort="-x"), 
    color=alt.Color('Education:N',sort=['<9th grade', 
                            '9th-11th grade', 
                            'high school diploma/GED/Equivalent', 
                            'some college or Associate’s degree', 
                            'college graduate or higher']),
    column=alt.Column('Education:N',
                      sort=['<9th grade', 
                            '9th-11th grade', 
                            'high school diploma/GED/Equivalent', 
                            'some college or Associate’s degree', 
                            'college graduate or higher']), # order columns by education level
    tooltip=[
        alt.Tooltip('Prevalence:Q', title="Prevalence (%)"),'Risk factor'],
).add_selection(
    selector5
).transform_filter(
    selector5
).properties(
    width=120,
    title='Prevalence of dementia risk factors by education'
)

bar_edu

# Task 6: Prevalence of multiple risk factors in mid-life and later-life adults by year 

# 6.1 calculate prevalence in each combination of multiple risk factor, age group, and year
df6 = dementia_df_new.groupby(['year','Age']).size().reset_index(name='population')
df6_1 = dementia_df_new.groupby(['year','Age','Total risk category']).size().reset_index(name='count')
df6_new = df6_1.merge(df6, on=['year', 'Age'], how ='left')
df6_new['Prevalence'] = df6_new['count']/df6_new['population']*100
df6_new.dropna(inplace=True) 

#6.2 Generate donut chart of prevalences of multiple risk factors in age group by year
# set year as slider
slider6 = alt.binding_range(
    min=df6_new["year"].min(),
    max=df6_new["year"].max(),
    step=2,
    name="Year",
)

selector6 = alt.selection_single(
    fields=["year"],
    bind=slider6,
    init={"year": df6_new["year"].min()},
)

# generate donut chart of multiple risk factor by age group; add year as selector 
donut_risk = alt.Chart(df6_new).mark_arc(innerRadius=50, outerRadius=90).encode(
    theta=alt.Theta(field="Prevalence",aggregate='sum', type="quantitative"),
    color=alt.Color(field="Total risk category", type="nominal", 
                   scale=alt.Scale(domain=['less than 1', '2 and 3', 'greater than 3'], 
                                   range=['green','gray','red'])), # set the highest risk category as red 
    column='Age:N',
    tooltip=['Prevalence:Q', 'Total risk category:N']
).add_selection(
    selector6
).transform_filter(
    selector6
).properties(
    width=300,
    title = 'Prevalence of multiple risk factors in mid-life and later-life adults'
)

donut_risk



