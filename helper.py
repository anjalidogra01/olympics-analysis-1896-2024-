import numpy as np
import plotly.express as px
###########    Medal Tally     #############
def medal_tally(df):
    medal_tally= df.drop_duplicates(subset=['Team', 'NOC', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    medal_tally=medal_tally.groupby('NOC').sum()[['Gold','Silver','Bronze']].sort_values('Gold',ascending=False).reset_index()
    medal_tally['Total'] = medal_tally['Gold']+medal_tally['Silver']+medal_tally['Bronze']
    return medal_tally


def country_year_list(df):
    years=df['Year'].unique().tolist()
    years.sort()
    years.insert(0,'Overall')


    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')
    
    return years, country

def fetch_medal_tally(df,year,country):
    medal_df= df.drop_duplicates(subset=['Team', 'NOC', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag =0
    if year =='Overall' and country =='Overall':
        temp_df = medal_df
    if year =='Overall' and country !='Overall': 
        flag=1
        temp_df =medal_df[medal_df['region']==country]
    if year !='Overall' and country =='Overall': 
        temp_df =medal_df[medal_df['Year']==int(year)]
    if year !='Overall' and country !='Overall': 
        temp_df =medal_df[(medal_df['Year']==int(year)) & (medal_df['region']==country) ] 
    if flag == 1:
        x =   temp_df.groupby('Year').sum()[['Gold','Silver','Bronze']].sort_values('Year').reset_index()  
    else:
        x =   temp_df.groupby('region').sum()[['Gold','Silver','Bronze']].sort_values('Gold',ascending=False).reset_index()  
    
    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x

###########    Overall Analysis    #############
def data_over_time(df,col):
    data_over_time = (
        df.drop_duplicates(['Year',col])
          .groupby('Year')[col]
          .count()
          .reset_index()
          .sort_values('Year')
    )
    data_over_time.rename(columns={'Year': 'Edition',col: f'No. of {col}'}, inplace=True)
    return data_over_time

def top_medalists(df, sport, top_n=10):

    if sport.lower() == 'overall':
        result = (
            df.groupby(['Name', 'Sport'], as_index=False)
              .agg({
                  'Gold': 'sum',
                  'Silver': 'sum',
                  'Bronze': 'sum',
                  'Total': 'sum'
              })
              .sort_values(
                  by=['Total', 'Gold', 'Silver', 'Bronze'],
                  ascending=False
              )
              .head(top_n)
        )

    else:
        result = (
            df[df['Sport'].str.lower() == sport.lower()]
              .groupby(['Name', 'Sport'], as_index=False)
              .agg({
                  'Gold': 'sum',
                  'Silver': 'sum',
                  'Bronze': 'sum',
                  'Total': 'sum'
              })
              .sort_values(
                  by=['Total', 'Gold', 'Silver', 'Bronze'],
                  ascending=False
              )
              .head(top_n)
        )

    return result


def yearwise_medal_tally(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team','NOC','Year','City','Sport','Event','Medal'],inplace=True)

    new_df = temp_df[temp_df['region']==country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df
###########   Countrywise Analysis     #############
def country_event_heatmap(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team','NOC','Year','City','Sport','Event','Medal'],inplace=True)

    new_df = temp_df[temp_df['region']==country]
    pt = new_df.pivot_table(index='Sport',columns='Year',values='Medal',aggfunc='count').fillna(0)
    return pt


def countrywise_top_medalists(df, country, top_n=10):

    temp_df = df[df['region'] == country]

    result = (
        temp_df
        .groupby(['Name', 'Sport'], as_index=False)[
            ['Gold', 'Silver', 'Bronze', 'Total']
        ]
        .sum()
        .sort_values(
            by=['Total', 'Gold', 'Silver', 'Bronze'],
            ascending=[False, False, False, False]
        )
        .head(top_n)
    )

    return result
###########    Sportwise Analysis     #############
def sport_medal_trend(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    temp_df = temp_df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    trend_df = (temp_df.groupby('Year').count()['Medal'].reset_index())

    return trend_df

def sport_country_dominance(df, sport, top_n=10):
    temp_df = df.dropna(subset=['Medal'])

    temp_df = temp_df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Medal'])
    if sport !='Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    result = (
        temp_df.groupby('region', as_index=False).count()[['region', 'Medal']].sort_values(by='Medal', ascending=False).head(top_n))

    return result

def most_competitive_sports(df, top_n=10):
    temp_df = df.dropna(subset=['Medal'])

    temp_df = temp_df.drop_duplicates(
        subset=['Year', 'Sport', 'Event', 'Medal']
    )

    result = (
        temp_df
        .groupby('Sport')['region']
        .nunique()
        .reset_index(name='No_of_Countries')
        .sort_values(by='No_of_Countries', ascending=False)
        .head(top_n)
    )

    return result

###########    Gender Analysis     #############
def gender_participation(df):
    temp_df = df.drop_duplicates(['Name', 'Sex', 'Year'])

    result = (temp_df.groupby(['Year', 'Sex'])['Name'].count().reset_index(name='Athletes'))

    return result

def gender_medal_distribution(df):
    temp_df = df.dropna(subset=['Medal'])
    temp = temp.drop_duplicates(
        subset=['Team','NOC','Year','Sport','Event','Medal'])
    result = (
    temp_df.groupby('Sex')['Medal'].count().reset_index(name='Medals'))

    return result

def top_female_sports(df, top_n=10):
    temp_df = df[df['Sex'] == 'F']

    temp_df = temp_df.drop_duplicates(['Name', 'Sport', 'Year'])

    result = (temp_df
        .groupby('Sport')['Name']
        .count()
        .reset_index(name='Female_Athletes')
        .sort_values(by='Female_Athletes', ascending=False)
        .head(top_n)
    )

    return result
