# setup_script.py

# just a bunch of random functions, etc. to pull new data, load it, and format
# it; collected here to avoid clutter in the jupyter notebook

import os
import time

import numpy as np
import pandas as pd


def getNewData(base='https://coviddata.github.io/covid-api/v1'):
    # data aggregation levels
    levels = ['countries', 'regions', 'places']
    reports = ['cases.csv', 'recoveries.csv', 'deaths.csv']

    # saving in data folder
    for level in levels:
        for report in reports:
            os.system(f'wget {base}/{level}/{report}')
            os.system(f'mv {report} data/{level}')
            time.sleep(1)

    return None


def reformat(dfs, k=4, jhu=True):
    """Reformats column names, sends dates to datetime, drops unnecessary rows."""
    for i in range(len(dfs)):
        df = dfs[i].copy()

        # rename non date columns
        rename = {'Province/State': 'state', 'Country/Region': 'country', 'Lat': 'lat', 'Long': 'long'}
        df.rename(columns=rename, inplace=True)
        # get rid of this weird 'Recovered' state...what even is that...
        dfs[i] = df[df.state != 'Recovered'].copy()

        # rename date columns
        rename = {date: pd.to_datetime(date) for date in df.columns.values[k:]}
        df.rename(columns=rename, inplace=True)

    return dfs


def loadAPIData(level):
    """Load the data aggregated by ``level`` from API source"""
    sortby = {'countries': 'Country', 'regions': 'Region', 'places': 'Place'}

    confirmed = pd.read_csv(f'data/{level}/cases.csv')\
                  .sort_values(by=sortby[level])\
                  .set_index(sortby[level])

    deaths = pd.read_csv(f'data/{level}/deaths.csv')\
               .sort_values(by=sortby[level])\
               .set_index(sortby[level])

    recoveries = pd.read_csv(f'data/{level}/recoveries.csv')\
                   .sort_values(by=sortby[level])\
                   .set_index(sortby[level])


    # drop weird index stuff
    try:
        confirmed.drop('Recovered', inplace=True)
    except:
        pass

    try:
        deaths.drop('Recovered', inplace=True)
    except:
        pass

    try:
        recoveries.drop('Recovered', inplace=True)
    except:
        pass

    # construct active cases df
    ind = {'countries': 0, 'regions': 1, 'places': 2}

    case_data = confirmed.values[:, ind[level]:]
    death_data = deaths.values[:, ind[level]:]
    recov_data = recoveries.values[:, ind[level]:]

    active_data = case_data - death_data - recov_data

    active = confirmed.copy()
    active.iloc[:, ind[level]:] = active_data

    # sort by active cases today
    active.sort_values(by=active.columns[-1], ascending=False, inplace=True)

    # sort inds
    inds = active.index
    confirmed = confirmed.loc[inds].copy()
    deaths = deaths.loc[inds].copy()
    recoveries = recoveries.loc[inds].copy()

    return active, confirmed, deaths, recoveries

def stackedDataFrame(a, c, d, r):
    """makes a big stacked dataframe of all the stuff for plotly"""
    countries = c.index.values.tolist()
    dfs = []

    conf_temp = c.T.copy()
    conf_temp['Date'] = conf_temp.index.values

    rec_temp = r.T.copy()
    rec_temp['Date'] = rec_temp.index.values

    death_temp = d.T.copy()
    death_temp['Date'] = death_temp.index.values

    act_temp = a.T.copy()
    act_temp['Date'] = act_temp.index.values

    for country in countries:
        ctemp = conf_temp[[country, 'Date']].copy()
        ctemp['Country'] = country
        ctemp['Kind'] = 'Confirmed'

        rtemp = rec_temp[[country, 'Date']].copy()
        rtemp['Country'] = country
        rtemp['Kind'] = 'Recovered'

        dtemp = death_temp[[country, 'Date']].copy()
        dtemp['Country'] = country
        dtemp['Kind'] = 'Deaths'

        atemp = act_temp[[country, 'Date']].copy()
        atemp['Country'] = country
        atemp['Kind'] = 'Active'

        # atemp = ctemp.copy()
        # atemp[country] = atemp[country].values - rtemp[country].values - dtemp[country].values
        # atemp['Kind'] = 'Active'

        dfs.append(ctemp.values)
        dfs.append(rtemp.values)
        dfs.append(dtemp.values)
        dfs.append(atemp.values)

    out = pd.DataFrame(np.concatenate(dfs), columns=['Count', 'Date', 'Country', 'Kind'])
    out['Date'] = pd.to_datetime(out['Date'])

    return out




    ############## Some other stuff that is currently useless ##############

def dropUSCounties(df):
    """Drops US County data (it's empty, so I don't know why it's included...)"""
    rm_comma = np.vectorize(lambda x: x==x.replace(',', ''))
    non_counties = np.vectorize(lambda x: x not in ['Virgin Islands, U.S.', 'Washington, D.C.'])
    temp = df[pd.isna(df.state) == False]
    return temp[(rm_comma(temp.state)) & ((temp.state != 'Virgin Islands, U.S.') | (temp.state != 'New Castle, DE'))]


def byCountry(df):
    # filter down to countries
    pass

# list of US states
state_names = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
               "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
               "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
               "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

# function for pulling out states
isState = np.vectorize(lambda x: x in state_names)
