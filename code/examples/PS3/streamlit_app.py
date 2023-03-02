import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###

# Move this code into `load_data` function {{
# }}

# Changed to use st.cache_data based on https://docs.streamlit.io/library/api-reference/st.cache
@st.cache_data
def load_data():
    ## {{ CODE HERE }} ##
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
    id_vars=["Country", "Year", "Cancer", "Sex"],
    var_name="Age",
    value_name="Deaths",
    )

    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000
   
    return df


# Uncomment the next line when finished
df = load_data()

### P1.2 ###


st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
# https://docs.streamlit.io/library/api-reference/widgets/st.slider
# default step is 1 for int, so we don't need to specify it
year = st.slider("Year", min_value=int(df["Year"].min()), 
max_value=int(df["Year"].max()), value=2012)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
# https://docs.streamlit.io/library/api-reference/widgets/st.radio
# the demo shows "M" listed before "F" so we need to reverse the order
sex = st.radio("Sex", sorted(df['Sex'].unique(), reverse=True), index = 0)
subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# https://docs.streamlit.io/library/api-reference/widgets/st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries = [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
]
countries = st.multiselect("Countries", options=sorted(df["Country"].unique()), default=countries)
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
# https://docs.streamlit.io/library/api-reference/widgets/st.selectbox
# cancer = "Malignant neoplasm of stomach"
cancer = st.selectbox("Cancer", options=sorted(df["Cancer"].unique()), index = 0)
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

# Color scale: https://vega.github.io/vega/docs/schemes/
# Log transform scale: https://altair-viz.github.io/user_guide/transform/log.html
chart = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age:O", sort=ages),
    y=alt.Y("Country:N", sort=sorted(countries)),
    color=alt.Color("Rate:Q", scale=alt.Scale(scheme='blues', type='log', domain=(0.001, 100), clamp=True), 
    title="Mortality rate per 100k"),
    tooltip=["Rate"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)
### P2.5 ###


st.altair_chart(chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
