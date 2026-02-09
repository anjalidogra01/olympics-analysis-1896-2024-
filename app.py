import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Olympics Analysis(1896-2024)",
    page_icon="🏅",
    layout="wide"
)

# ---------------- DATA LOADING ----------------
df = pd.read_csv('olympics_dataset.csv')
region_df = pd.read_csv('noc_regions.csv')

# ---------------- SPORT NORMALIZATION ----------------
mapping = {
    'Artistic Gymnastics': 'Gymnastics',
    'Rhythmic Gymnastics': 'Gymnastics',
    'Trampoline Gymnastics': 'Gymnastics',
    'Cycling Road': 'Cycling',
    'Cycling Track': 'Cycling',
    'Cycling BMX Racing': 'Cycling',
    'Cycling BMX Freestyle': 'Cycling',
    'Cycling Mountain Bike': 'Cycling',
    'Marathon Swimming': 'Swimming',
    'Artistic Swimming': 'Swimming',
    '3x3 Basketball': 'Basketball',
    'Baseball/Softball': 'Baseball/Softball'
}

df['Sport'] = df['Sport'].replace(mapping)
df['Sport'] = df['Sport'].astype(str).str.split(',')
df = df.explode('Sport')
df['Sport'] = df['Sport'].str.strip()
df.reset_index(drop=True, inplace=True)

# ---------------- PREPROCESS ----------------
df = preprocessor.preprocess(df, region_df)

# ---------------- SIDEBAR ----------------
st.sidebar.image('https://colorlib.com/wp/wp-content/uploads/sites/2/olympic-logo-2024.png')
st.sidebar.markdown(
    """
    ## 🏅 Olympics Dashboard  
    **1896 – 2024**
    ---
    """
)

options = st.sidebar.radio(
    "Navigate",
    (
        '🏅 Medal Tally',
        '📊 Overall Analysis',
        '🌍 Country-wise Analysis',
        '🏆 Sport-wise Analysis',
        '👩‍🦰 Gender Analysis',
    )
)

# ================= MEDAL TALLY =================
if options == '🏅 Medal Tally':
    st.title("🏅 Medal Tally")
    st.markdown("---")

    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.subheader("Overall Medal Tally")
    elif selected_year == 'Overall':
        st.subheader(f"{selected_country} Overall Performance")
    elif selected_country == 'Overall':
        st.subheader(f"Medal Tally in {selected_year} Olympics")
    else:
        st.subheader(f"{selected_country} in {selected_year} Olympics")

    st.dataframe(medal_tally, use_container_width=True, hide_index=True)

# ================= OVERALL ANALYSIS =================
if options == '📊 Overall Analysis':
    st.title("📊 Overall Analysis")
    st.markdown("---")

    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏟 Editions", editions)
    col2.metric("🌍 Hosts", cities)
    col3.metric("🏅 Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Events", events)
    col2.metric("🏳 Nations", nations)
    col3.metric("👤 Athletes", athletes)

    st.markdown("### 🌍 Participation Over Time")

    nations_over_time = helper.data_over_time(df, "region")
    fig = px.line(nations_over_time, x='Edition', y='No. of region', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    events_over_time = helper.data_over_time(df, "Event")
    fig = px.line(events_over_time, x='Edition', y='No. of Event', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    athletes_over_time = helper.data_over_time(df, "Name")
    fig = px.line(athletes_over_time, x='Edition', y='No. of Name', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧊 Sports vs Events Heatmap")

    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    pivot_df = x.pivot_table(
        index='Sport',
        columns='Year',
        values='Event',
        aggfunc='count'
    ).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(18, 12))
    sns.heatmap(pivot_df, cmap="YlOrRd", linewidths=0.5, annot=False)
    st.pyplot(fig)

    st.markdown("### 🏆 Most Successful Athletes")

    sport_list = sorted(df['Sport'].unique().tolist())
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select Sport", sport_list)

    top_athletes = helper.top_medalists(df, selected_sport, top_n=15)
    st.dataframe(top_athletes, use_container_width=True, hide_index=True)

# ================= COUNTRY-WISE ANALYSIS =================
if options == '🌍 Country-wise Analysis':
    st.title("🌍 Country-wise Analysis")
    st.markdown("---")

    country_list = sorted(df['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country", country_list)

    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x='Year', y='Medal', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧊 Sport Dominance Heatmap")

    pt = helper.country_event_heatmap(df, selected_country)
    if pt.empty:
        st.info("ℹ️ No data available for selected filters")
    else:
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.heatmap(pt, cmap="Blues", linewidths=0.5)
        st.pyplot(fig)

    st.markdown("### 🏅 Top 10 Athletes")

    top10_df = helper.countrywise_top_medalists(df, selected_country, top_n=10)
    st.dataframe(top10_df, use_container_width=True, hide_index=True)

# ================= SPORT-WISE ANALYSIS =================
if options == '🏆 Sport-wise Analysis':
    st.title("🏆 Sport-wise Analysis")
    st.markdown("---")

    sport_list = sorted(df['Sport'].unique().tolist())
    sport_list.insert(0, 'Overall')
    selected_sport = st.sidebar.selectbox("Select Sport", sport_list)

    trend_df = helper.sport_medal_trend(df, selected_sport)
    fig = px.line(trend_df, x='Year', y='Medal', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🌍 Country Dominance")

    country_df = helper.sport_country_dominance(df, selected_sport)
    fig = px.bar(country_df, x='region', y='Medal', text='Medal')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔥 Most Competitive Sports")

    comp_df = helper.most_competitive_sports(df, top_n=10)
    fig = px.bar(comp_df, x='Sport', y='No_of_Countries', text='No_of_Countries')
    st.plotly_chart(fig, use_container_width=True)

# ================= GENDER ANALYSIS =================
if options == '👩‍🦰 Gender Analysis':
    st.title("👩‍🦰 Gender Analysis")
    st.markdown("---")

    st.markdown("### 📈 Participation Trend")

    gender_df = helper.gender_participation(df)
    fig = px.line(gender_df, x='Year', y='Athletes', color='Sex', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏅 Medal Distribution")

    medal_gender_df = helper.gender_medal_distribution(df)
    fig = px.pie(medal_gender_df, names='Sex', values='Medals', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔥 Female Dominated Sports")

    female_sport_df = helper.top_female_sports(df)
    fig = px.bar(female_sport_df, x='Sport', y='Female_Athletes', text='Female_Athletes')
    st.plotly_chart(fig, use_container_width=True)
