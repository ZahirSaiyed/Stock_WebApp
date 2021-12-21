#Created: 12/17/2021
#Author: Zahir Saiyed

import yfinance as yf
import streamlit as st
import pandas as pd

st.write("""
# Stock Analysis App
""")

#creating a navigation bar to cater to different user needs
nav = st.sidebar.radio("Navigation", ["Individual", "Relative Returns", "Import Companies"])

if nav == "Import Companies":
    file = st.file_uploader("Please upload a file with just tickers", type="xlsx")
    invalid = ['hi']
    if file:
        companyDF = pd.read_excel(file)
        st.dataframe(companyDF)

        cList = companyDF['Ticker'].values.tolist()


        start = st.date_input('Start', value = pd.to_datetime('2016-01-04'))
        end = st.date_input('Start', value = pd.to_datetime('2020-12-31'))
        years = 5

        df = yf.download(cList,start,end)['Adj Close']
        df = df.fillna(-1)

        returns = pd.DataFrame(columns=list(df.columns), index =['Total Returns', 'Annualized Return'])
        #returns = returns.iloc[: , 1:]

        st.dataframe(df.head())

        for col in returns:
            if(df.at[0,col] != -1):
                returns.at['Total Returns',col] = (df[col][-1] - df[col][0])/(df[col][0])

        st.dataframe(returns)

        for col in returns:
            if(df.at[0,col] != -1):
                returns.at['Annualized Return',col] = ((1+returns.at['Total Returns',col])**(1/years))-1

        st.dataframe(returns)


if nav == "Relative Returns":

    #reading in all possible tickers
    tickers = ('AAPL', 'AMC', 'TSLA', 'BTC-USD', '^RUA', '^DJI', 'XLV')
    #creating multi-select dropdown
    ticker_dropdown = st.multiselect('Pick your tickers', tickers)
    #start date
    start = st.date_input('Start', value = pd.to_datetime('2010-01-01'))
    end = st.date_input('End', value = pd.to_datetime('today'))

    # Directly taken from https://www.youtube.com/watch?v=Km2KDo6tFpQ
    def relativeret(df):
        rel = df.pct_change()
        cumret = (1+rel).cumprod() - 1
        cumret = cumret.fillna(0)
        return cumret

    if len(ticker_dropdown) > 0:
        # downloading data for chosen tickers + calculating relative returns
        df = relativeret(yf.download(ticker_dropdown,start,end)['Adj Close'])
        st.markdown(f"Shown are the returns of: {ticker_dropdown}")
        st.line_chart(df)
        st.write("### Cumulative Returns (%)", df.sort_index())


if nav == "Individual": 
    ##taking in custom ticker from user; if no input, then Google is default
    ticker_input = st.text_input("Enter a ticker", "GOOGL")
    ##printing the chosen ticker on screen
    st.markdown(f"Shown are the stock **closing price** and ***volume*** of: {ticker_input}")

    # https://towardsdatascience.com/how-to-get-stock-data-using-python-c0de1df17e75
    #define the ticker symbol
    tickerSymbol = ticker_input
    #get data on this ticker
    tickerData = yf.Ticker(tickerSymbol)
    #get the historical prices for this ticker
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')
    # Open	High	Low	Close	Volume	Dividends	Stock Splits

    st.write("""
    ## Closing Price
    """)
    st.line_chart(tickerDf.Close)
    st.write("""
    ## Volume Price
    """)
    st.line_chart(tickerDf.Volume)

    st.write("## Other Metrics")
    st.write("### Quarterly Financials")
    st.write(tickerData.quarterly_financials)
    
    st.write("### Sustainability")
    if tickerData.sustainability is not None:
        st.write(pd.DataFrame.transpose(tickerData.sustainability))
    
    st.write("## In The News")
    newsDF = pd.DataFrame(tickerData.news)
    st.table(newsDF[['title','link']])

