import twder
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
def getCurrencyName(currency):
    currency_list = {
        "USD" : "美元",
        "JPY" : "日圓",
        "HKD" : "港幣",
        "GBP" : "英鎊",
        "AUD" : "澳幣",
        "CAD" : "加拿大幣",
        "CHF" : "瑞士法郎",
        "SGD" : "新加坡幣",
        "ZAR" : "南非幣",
        "SEK" : "瑞典幣",
        "NZD" : "紐元",
        "THB" : "泰幣",
        "PHP" : "菲國比索",
        "IDR" : "印尼幣",
        "KRW" : "韓元",
        "MYR" : "馬來幣",
        "VND" : "越南盾",
        "CNY" : "人民幣"
        }
    try: currency_name = currency_list[currency]
    except: return "無可支援的外幣"
    return currency_name

def getExchangeRate(msg):
    """
    samlpe
    code = '換匯USD/TWD/100'
    code = '換匯USD/JPY/100'
    """
    currency_list = msg[2:].split("/")
    currency = currency_list[0]#輸入想查詢的匯率
    currency1 = currency_list[1]#輸入想兌換的匯率
    money_value = currency_list[2]#輸入金額數值
    url_coinbase = 'https://api.coinbase.com/v2/exchange-rates?currency=' + currency
    res = requests.get(url_coinbase)
    jData = res.json()
    pd_currency = jData['data']['rates']
    content = f"目前的兌換率為：{pd_currency[currency]}{currency}\n查詢的金額為:"
    amount = float(pd_currency[currency1])
    content += str('%.2f'%(amount * float(money_value))) + "" + currency1
    return content


# 查詢匯率
def showCurrency(code): #-> "JPY": # code 為外幣代碼
    content = ""
    currency_name = getCurrencyName(code)
    if currency_name == "無可支援的外幣": return "無可支援的外幣"
    # 資料格式 {貨幣代碼: (時間, 現金買入, 現金賣出, 即期買入, 即期賣出), ...}
    currency = twder.now(code) 
    # 當下時間
    now_time = str(currency[0])
    # 銀行現金買入價格
    buying_cash = "無資料" if currency[1] == '-' else str(float(currency[1])) 
    # 銀行現金賣出價格
    sold_cash = "無資料" if currency[2] == '-' else str(float(currency[2])) 
    # 銀行即期買入價格
    buying_spot = "無資料" if currency[3] == '-' else str(float(currency[3])) 
    # 銀行即期賣出價格
    sold_spot = "無資料" if currency[4] == '-' else str(float(currency[4])) 
    content +=  f"{currency_name} 最新掛牌時間為: {now_time}\n ---------- \n 現金買入價格: {buying_cash}\n 現金賣出價格: {sold_cash}\n 即期買入價格: {buying_spot}\n 即期賣出價格: {sold_spot}\n \n"
    return content