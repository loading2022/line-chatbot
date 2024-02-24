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

    try:
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']         # 取得 reply token
        text_message = TextSendMessage(text='文件上傳成功!')          # 設定回傳同樣的訊息
        line_bot_api.reply_message(tk,text_message)       # 回傳訊息
    except:
        print('error')
    return 'OK'

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    file_id=event.message.id
    url = f"https://api-data.line.me/v2/bot/message/{file_id}/content"
    headers = {
        'Authorization': f'Bearer {channel_access_token}'
    }
    """
    response = requests.get(url, headers=headers)
    print(response.status_code) #可以檢查回應狀態碼
    print(response.content) #可以取得回應內容
    """
    message_content = line_bot_api.get_message_content(event.message.id)
    print(message_content)
    response = requests.get(url, headers=headers)
    print(response.text)

    
    #for chunk in message_content.iter_content():
    #    print(chunk)
    #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=chunk))
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text="File uploaded successfully."))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
