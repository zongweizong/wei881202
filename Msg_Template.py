from linebot.models import *
def stock_reply_rate():
    content_text = "想知道匯率嗎？嘿嘿"
    text_message = TextSendMessage(
                                text = content_text ,
                                quick_reply=QuickReply(
                                   items=[
                                       QuickReplyButton(
                                                action=MessageAction(
                                                    label="💜查詢幣別💜", 
                                                    text="幣別種類",
                                                )
                                       ),
                                       QuickReplyButton(
                                           action = MessageAction(
                                               label="💜查詢幣別匯率💜",
                                               text="查詢匯率",
                                                )
                                       ),
                                       QuickReplyButton(
                                           action = MessageAction(
                                               label="💜💜關注的匯率",
                                               text="我的外幣",
                                                )
                                       ),
                                ]
                            ))
    return text_message

def stock_reply_other():
    content_text = "分析趨勢圖"
    text_message = TextSendMessage(
                                text = content_text ,
                                quick_reply=QuickReply(
                                   items=[
                                       QuickReplyButton(
                                                action=MessageAction(
                                                    label="💜即時股價報你災💜", 
                                                    text="股價查詢->#2330",
                                                )
                                       ),
                                       QuickReplyButton(
                                           action = MessageAction(
                                               label="💜匯率圖💜",
                                               text="CT幣別->CTUSD",
                                                )
                                       ),
                                       QuickReplyButton(
                                           action = MessageAction(
                                               label="💜股價Ｋ線圖💜",
                                               text="@k股價代號日期區間->@k23302024-01-01",
                                                )
                                       ),
                                ]
                            ))
    return text_message
#測試的button
def show_Button():
    flex_message = FlexSendMessage(
            alt_text="show",
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://i.imgur.com/yOCnuHO.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                    "type": "uri",
                    "uri": "https://line.me/"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "💰請點選你要查看的外幣💰"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "美金",
                            "text": "USD"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "日幣",
                            "text": "JPY"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "韓元",
                            "text": "KRW"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "人民幣",
                            "text": "CNY"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "text": "HKD",
                            "label": "港幣"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "泰銖",
                            "text": "THB"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        }
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "英鎊",
                            "text": "GBP"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "澳幣",
                            "text": "AUD"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "新加坡",
                            "text": "SGD"
                            },
                            "style": "secondary",
                            "color": "#F7B5CA"
                        }
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    }
                    ]
                },
                "styles": {
                    "body": {
                    "backgroundColor": "#FFEBD4"
                    }
                }
                }
    )
    return flex_message


def realtime_currency_other(currency):
    content = "想要看更多嗎，嘿嘿?"
    text_message = TextSendMessage(
                                text = content ,
                               quick_reply=QuickReply(
                                   items=[
                                       QuickReplyButton(
                                                action=MessageAction(
                                                    label="即時匯率", 
                                                    text="外幣"+currency,
                                                )
                                       ),
                                       QuickReplyButton(
                                                action=MessageAction(
                                                    label="加入清單", 
                                                    text="新增外幣"+currency,
                                                )
                                       ),
                                        QuickReplyButton(
                                                action=MessageAction(
                                                    label="走勢圖", 
                                                    text="CT"+currency,
                                                )
                                       ),
                                        QuickReplyButton(
                                                action=MessageAction(
                                                    label="新聞", 
                                                    text="N外匯"+currency,
                                                )
                                       )
                                ]
                            ))
    return text_message