from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
from PyPDF2 import PdfFileReader
from docx import Document

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
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(event.message.file_name, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    if event.message.file_name.endswith('.pdf'):
        text = get_text_from_pdf(event.message.file_name)
    elif event.message.file_name.endswith('.docx'):
        text = get_text_from_docx(event.message.file_name)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='File received!'))
    
def get_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfFileReader(file)
        for page_num in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page_num).extract_text()
    return text

def get_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
