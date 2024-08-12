from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import re , requests , datetime , twstock , Msg_Template , mongodb , EXRate 
from bs4 import BeautifulSoup

from line_bot import *
app = Flask(__name__)


#抓使用者他關注的股票

def cache_users_stock():
    db =mongodb.constructor_stock()
    nameList = db.list_collection_names()
    users = []
    for i in range(len(nameList)):
        collect = db[nameList[i]]
        cel = list(collect.find({'tag':'stock'}))
        users.append(len)
    return users

#油價查詢
def oil_price():
    target_url = 'https://gas.goodlife.tw/'
    rs = requests.session()
    res = rs.get(target_url,verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text,'html.parser')
    title = soup.select('#main')[0].text.replace('\n', '').split('(')[0]
    gas_price = soup.select('#gas-price')[0].text.replace('\n\n\n','').replace(' ','')
    cpc = soup.select('#cpc')[0].text.replace(' ','')
    content = '{}\n{}{}'.format(title,gas_price,cpc)
    return content
def push_msg(event,msg):
    try:
        user_id = event.source.user_id
        line_bot_api.push_message(user_id,TextSendMessage(text=msg))
    except:
        room_id = event.source.user_id
        line_bot_api.push_message(room_id,TextSendMessage(text=msg))

def usage(event):
    push_msg(event,"   ★ ★  查詢方法  ★ ★   \
             \n\
             \n⊕本機器人可查詢油價及匯率⊕\
             \n\
             \n◎ 油價通知 →→→→ 輸入查詢油價\
             \n◎ 匯率通知 →→→→ 輸入查詢匯率\
             \n◎ 匯率兌換 →→→→ 換匯USD/TWD")
    
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    #    line_bot_api.reply_message(
    #        event.reply_token,
    #        TextSendMessage(text=event.message.text))
    msg = str(event.message.text).upper().strip()
    profile = line_bot_api.get_profile(event.source.user_id)

    userpeak=str(event.message.text) #使用者講的話
    uid = profile.user_id
    user_name = profile.display_name #使用者名稱 

    ##############################目錄區##############################
    if event.message.text == "油價查詢":
        content = oil_price()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "使用說明":
        usage(event)
    if event.message.text =="開始玩":
        message = TemplateSendMessage(
            alt_text='目錄 template',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/bGyGdb1.jpg',
                        title='選擇服務',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='開始玩',
                                text='開始玩'
                            ),
                            URIAction(
                                label='股價查詢',
                                uri='https://tw.stock.yahoo.com/news/'
                            ),
                            URIAction(
                                label='粉絲團',
                                uri='https://zh-tw.facebook.com/lccnet10/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/bGyGdb1.jpg',
                        title='選擇服務',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='開始玩',
                                text='開始玩'
                            ),
                            URIAction(
                                label='財經新聞',
                                uri='https://tw.stock.yahoo.com/news/'
                            ),
                            URIAction(
                                label='粉絲團',
                                uri='https://zh-tw.facebook.com/lccnet10/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/bGyGdb1.jpg',
                        title='選擇服務',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='開始玩',
                                text='開始玩'
                            ),
                            URIAction(
                                label='財經新聞',
                                uri='https://tw.stock.yahoo.com/news/'
                            ),
                            URIAction(
                                label='粉絲團',
                                uri='https://zh-tw.facebook.com/lccnet10/'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,message)
    ################################股票區################################
    if event.message.text == "股價查詢":
        line_bot_api.push_message(uid,TextSendMessage("請輸入 #股票代號....."))

     ################################股票提醒################################

    if re.match('關閉提醒',msg):
        import schedule
        schedule.clear()
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
        schedule.every(10).seconds.do(job).tag('daily-tasks-stock'+uid,'second') #每10秒執行一次
        #schedule.every().hour.do(job) #每小時執行一次
        #schedule.every().day.at("17:19").do(job) #每天9點30執行一次
        #schedule.every().monday.do(job) #每週一執行一次
        #schedule.every().wednesday.at("14:45").do(job) #每週三14點45執行一次
        # 無窮迴圈
        while True: 
            schedule.run_pending()
            time.sleep(1)
            
    #新增使用者關注的股票到mongodb EX:關注2330>XXX
    if re.match('關注[0-9]{4}[<>][0-9]' ,msg):
        stockNumber = msg[2:6]
        content = mongodb.write_my_stock(uid ,user_name ,stockNumber ,msg[6:7] ,msg[7:])
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 
    #查詢股票篩選條件清單
    if re.match('股票清單',msg):
        line_bot_api.push_message(uid,TextSendMessage('稍等一下, 股票查詢中...'))
        content = mongodb.show_stock_setting(user_name,uid)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 
    #刪除存在資料庫裡面的股票
    if re.match('刪除[0-9]{4}',msg):
        content = mongodb.delete_my_stock(user_name,msg[2:])
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0
    #清空存在資料庫裡面的股票
    if re.match('清空股票',msg):
        content = mongodb.delete_my_allstock(user_name,uid)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 
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
        content += '現價: %s \n'%(
            stock_rt['realtime']['latest_trade_price'])
        content += '開盤: %s \n'%(  
            stock_rt['realtime']['open'])
        content += '最高: %s\n'%(
            stock_rt['realtime']['high'])
        content += '最低: %s\n'%(    
            stock_rt['realtime']['low'])
        content += '量: %s\n' %(stock_rt['realtime']['accumulate_trade_volume'])

        stock = twstock.Stock(text)
        content += '------\n'
        content += '最近五日價格: \n'
        price5 = stock.price[-5:][::-1]
        date5 = stock.date[-5:][::-1]
        for i in range(len(price5)):
            content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d"),price5[i])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)
        )            

    #影片
    if re.match('理財相關',msg):
        message = Msg_Template.youtube_channel()
        line_bot_api.reply_message(event.reply_token,message)
    
    ################################匯率區################################
    if re.match('外幣及匯率',msg):
        message = Msg_Template.show_Button()
        line_bot_api.reply_message(event.reply_token,message)
    if re.match('[A-Z]{3}',msg):
        currency_name = EXRate.getCurrencyName(msg)
        if currency_name == "無可支援的外幣": content = "無可支援的外幣"
        else:
            line_bot_api.push_message(uid,TextSendMessage("正在為您計算外幣....."))
            content = EXRate.showCurrency(msg)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0
    if re.match("匯率查詢",msg):
        btn_msg = Msg_Template.stock_reply_rate()
        line_bot_api.push_message(uid, btn_msg)
        return 0 
    if re.match("換匯[A-Z]{3}/[A-Z]{3}/[0-9]",msg):
        line_bot_api.push_message(uid,TextSendMessage("將為您做外匯計算....."))
        content = EXRate.getExchangeRate(msg)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 
    if re.match('新增外幣[A-Z]{3}',msg):
        currency = msg[4:7]
        currency_name = EXRate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣": content = "無可支援的外幣"
        elif re.match('新增外幣[A-Z]{3}[<>][0-9]',msg):
            content = mongodb.write_my_currency(uid,user_name,currency,msg[7:8],msg[8:])
        else:
            content = mongodb.write_my_currency(uid,user_name,currency,"未設定","未設定")
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0
    if re.match('我的外幣',msg):
        line_bot_api.push_message(uid,TextSendMessage('稍等一下,匯率查詢中...'))
        content = mongodb.show_my_currency(uid,user_name)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 
    if re.match('刪除外幣[A-Z]{3}',msg):
        content = mongodb.delete_my_currency(user_name,msg[4:7])
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0
    if re.match('清空外幣',msg):
        content = mongodb.delete_my_currency(user_name,uid)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 

@handler.add(FollowEvent)
def handler_follow(event):
    welcome_msg = """Hello! 您好，歡迎您成為 Master 財經小幫手 的好友!
    
我是Master 財經小幫手

-這裡有股票，匯率資訊哦
-直接點選下方【圖中】選單功能

-期待您的光臨!"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg)
    )
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print(event)
if __name__ == "__main__":
    app.run(port=8082)