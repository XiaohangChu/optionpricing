from yahoo_fin import options
import pandas as pd
from bs4 import BeautifulSoup
import requests
from scipy.stats import norm
import numpy as np
from yahoo_fin import stock_info
import datetime




class optionprice():
    def __init__(self, ticker, optiontype,strike):
        self.ticker = ticker
        self.optiontype = optiontype
        self.strike = strike
    def getstock(self):
        headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'}
        
        stockurl = f'https://finance.yahoo.com/quote/{self.ticker}'
        stockinfo = requests.get(stockurl, headers=headers)
        stocksoup = BeautifulSoup(stockinfo.text, 'html.parser')
        stockprice = stocksoup.find('span', {'class':'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
        
        dividendurl = f'https://finance.yahoo.com/quote/{self.ticker}/key-statistics?p={self.ticker}'
        dividendinfo = requests.get(dividendurl, headers=headers)
        dividendsoup = BeautifulSoup(dividendinfo.text, 'html.parser')
        dividendt = dividendsoup.find('div',{'class':'Fl(end) W(50%) smartphone_W(100%)'}).find('div',{'class':'Pstart(20px) smartphone_Pstart(0px)'}).find_all('td')[41].text
        
        interesturl = 'https://finance.yahoo.com/quote/%5ETNX?p=^TNX&.tsrc=fin-srch'
        interestinfo = requests.get(interesturl, headers = headers)
        interestsoup = BeautifulSoup(interestinfo.text, 'html.parser')
        interestrate = interestsoup.find('span',{'class' : 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
    
        if dividendt == 'N/A':
            dividendt = 0
            return [float(stockprice), float(dividendt)/100, float(interestrate)/100]
        else:
            dividendt = dividendt.strip('%')
            return [float(stockprice), float(dividendt)/100, float(interestrate)/100]
        
    def getoption(self):
        date = options.get_expiration_dates(self.ticker)
        for dates in date:
            print(dates)
        selected_date = input()
        expirationdate = datetime.datetime.strptime(selected_date,'%B %d, %Y').date()
        date_today = datetime.date.today()
        date_difference = float((expirationdate - date_today).days)
        pd.set_option('display.max_columns',None)
        chain = options.get_options_chain(self.ticker,selected_date)
        option = chain[self.optiontype]
        optionchain = option[option['Strike'] == self.strike]
        
        return float(optionchain['Last Price']), date_difference
    
    
    
    
    def getvol(self):
        current_date = datetime.date.today()
        yearago = current_date.replace(current_date.year - 1)
        stockinfo = stock_info.get_data(self.ticker,start_date=yearago,end_date=current_date)
        
        price = stockinfo['close']
        pricevar = price.var()
        pricestd = np.sqrt(pricevar)
        annualized_volatility = pricestd
        return annualized_volatility/100
    
    
    def bsprediction(self):
        stockprice, dividend, interestrate = self.getstock()
        optionprice, datediff = self.getoption()
        vol = self.getvol()
        
        N = norm.cdf

        def BS_CALL(S, K, T, q, r, sigma):
            d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            return S*np.exp(-q * T)*N(d1) - K * np.exp(-r*T)* N(d2)
    
        def BS_PUT(S, K, T, q, r, sigma):
            d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma* np.sqrt(T)
            return K*np.exp(-r*T)*N(-d2) - S*np.exp(-q*T)*N(-d1)
    
    
        if self.optiontype =='calls':
            callprice = BS_CALL(stockprice, self.strike, datediff/365, dividend, interestrate, vol)
            print("Using Black Scholes model, the theoretical option price is $"+ str(callprice))
        else:
            putprice = BS_PUT(stockprice, self.strike, datediff/365, dividend, interestrate, vol)
            print("Using Black Scholes model, the theoretical option price is $"+ str(putprice))



    
    def deltahedging(self):
        date = options.get_expiration_dates(self.ticker)
        for dates in date:
            print(dates)
        selected_date = input()
        expirationdate = datetime.datetime.strptime(selected_date,'%B %d, %Y').date()
        date_today = datetime.date.today()
        pd.set_option('display.max_columns',None)
        chain = options.get_options_chain(self.ticker,selected_date)
        option = chain[self.optiontype]
        optionchain = option[option['Strike'] == self.strike].replace('-',0)
        
        change = float(optionchain['Change'])
        previousprice = float(optionchain['Last Price']) - change
        optionpercent = change/previousprice
        
        
        
        
        headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'}    
        stock1url = f'https://finance.yahoo.com/quote/{self.ticker}'
        stock1info = requests.get(stock1url, headers=headers)
        stock1soup = BeautifulSoup(stock1info.text, 'html.parser')
        stockchange = stock1soup.find('span', {'class':'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)'}).text
        if stockchange[0] == '+':
            stockpercent = float(stockchange[8:-2])/100
            optiondelta = stockpercent/optionpercent 
            print('you need to short '+str(optiondelta * 100 * 5)+' share of stock')
        else:
            stockpercent = float(stockchange[8:-2])/100 *(-1)
            optiondelta = stockpercent/optionpercent 
            print('you need to long '+str(optiondelta * 100 * 5*(-1))+' share of stock')
            
            
            
aapl = optionprice('AAPL', 'calls', 130)
aapl.deltahedging()

