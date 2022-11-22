import streamlit as st
import pandas as pd

from datetime import datetime
from meteostat import Stations, Daily
from plotly.subplots import make_subplots
import plotly.graph_objects as go


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


day_hour = "daily"

st.title("Weather App with colourful plots.")

min_date = datetime(1850,5,4)


start = st.date_input(
    "Start Date",
    datetime(2020, 5,4), key='start', min_value=min_date)


end = st.date_input(
    "End Date",
    datetime(2022, 2, 1))

#print(start, type(start))
longitude = st.number_input('Choose longitude', value = 30.523333)


latitude = st.number_input('Choose latitude', value = 50.450001)


st.write('Start date is:', start)
st.write('End date is:', end)
st.write('Longitude: ', longitude)
st.write('Latitude: ', latitude)

#start = datetime(2015,1,1)
#end = datetime(2020,1,1)
start =datetime.combine(start, datetime.min.time())
end = datetime.combine(end, datetime.min.time())

stations = Stations()
stations = stations.nearby(latitude,longitude)
stations = stations.inventory(day_hour, (start, end))
station = stations.fetch(1)
more_stations = stations.fetch(3)

# # Get daily data
data = Daily(station, start, end)
data = data.fetch()

st.write("Station: ", station['name'].iloc[0])

st.write('The three closest stations to chosen lat/long:')
st.dataframe(more_stations)
st.dataframe(data.head(2))

#st.dataframe(data)


fig = subplots(data)
st.header("General Plots")
st.plotly_chart(fig,use_container_width=True)


status = st.radio("Select Period: ", ('Week', 'Month','Year'))
status_t = st.radio("Select Option: ", ('avg temp', 'min temp','max temp'))

if (status == 'Week') and (status_t == "avg temp"):
    fig2 = plot_period_choose_date(data, period = 'week', t_param="tavg")
elif (status == 'Week') and (status_t == "min temp"):
    fig2 = plot_period_choose_date(data, period = 'week', t_param="tmin")
elif (status == 'Week') and (status_t == "max temp"):
    fig2 = plot_period_choose_date(data, period = 'week', t_param="tmax")
#######
elif (status == "Month") and (status_t == "avg temp"):
    fig2 = plot_period_choose_date(data, period = 'month', t_param="tavg")
elif (status == "Month") and (status_t == "min temp"):
    fig2 = plot_period_choose_date(data, period = 'month', t_param="tmin")
elif (status == "Month") and (status_t == "max temp"):
    fig2 = plot_period_choose_date(data, period = 'month', t_param="tmax")
#######
elif (status == "Year") and (status_t == "avg temp"):
    fig2 = plot_period_choose_date(data, period = 'year', t_param="tavg")
elif (status == "Year") and (status_t == "min temp"):
    fig2 = plot_period_choose_date(data, period = 'year', t_param="tmin")
elif (status == "Year") and (status_t == "max temp"):
    fig2 = plot_period_choose_date(data, period = 'year', t_param="tmax")

#fig2 = plot_period_choose_date(data, period = 'month')
st.plotly_chart(fig2)

@st.cache
def convert_df(df, csv= False):
    to_download = []
    if csv:
        to_download = df.to_csv()
    return to_download

download = st.radio("Download format: ", ('Nothing','csv'))

if download == "csv":
    csv = convert_df(data, csv=True)
    filename = 'my_data.csv'


#st.write(st.session_state)

if st.button('Want to download?'):
    if download == "Nothing":
        st.write("Choose format (csv) above and click again")
    else:
        st.write('Click download button below')
        st.download_button(
            label="Click to download data",
            data=csv,
            file_name=filename
        )
# else:
#     st.write('No downloads')

