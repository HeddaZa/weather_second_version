import streamlit as st
import pandas as pd

from datetime import datetime
from meteostat import Stations, Daily
from plotly.subplots import make_subplots
import plotly.graph_objects as go


###### data cleaning functions:
def fill_nans(data):
    """fills nans of several columns"""
    nan_dict = {
        "prcp":0,
        "snow":0,
        "tmin":"ffill",
        "wspd":"ffill",
        "pres":"ffill"
    }
    return data.fillna(nan_dict)

def drop_columns_with_more_than_80_nan(data):
    """drops columns with more than 80% nans"""
    value_count_nan = data.isnull().sum()/data.shape[0]
    over_80 = value_count_nan[value_count_nan >= 0.8].index
    return data.drop(columns =  over_80)


###### plot functions:
def subplots(reset):
    ''' 
    plots three subplots: 
    - temperature (mean temperature, min temperature, max temperature)
    - precipitation
    - wind (mean velocity, max velocity)
    '''
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True)

    fig.add_trace(
        go.Scatter(x=reset.index, y=reset['tavg'],
        name = 'mean temperature',
        legendgroup = '1',
        line = dict(color = 'rgb(255,102,102)')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=reset.index, y=reset['tmax'],
        name = 'max temperature',
        legendgroup = '1',
        line = dict(color = 'rgb(204,0,0)')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=reset.index, y=reset['tmin'],
        name= 'min temperature',
        showlegend= True,
        legendgroup = '1',
        line = dict(color = 'rgb(0,128,255)')),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=reset.index, y=reset['prcp'],
        name = 'rain',
        #hoverinfo= 'name',
        legendgroup = '2',
        line = dict(color = 'rgb(0,100,255)'),
        fill='tozeroy'),
        row=2, col=1
    )


    fig.add_trace(
        go.Scatter(x=reset.index, y=reset['snow'],
        name = 'snow',
        legendgroup = '3',
        line = dict(color = 'rgb(204,0,204)')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=reset.index, y=reset['wspd'],
        name = 'wind speed',
        legendgroup = '4',
        line = dict(color = 'rgb(204,0,102)')),
        row=4, col=1
    )

    fig.update_layout(
        height=1500, 
        width=1000, 
        title_text="Plots of Temperature, Precipitation, and Wind Speed",
        legend_tracegroupgap = 330,
        xaxis3_title = 'Date',
        yaxis1_title = 'Celsius',
        yaxis2_title = 'mm',
        yaxis3_title = 'm/s',
        xaxis_showticklabels=True, 
        xaxis2_showticklabels=True
        )
    return fig


def period_index(df, period):
    df = df.reset_index(drop = False)
    df['time'] = pd.to_datetime(df['time'])
    if period == 'year':
        df['period'] = df['time'].dt.year
        df['period_xaxis'] = df['time'].apply(lambda x: x.replace(year = 2000))
    elif period == 'month':
        df['period'] = df['time'].dt.month
        df['period_xaxis'] = df['time'].dt.day
    elif period == 'week':
        df['period'] = df['time'].dt.isocalendar().week
        df['period_xaxis'] = df['time'].dt.day_name()
    else:
        raise ValueError('Wrong period format')
    return df.set_index(['period','time'])

def plot_period(df, period = 'week'):
    df = period_index(df, period = period)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    for index in df.index.levels[0]:
        period_data = df.loc[index]
        fig.add_trace(
            go.Scatter(x = period_data['period_xaxis'],y=period_data['tavg'],
            name = str(index)),
            row = 1, col = 1
        )
    fig.update_layout( title_text=f"Comparison by {period}")
    return fig

def filter_for_date(df, start_date, end_date):
    return df[df.index.to_series().between(start_date, end_date)]

def plot_period_choose_date(df, period = 'week', t_param = "tavg"):
    #df = filter_for_date(df, start_date, end_date)
    #df = df.loc[start_date:end_date]
    df = period_index(df, period = period)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    for index in df.index.levels[0]:
        period_data = df.loc[index]
        fig.add_trace(
            go.Scatter(x = period_data['period_xaxis'],y=period_data[t_param],
            name = str(index)),
            row = 1, col = 1
        )
    fig.update_layout( title_text=f"Temperature comparison by {period}")
    return fig