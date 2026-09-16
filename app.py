import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

print("VERIFY_TOKEN:", VERIFY_TOKEN)
print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)


@app.route("/", methods=["GET"])
def home():
    return "WhatsApp GPT Bot is running!", 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("Webhook verify:")
    print(mode, token, challenge)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified")
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():

    data = request.get_json()

    print("====================")
    print("收到 WhatsApp webhook")
    print(data)
    print("====================")

    try:

        value = data["entry"][0]["changes"][0]["value"]

        # 过滤状态通知
        if "messages" not in value:
            print("不是用户消息，跳过")
            return "EVENT_RECEIVED", 200


        message = value["messages"][0]

        from_number = message["from"]

        text = ""

        if message["type"] == "text":
            text = message["text"]["body"]
        else:
            text = "收到非文字消息"


        print("用户号码:", from_number)
        print("用户内容:", text)


        reply = "收到你的消息：" + text

        print("准备发送回复:")
        print(reply)


        send_message(
            from_number,
            reply
        )


    except Exception as e:

        print("====================")
        print("处理错误:")
        print(type(e))
        print(e)
        print("====================")


    return "EVENT_RECEIVED", 200



def send_message(to, text):

    url = (
        f"https://graph.facebook.com/v26.0/"
        f"{PHONE_NUMBER_ID}/messages"
    )


    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {

        "messaging_product": "whatsapp",

        "to": to,

        "type": "text",

        "text": {
            "body": text
        }
    }


    print("发送 WhatsApp API:")
    print(payload)


    response = requests.post(
        url,
        headers=headers,
        json=payload
    )


    print("Meta返回状态:")
    print(response.status_code)

    print("Meta返回内容:")
    print(response.text)



if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
