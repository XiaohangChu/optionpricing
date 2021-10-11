# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 17:28:42 2021

@author: 16148
"""

from yahoo_fin import options
import pandas as pd
from bs4 import BeautifulSoup
import requests
from scipy.stats import norm
import numpy as np
from yahoo_fin import stock_info
import datetime




"""
get stock price, dividend rate and market riskfree interest rate, source yahoo finance
"""
def getstock(symbol):
    headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'}
    
    stockurl = f'https://finance.yahoo.com/quote/{symbol}'
    stockinfo = requests.get(stockurl, headers=headers)
    stocksoup = BeautifulSoup(stockinfo.text, 'html.parser')
    stockprice = stocksoup.find('span', {'class':'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
    
    dividendurl = f'https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}'
    dividendinfo = requests.get(dividendurl, headers=headers)
    dividendsoup = BeautifulSoup(dividendinfo.text, 'html.parser')
    dividendt = dividendsoup.find('div',{'class':'Fl(end) W(50%) smartphone_W(100%)'}).find('div',{'class':'Pstart(20px) smartphone_Pstart(0px)'}).find_all('td')[41].text
    
    interesturl = 'https://finance.yahoo.com/quote/%5ETNX?p=^TNX&.tsrc=fin-srch'
    interestinfo = requests.get(interesturl, headers = headers)
    interestsoup = BeautifulSoup(interestinfo.text, 'html.parser')
    interestrate = interestsoup.find('span',{'class' : 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text

    if dividendt == 'N/A':
        dividendt = 0
        print('Stock price is: $'+(stockprice))
        print('Annual dividend rate is '+str(dividendt)+"%")
        print('Current risk free interest rate is '+(interestrate)+"%")
        return float(stockprice), float(dividendt)/100, float(interestrate)/100
    else:
        dividendt = dividendt.strip('%')
        print('Stock price is: $'+(stockprice))
        print('Annual dividend rate is '+str(dividendt)+"%")
        print('Current risk free interest rate is '+(interestrate)+"%")
        return float(stockprice), float(dividendt)/100, float(interestrate)/100
"""
get option price, source yahoo finance
"""   
    
def getoption(ticker,optiontype,strike):
        date = options.get_expiration_dates(ticker)
        for dates in date:
            print(dates)
        selected_date = input()
        expirationdate = datetime.datetime.strptime(selected_date,'%B %d, %Y').date()
        date_today = datetime.date.today()
        date_difference = float((expirationdate - date_today).days)
        pd.set_option('display.max_columns',None)
        chain = options.get_options_chain(ticker,selected_date)
        option = chain[optiontype]
        optionchain = option[option['Strike'] == strike]
        
        return float(optionchain['Last Price']), date_difference
''' 
get theoritical volatility for the stock in past year
'''

def getvol(ticker):
        current_date = datetime.date.today()
        yearago = current_date.replace(current_date.year - 1)
        stockinfo = stock_info.get_data(ticker,start_date=yearago,end_date=current_date)
        
        price = stockinfo['close']
        pricevar = price.var()
        pricestd = np.sqrt(pricevar)
        annualized_volatility = pricestd
        return annualized_volatility/100
    
'''
applying b-s option pricing model
'''
   

N = norm.cdf

def BS_CALL(S, K, T, q, r, sigma):
    d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S*np.exp(-q * T)*N(d1) - K * np.exp(-r*T)* N(d2)

def BS_PUT(S, K, T, q, r, sigma):
    d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma* np.sqrt(T)
    return K*np.exp(-r*T)*N(-d2) - S*np.exp(-q*T)*N(-d1)

print('ticker, All capital such as "UBER","ASML"')
stock = input() 
print('strike price')
strike = int(input())
print('calls or puts')
optiontype = input() 

price,div,interest = getstock(stock)


optionprice,datedifference = getoption(stock, optiontype, strike)
print("the option market price is $"+str(optionprice))

sigma = getvol(stock)

if optiontype =='calls':
    callprice = BS_CALL(price, strike, datedifference/365, div, interest, sigma)
    print("Using Black Scholes model, the theoretical option price is $"+ str(callprice))
else:
    putprice = BS_PUT(price, strike, datedifference/365, div, interest, sigma)
    print("Using Black Scholes model, the theoretical option price is $"+ str(putprice))

