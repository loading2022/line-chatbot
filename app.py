from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

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
    user_input = event.message.text
    #user_input="你是一個克蘭詩美容產品專員，負責招待客人，你剛剛推薦型男保濕緊緻凝露這項產品給15-20歲男性無皺紋無黑斑的客人了解，繼續解決客人的疑問，也可以推薦不同的產品，但必須是克蘭詩的產品，回答內容在50字以內"
    if user_input:
        files_folder = 'data'

        text = ""
        for filename in os.listdir(files_folder):
            file_path = os.path.join(files_folder, filename)
            if filename.endswith('.pdf'):
                text += get_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                text += get_text_from_docx(file_path)
            elif filename.endswith('.doc'):
                output_path=os.path.splitext(file_path)[0] + "_output.docx"
                if not os.path.exists(output_path):
                    convert(file_path,output_path)
                    os.remove(file_path)
                text += get_text_from_docx(output_path)

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        docs = knowledge_base.similarity_search(user_input)

        llm = ChatOpenAI(
            model_name="gpt-4-1106-preview",
            temperature=0.4
        )

        chain = load_qa_chain(llm, chain_type="stuff")

        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=user_input)

        response = {'response': response}

        chat_history.append({'user': user_input, 'assistant': response['response']})
        print(response)
        #message = TextSendMessage(text=event.message.text)
        line_bot_api.reply_message(event.reply_token, response)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
