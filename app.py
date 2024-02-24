from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import requests
import json

app = Flask(__name__)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)               # 印出 json_data

    headers = {'Authorization':'Bearer {channel_access_token}','Content-Type':'application/json'}
    body = {
        'replyToken':events.replyToken,
        'messages':[{
                'type': 'text',
                'text': '文件上傳成功!'
            }]
    }
    req = requests.request('POST', 'https://api.line.me/v2/bot/message/reply', headers=headers,data=json.dumps(body).encode('utf-8'))
    print(req.text)
    return 'OK'

"""
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    url = 'https://api-data.line.me/v2/bot/message/{event.message.id}/content'
    headers = {
        'Authorization': 'Bearer {channel access token}'
    }
    
    response = requests.get(url, headers=headers)
    print(response.status_code) #可以檢查回應狀態碼
    print(response.content) #可以取得回應內容
    
    

    #message_content = line_bot_api.get_message_content(event.message.id)
    #print(message_content)
    #if not os.path.exists("uploads"):
    #    os.makedirs("uploads")
    #with open(f"uploads/{event.message.id}.pdf", "wb") as file:
    #    for chunk in message_content.iter_content():
    #        file.write(chunk)
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text="File uploaded successfully."))

import os
"""
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
