import streamlit as st
import MetaTrader5 as mt
from datetime import datetime, timedelta
import pandas as pd
import requests
import time
import plotly.graph_objects  as go
import plotly.express  as px
import json
import pandas_ta as ta

def empty(placeholder):
    placeholder.empty()

loginid = 51911733
password = '72j@b58zH&ih2I'
server = 'ICMarketsSC-Demo'
mt.initialize()
mt.login(loginid, password,server)


st.set_page_config (layout = 'wide')
st.title('Market Data')

#ind_list = df.ta.indicators(as_list = True)


placeholder = st.empty()
ticker = st.sidebar.selectbox('Ticker', ['XAUUSD','US500','GBPUSD','EURUSD','USDJPY','TSLA.NAS','MSFT.NAS','AAPL.NAS'])
timeframe = st.sidebar.number_input('Timeframe (in hours)', min_value=0.0, value=0.5, step=0.5, format = "%0.1f")
# weekday = datetime.today().weekday() 
# if weekday < 5:
#     default_date = datetime.today() - timedelta(days = 1 )
# else:
#     default_date = datetime.today() - timedelta(days = weekday-3 )

# from_date = st.sidebar.date_input('Start Date', value = default_date)

ind_list = [ 'ema', 'sma', 'rsi','bbands'] 
technical_indicator = st.sidebar.selectbox('Technical Indicator', ind_list )

time_period = st.sidebar.selectbox('Time Period', ['1 minute','1 hour','1 day','1 week','1 month'])

method = technical_indicator

flag = mt.COPY_TICKS_INFO

interval_mapping = {'1 minute': mt.TIMEFRAME_M1,
                    '1 hour': mt.TIMEFRAME_H1,
                    '1 day': mt.TIMEFRAME_D1, 
                    '1 week': mt.TIMEFRAME_W1, 
                    '1 month':mt.TIMEFRAME_M1 }



for i in range(100):
        with placeholder.container():
            left, right = st.columns([.65,.35])
            left.subheader('Live Market Data')
            right.subheader('News Feed')

            #bid ask proce
            from_date = datetime.now() - timedelta(hours=timeframe, minutes=0)
            ticksdata = mt.copy_ticks_range(ticker , from_date, datetime.now(), flag)
            ticksdata = pd.DataFrame(ticksdata)
            ticksdata["time"] = pd.to_datetime(ticksdata["time"], unit = 's')
            ticksdata["time_msc"] = pd.to_datetime(ticksdata["time_msc"], unit = 'ms')
            ticksdata.sort_values( by="time_msc", ascending=True, inplace=True)
            ticksdata["bid_lag"] = ticksdata["bid"].shift(1)
            ticksdata["ask_lag"] = ticksdata["ask"].shift(1)
            latest_price = ticksdata.tail(1).reset_index()

            # ohlc data for indicator
            if i%60 == 0:
                interval =  interval_mapping.get(time_period)
                ohlc = pd.DataFrame(mt.copy_rates_range(ticker,interval, from_date, datetime.now()))
                ohlc["time"] = pd.to_datetime(ohlc["time"], unit = 's')
                indicator_df = pd.DataFrame(getattr(ta, method)(low = ohlc["low"], close = ohlc["close"], high = ohlc["high"], volume = ohlc["tick_volume"]))
                indicator_df["close"] = ohlc["close"]
        # av_api_key = "5D5CAQVJJWI0CRKJ"
        # base_url = "https://www.alphavantage.co/query?"
        # function = 'NEWS_SENTIMENT'
        # tickers = 'COIN,CRYPTO:BTC,FOREX:USD'
        # limit = 5
        # now = datetime.now()
        # #time_start = now.strftime('%Y%m%dT%H%M')
        # time_start = '20240817T0130'
        # url = f'{base_url}function={function}&tickers={tickers}&time_from={time_start}&limit={limit}&apikey={av_api_key}'
        # r = requests.get(url)
        # data = r.json()
            with open('news_feed.txt', 'r') as file:
                news_data = json.load(file)

            #with placeholder.container():
            bid_col, ask_col = left.columns(2)
            with bid_col:
                st.metric(label = f'Bid Price', value=f'{latest_price.iloc[0]["bid"]}' ,delta=f'{(latest_price.iloc[0]["bid"] - latest_price.iloc[0]["bid_lag"]):.2f}' )
            with ask_col:
                st.metric(label = f'Ask Price', value=f'{latest_price.iloc[0]["ask"]}' ,delta=f'{(latest_price.iloc[0]["ask"] - latest_price.iloc[0]["ask_lag"]):.2f}' )
            fig = go.Figure()
            fig.add_trace(go.Scatter( x=ticksdata.time_msc, y=ticksdata.bid, mode='markers',name="Bid Price"))
            fig.add_trace(go.Scatter( x=ticksdata.time_msc, y=ticksdata.ask, mode='markers',name="Ask Price"))
            fig.update_layout(hovermode="x")
            left.plotly_chart(fig)

            # ohlc chart
            left.subheader('OHLC Chart')
            fig_ohlc = go.Figure()
            fig_ohlc.add_trace(go.Candlestick(x = ohlc['time'] ,
                                              open = ohlc['open'],
                                              high = ohlc['high'],
                                              low = ohlc['low'],
                                              close = ohlc['close']
                                              ))
            left.plotly_chart(fig_ohlc)

            # indicator plot
            left.subheader('Technical Indicator')
            fig_indicator = px.line(indicator_df)
            left.plotly_chart(fig_indicator)

            for j in range(len(news_data['feed'])):
                    title = news_data['feed'][j].get('title')
                    url_link = news_data['feed'][j].get('url')
                    right.write(title)
                    right.write(url_link)


        time.sleep(1)








    