import streamlit as st
import pandas as pd

from datetime import datetime
from meteostat import Stations, Daily
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import myweather as mw


day_hour = "daily"

st.title("Weather App with colourful plots.")

min_date = datetime(1850,5,4)

with st.sidebar:
    st.header("Pick date, lat and long:")
    start = st.date_input(
        "Start Date",
        datetime(2020, 5,4), key='start', min_value=min_date)


    end = st.date_input(
        "End Date",
        datetime(2022, 2, 1))

    #print(start, type(start))
    longitude = st.number_input('Choose longitude', value = 30.523333)


    latitude = st.number_input('Choose latitude', value = 50.450001)


#st.write('Start date is:', start)
#st.write('End date is:', end)
#st.write('Longitude: ', longitude)
#st.write('Latitude: ', latitude)

#start = datetime(2015,1,1)
#end = datetime(2020,1,1)
start =datetime.combine(start, datetime.min.time())
end = datetime.combine(end, datetime.min.time())

stations = Stations()
stations = stations.nearby(latitude,longitude)
stations = stations.inventory(day_hour, (start, end))
station = stations.fetch(1)
more_stations = stations.fetch(3)
more_stations = more_stations.set_index("name", drop=True)
more_stations = more_stations[["country", "latitude", "longitude","elevation"]]

# # Get daily data
data = Daily(station, start, end)
data = data.fetch()

st.write("Station: ", station['name'].iloc[0])

st.write('The three closest stations to chosen lat/long:')
st.dataframe(more_stations)
st.write("Glimpse at data of chosen station:")
st.dataframe(data.head(2))

#st.dataframe(data)


fig = mw.subplots(data)
st.header("General Plots")
st.plotly_chart(fig,use_container_width=True)


status = st.radio("Select Period: ", ('Week', 'Month','Year'))
status_t = st.radio("Select Option: ", ('avg temp', 'min temp','max temp'))

if (status == 'Week') and (status_t == "avg temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'week', t_param="tavg")
elif (status == 'Week') and (status_t == "min temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'week', t_param="tmin")
elif (status == 'Week') and (status_t == "max temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'week', t_param="tmax")
#######
elif (status == "Month") and (status_t == "avg temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'month', t_param="tavg")
elif (status == "Month") and (status_t == "min temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'month', t_param="tmin")
elif (status == "Month") and (status_t == "max temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'month', t_param="tmax")
#######
elif (status == "Year") and (status_t == "avg temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'year', t_param="tavg")
elif (status == "Year") and (status_t == "min temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'year', t_param="tmin")
elif (status == "Year") and (status_t == "max temp"):
    fig2 = mw.plot_period_choose_date(data, period = 'year', t_param="tmax")

#fig2 = plot_period_choose_date(data, period = 'month')
st.plotly_chart(fig2)

@st.cache
def convert_df(df, type = "csv", name = "my_data"):
    if type == "csv":
        to_download = df.to_csv()
        name = f'{name}.csv'
    elif type == "pickle":
        name = f'{name}.pkl'
        to_download = df.to_pickle(name)       
    elif type == "xlsx":
        name = f'{name}.xlsx'
        to_download = df.to_excel(name)
        
    else:
        raise ValueError("Unknown type")
    return to_download, name




#st.write(st.session_state)
with st.sidebar:
    #with st.form(key="my_download"):
    ##download = st.radio("Download format: ", ('csv',"xlsx",'pickle'))

    # if download == "csv":
    #     download_data = convert_df(data, type = "csv")
    # elif download == "pickle":
    #     download_data = convert_df(data, type = "pickle")
    # elif download == "xlsx":
    #     download_data = convert_df(data, type = "xlsx")
    #download_data, name_download_data = convert_df(data, type = download)

    st.download_button(
                label="Click to download data",
                data=convert_df(data, type = "csv")[0],
                file_name= convert_df(data, type = "csv")[1]
        )

        #st.form_submit_button("download")
   
