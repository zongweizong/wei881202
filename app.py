# -- coding: utf-8 --**
#載入LineBot所需要的套件
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import re
import requests
from line_bot import *
from bs4 import BeautifulSoup 
import twstock
import datetime
import Msg_Template
import EXRate
import mongodb
import twder
import json,time
import place
import yfinance as yf
import mplfinance as mpf
import pyimgur
import io
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
app = Flask(__name__)
IMGUR_CLIENT_ID = '4670b4b0bf170b4'
access_token = 'aNQvaXsXOedUChNcmQryfaaFLckYzvQ+Y6wi28/fq0vSDTd18PH+SaNZc+y0VJaxrrvGN8292ki0utK+Gx1wyFVJWfgHBc9AQkpbkz0BAzBqrq0yTbhJI2glggHON/UCWs3JWf0ETfbcDb9BbyAXyQdB04t89/1O/w1cDnyilFU='
channel_secret = '753fff928d206cda0db7a5b2f8271206'
mat_d = {}
# **************   CNN   ************* #
#加載以訓練的CNN模型
model = load_model("mnist_cnn_model.h5")


def preprocess_image(image):
    
    """
    預處理上傳的圖像，使其符合CNN模型的輸出要求
    """

    image = image.convert('L')
    image = image.resize((28,28))
    image = np.array(image)
    image = image / 255.0
    image = np.expand_dims(image,axls= 0)
    image = np.expand_dims(image,axls= -1)
    return image


def plot_stock_k_chart(IMGUR_CLIENT_ID,stock = "0050",date_from='2020-01-01'):
    """
    進行各股K線繪製，回傳至雲端圖床的連結，將顯示包含5MA、20MA及量價關係，起始預設自2020-01-01起迄昨日收盤價。
    ::
    ::

    """


    stock = str(stock) + '.TW'
    try:

        #使用yfinance獲取數據
        print(f"正在獲取股票資訊:{stock}")
        df = yf.download(stock,start=date_from)

        #檢查數據是否獲取成功

        if df is None or df.empty:
            print("未能獲取股票數據，可能因為股票代碼不正確或數據來源問題")
            return None
        print("股票數據獲取成功，開始繪製Ｋ線圖...")
        mpf.plot(df,type='candle',mav =(5,20),volume =True,ylabel=stock.upper() + 'Price', savefig = 'testsave.png')
        
        #上傳圖片到IMGUR

        PATH = 'testsave.png'
        im = pyimgur.Imgur(IMGUR_CLIENT_ID)
        uploaded_imge = im.upload_image(PATH,title=stock + "candlestick chart")
        print(f"圖片上傳成功:{uploaded_imge.link}")
        return uploaded_imge.link
    except Exception as e:
        print(f"錯誤: {e}")
        return None
    

def reply_image(msg,rk,token):
    headers = {'Authorization':f'Bearer {token}', 'Content-Type':'application/json'}
    body = {
    'replyToken' :rk,
    'messages': [{
            'type': 'image',
            'originalContentUrl': msg,
            "previewImageUrl": msg
        }]
    }
    req = requests.request('POST', 'https://api.line.me/v2/bot/message/reply', headers = headers, data=json.dumps(body).encode('utf-8'))
    print(req.text)
# 抓使用者設定它關心的匯率
def cache_users_currency():
    db=mongodb.constructor_currency()
    nameList = db.list_collection_names()
    users = []
    for i in range(len(nameList)):
        collect = db[nameList[i]]
        cel = list(collect.find({"tag":'currency'}))
        users.append(cel)
    return users
def Usage(event):
    push_msg(event," 🚬 🚬 殺手BOT說明書 🚬 🚬   \
                    \n\
                    \n使用者您好，雖然我是一名殺手級選手🥷🏼，但我可以為您查詢你所要的資訊\
                    \n\
                    \n ❤️常用軟件❤️ ➡️ 輸入：開始玩\
                    \n 📣股價資訊📣 ➡️ 輸入：股價查詢\
                    \n 📣油價通知📣 ➡️ 輸入：油價查詢\
                    \n 🔊匯率通知🔊 ➡️ 輸入：查詢匯率\
                    \n 📡查看衛星雲圖📡 ➡️ 輸入：衛星雲圖\
                    \n 💵匯率兌換💵 ➡️ 🔍換匯USD/TWD")
# 監聽所有來自 /callback 的 Post Request
def push_msg(event,msg):
    try:
        user_id = event.source.user_id
        line_bot_api.push_message(user_id,TextSendMessage(text=msg))
    except:
        room_id = event.source.room_id
        line_bot_api.push_message(room_id,TextSendMessage(text=msg))

# 抓使用者設定它關心的股票
def cache_users_stock():
    db=mongodb.constructor_stock()
    nameList = db.list_collection_names()
    users = []
    for i in range(len(nameList)):
        collect = db[nameList[i]]
        cel = list(collect.find({"tag":'stock'}))
        users.append(cel)
    return users

# 油價查詢
def oil_price():
    target_url = 'https://gas.goodlife.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.select('#main')[0].text.replace('\n', '').split('(')[0]
    gas_price = soup.select('#gas-price')[0].text.replace('\n\n\n', '').replace(' ', '')
    cpc = soup.select('#cpc')[0].text.replace(' ', '')
    content = '{}\n{}{}'.format(title, gas_price, cpc)
    return content

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)


    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # message = TextSendMessage(text=event.message.text)
    # line_bot_api.reply_message(event.reply_token, message)
    msg = str(event.message.text).upper().strip() # 使用者輸入的內容
    profile = line_bot_api.get_profile(event.source.user_id)
   
    usespeak=str(event.message.text) #使用者講的話
    uid = profile.user_id #使用者ID
    user_name = profile.display_name #使用者名稱
    
    ######################## 匯率區 ##############################################    
    if re.match("查詢匯率", msg):
        btn_msg = Msg_Template.stock_reply_rate()
        line_bot_api.push_message(uid, btn_msg)
        return 0
    if re.match("換匯[A-Z]{3}/[A-Z{3}]", msg):
        line_bot_api.push_message(uid,TextSendMessage("將為您做外匯計算....."))
        content = EXRate.getExchangeRate(msg)
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    if re.match('幣別種類',msg):
        message = Msg_Template.show_Button()
        line_bot_api.reply_message(event.reply_token,message)
    if re.match('新增外幣[A-Z]{3}', msg):
        currency = msg[4:7]
        currency_name = EXRate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣": content = "無可支援的外幣"
        elif re.match('新增外幣[A-Z]{3}[<>][0-9]', msg):
            content = mongodb.write_my_currency(uid , user_name, currency, msg[7:8], msg[8:])
        else:
            content = mongodb.write_my_currency(uid , user_name, currency, "未設定", "未設定")
        
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    if re.match('我的外幣', msg):
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 匯率查詢中...'))
        content = mongodb.show_my_currency(uid, user_name)
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    if re.match('刪除外幣[A-Z]{3}', msg):
        content = mongodb.delete_my_currency(user_name, msg[4:7])
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    
    if re.match('清空外幣', msg):
        content = mongodb.delete_my_allcurrency(user_name, uid)
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    ##############給匯率走勢圖#############
    if re.match("CT[A-Z]{3}", msg):   
        currency = msg[2:5] # 外幣代號
        if EXRate.getCurrencyName(currency) == "無可支援的外幣":
            line_bot_api.push_message(uid, TextSendMessage('無可支援的外幣'))
            return 0
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 將會給您匯率走勢圖'))
        cash_imgurl = EXRate.cash_exrate_sixMonth(currency)            
        if cash_imgurl == "現金匯率無資料可分析":
            line_bot_api.push_message(uid, TextSendMessage('現金匯率無資料可分析'))
        else:
            line_bot_api.push_message(uid, ImageSendMessage(original_content_url=cash_imgurl, preview_image_url=cash_imgurl))
        
        spot_imgurl = EXRate.spot_exrate_sixMonth(currency)
        if spot_imgurl == "即期匯率無資料可分析":
            line_bot_api.push_message(uid, TextSendMessage('即期匯率無資料可分析'))
        else:
            line_bot_api.push_message(uid, ImageSendMessage(original_content_url=spot_imgurl, preview_image_url=spot_imgurl))
        btn_msg = Msg_Template.realtime_currency_other(currency)
        line_bot_api.push_message(uid, btn_msg)
        return 0
    if re.match('外幣[A-Z]{3}',msg):
        currency = msg[2:5] # 外幣代號
        currency_name = EXRate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣": 
            content = "無可支援的外幣"
            line_bot_api.push_message(uid, TextSendMessage(content))
        else:
            line_bot_api.push_message(uid, TextSendMessage(f'您要查詢的外幣是: {currency_name}'))
            content = EXRate.showCurrency(currency)
            #content = EXRate.getExchangeRate(msg)
            line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    ######################## 使用說明 選單 油價查詢################################
    if event.message.text == "油價查詢":
        content = oil_price()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "殺手說明書":
        Usage(event)
        print(user_name)

    if re.match("分析趨勢圖",msg):
        message = Msg_Template.stock_reply_other()
        line_bot_api.reply_message(event.reply_token,message)
    
    ############################### 股票區 ################################
    
    if re.match('關注[0-9]{4}[<>][0-9]' ,msg):
        stockNumber = msg[2:6]
        content = mongodb.write_my_stock(uid, user_name , stockNumber, msg[6:7], msg[7:])
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    # 查詢股票篩選條件清單
    if re.match('股票清單',msg): 
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 股票查詢中...'))
        content = mongodb.show_stock_setting(user_name, uid)
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    if event.message.text == "股價查詢":
        line_bot_api.push_message(uid,TextSendMessage("請輸入#股票代號....."))
    if(msg.startswith('#')):
            text = msg[1:]
            content = ''

            stock_rt = twstock.realtime.get(text)
            my_datetime = datetime.datetime.fromtimestamp(stock_rt['timestamp']+8*60*60)
            my_time = my_datetime.strftime('%H:%M:%S')

            content += '%s (%s) %s\n' %(
                stock_rt['info']['name'],
                stock_rt['info']['code'],
                my_time)
            content += '現價: %s / 開盤: %s\n'%(
                stock_rt['realtime']['latest_trade_price'],
                stock_rt['realtime']['open'])
            content += '最高: %s / 最低: %s\n' %(
                stock_rt['realtime']['high'],
                stock_rt['realtime']['low'])
            content += '量: %s\n' %(stock_rt['realtime']['accumulate_trade_volume'])

            stock = twstock.Stock(text)#twstock.Stock('2330')
            content += '-----\n'
            content += '最近五日價格: \n'
            price5 = stock.price[-5:][::-1]
            date5 = stock.date[-5:][::-1]
            for i in range(len(price5)):
                #content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d %H:%M:%S"), price5[i])
                content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d"), price5[i])
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )
    # 刪除存在資料庫裡面的股票
    if re.match('刪除[0-9]{4}',msg): 
        content = mongodb.delete_my_stock(user_name, msg[2:])
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    # 清空存在資料庫裡面的股票
    if re.match('清空股票',msg): 
        content = mongodb.delete_my_allstock( user_name, uid)
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    
    if event.message.text[:2].upper() == "@K" : #這段主要在畫Ｋ線圖
        input_word = event.message.text.replace("  ","") #合併字串取消空白
        stock_name =input_word[2:6]#2330
        start_date =input_word[6:]
        content = plot_stock_k_chart(IMGUR_CLIENT_ID,stock_name,start_date)
        message = ImageSendMessage(original_content_url=content,preview_image_url=content)
        line_bot_api.reply_message(event.reply_token,message)
    
    ################################ 目錄區 ##########################################
    if event.message.text == "開始玩":
        message = TemplateSendMessage(
        alt_text='目錄 template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/j0udLKo.png',
                        title='社群網站',
                        text='請選擇你要使用的網站',
                        actions=[
                            URIAction(
                                label='Facebook',
                                uri='https://liff.line.me/2006134072-QYmMEpmK'
                            ),
                            URIAction(
                                label='Instagram',
                                uri='https://liff.line.me/2006134072-2zLJ3ALp'
                            ),
                            URIAction(
                                label='Twitter',
                                uri='https://x.com/'
                            )
                        ]
                    ),
                CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/lmxC1Dy.png',
                        title='影音網站',
                        text='請選擇你要使用的網站',
                        actions=[
                            URIAction(
                                label='Netflix',
                                uri='https://www.netflix.com/browse'
                            ),
                            URIAction(
                                label='Youtube',
                                uri='https://www.youtube.com/'
                            ),
                            URIAction(
                                label='Spotify',
                                uri='https://open.spotify.com/'
                            )
                        ]
                    ),
                CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/aLMBuVk.png',
                        title='今天看啥片？',
                        text='請選擇您今天要尻尻的網站',
                        actions=[
                            URIAction(
                                label='漫畫',
                                uri='https://hanime1.me/comics'
                            ),
                            URIAction(
                                label='Japan video',
                                uri='https://missav.com/genres?page=2'
                            ),
                            URIAction(
                                label='素人video',
                                uri='https://ppp.porn/new/'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    if re.match("股價提醒", msg):
        import schedule
        import time
        # 查看當前股價
        def look_stock_price(stock, condition, price, userID):
            print(userID)
            url = 'https://tw.stock.yahoo.com/q/q?s=' + stock
            list_req = requests.get(url)
            soup = BeautifulSoup(list_req.content, "html.parser")
            getstock = soup.find('span', class_='Fz(32px)').string
            content = stock + "當前股市價格為: " +  getstock
            if condition == '<':
                content += "\n篩選條件為: < "+ price
                if float(getstock) < float(price):
                    content += "\n符合" + getstock + " < " + price + "的篩選條件"
                    line_bot_api.push_message(userID, TextSendMessage(text=content))
            elif condition == '>':
                content += "\n篩選條件為: > "+ price
                if float(getstock) > float(price):
                    content += "\n符合" + getstock + " > " + price + "的篩選條件"
                    line_bot_api.push_message(userID, TextSendMessage(text=content))
            elif condition == "=":
                content += "\n篩選條件為: = "+ price
                if float(getstock) == float(price):
                    content += "\n符合" + getstock + " = " + price + "的篩選條件"
                    line_bot_api.push_message(userID, TextSendMessage(text=content))
        # look_stock_price(stock='2002', condition='>', price=31)
        def job():
            print('HH')
            dataList = cache_users_stock()
            # print(dataList)
            for i in range(len(dataList)):
                for k in range(len(dataList[i])):
                    # print(dataList[i][k])
                    look_stock_price(dataList[i][k]['favorite_stock'], dataList[i][k]['condition'], dataList[i][k]['price'], dataList[i][k]['userID'])
                    # look_stock_price(stock='2002', condition='>', price=31)
        schedule.every(30).seconds.do(job).tag('daily-tasks-stock'+uid,'second') #每10秒執行一次
        #schedule.every().hour.do(job) #每小時執行一次
        #schedule.every().day.at("17:19").do(job) #每天9點30執行一次
        #schedule.every().monday.do(job) #每週一執行一次
        #schedule.every().wednesday.at("14:45").do(job) #每週三14點45執行一次
        # 無窮迴圈
        while True: 
            schedule.run_pending()
            time.sleep(1)
    ################################################匯率推播#######################################
    if re.match("匯率推播", msg):
        import schedule
        import time
        
        def look_currency_price(currency, condition, price, userID):
            print(userID)
            try:
                realtime_currency = (twder.now(currency))[4]
                currency_name = mongodb.currency_list[currency]
                content = currency_name + "當前即期賣出價格為: " + str(realtime_currency)
                if condition == '<':
                    content += "\n篩選條件為: < "+ price
                    if float(realtime_currency) < float(price):
                        content += "\n符合" + realtime_currency + " < " + price + "的篩選條件"
                        # line_bot_api.push_message(userID, TextSendMessage(text=content))
                elif condition == '>':
                    content += "\n篩選條件為: > "+ price
                    if float(realtime_currency) > float(price):
                        content += "\n符合" + realtime_currency + " > " + price + "的篩選條件"
                        # line_bot_api.push_message(userID, TextSendMessage(text=content))
                elif condition == "=":
                    content += "\n篩選條件為: = "+ price
                elif condition == "未設定":
                    content += "\n尚未設置篩選條件, 請設定您想要的目標價格條件,如: 新增外幣"+currency+">10"
                
                else:
                    content += "\n無法判定此外幣設定的篩選條件"
                line_bot_api.push_message(userID, TextSendMessage(text=content))
                print(content)  # 打印内容用于调试
            except Exception as e:
                print(f"Error checking currency: {e}")
        print(cache_users_currency())
        # def job_currency():
        #     print('HH')
        #     dataList = cache_users_currency()
        #     print(dataList)
        #     for i in range(len(dataList)):
        #         for k in range(len(dataList[i])):
        #             look_currency_price(dataList[i][k]['favorite_currency'], dataList[i][k]['condition'], dataList[i][k]['price'], dataList[i][k]['userID'])
        def job_currency():
            print('Running currency check job')
            dataList = cache_users_currency()
            print(f"Data list: {dataList}")
            for user_data in dataList:
                for entry in user_data:
                    look_currency_price(entry['favorite_currency'], entry['condition'], entry['price'], entry['userID'])           
        schedule.every(30).seconds.do(job_currency) #每10秒執行一次
        #schedule.every(30).seconds.do(job_currency) #每10秒執行一次
        #schedule.every().hour.do(job) #每小時執行一次
        #schedule.every().day.at("20:00").do(job) #每天9點30執行一次
        #schedule.every().monday.do(job) #每週一執行一次
        #schedule.every().wednesday.at("14:45").do(job) #每週三14點45執行一次
        # 無窮迴圈
        while True: 
            schedule.run_pending()
            time.sleep(1)

    #*******************************雷達回波********************************#

    if re.match('衛星雲圖',msg):
        url = 'https://www.cwa.gov.tw/Data/radar/CV1_3600.png'
        radar_img = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(event.reply_token,radar_img)

    #*******************************雷達回波********************************#
    #冬水*****水*****水****weather**冰水冰*水*水*水水水*水冬水冰井＃固文遐單
    # 第一層-最新氣象->4格圖片Flex Messag
    if re.match('最新氣象|查詢天氣|天氣查詢|天氣|weather',msg):
        content= place.img_Carousel() #呼叫4格圖片Flex Message
        line_bot_api.reply_message(event.reply_token, content)
        return 0
    ##########井#######并####1。园归夺天天条-OK#井##井###井##井##井##游##井林## 
    # 1.第二層-即時天氣->呼叫quick_reply
    if re.match('即時天氣|即時氣象',msg):
        mat_d[uid] = '即時天氣'
        content = place.quick_reply_weather(mat_d[uid])
        line_bot_api.reply_message(event.reply_token, content)
    return 0


@handler.add(MessageEvent,message= ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message,id)
    imge = Image.open(io.BytesIO(message_content.content))

    image = preprocess_image(image)

    prediction = model.predict(image)
    digit = np.argmax(prediction)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f'預測的數字是:{digit}')
    )

import os
if __name__ == "__main__":
    app.run()

#https://opendata.cwb.gov.tw/index
#CWA-C07BDC7E-7138-4068-BCEC-13C15865812A