import requests
import csv
import pandas

def pullData(BASE='http://blog.lazd.net/coronadatascraper/', ext='./timeseries.csv'):
    """Pulls csv data from given url and formats it as pandas DataFrame"""
    # pull data and decode as utf-8
    data = requests.get(url + ext).content.decode('utf-8')
    # convert to list of values
    data = list(csv.reader(data.splitlines(), delimiter=','))
    # cast to pandas DataFrame
    data = pd.DataFrame(data[1:], columns=data[0])
    # drop cities
    data = data[data.city == ''].drop('city', axis=1)

    return data

def formatData(data):
    """Formats the data from pullData"""
    # split into country, state, and county levels
    byCountry = data[(data.state == '') & (data.county == '')]
    byState = data[(data.state != '') & (data.county == '')]
    byCounty = data[data.county != '']
