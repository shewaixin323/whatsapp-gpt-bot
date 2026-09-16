import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")


@app.route("/", methods=["GET"])
def home():
    return "WhatsApp GPT Bot is running!", 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():

    data = request.get_json()

    print("收到消息:")
    print(data)

    try:
 message = data["entry"][0]["changes"][0]["value"]["messages"][0]

    from_number = message["from"]
    text = message["text"]["body"]

    print("用户:", from_number)
    print("内容:", text)

    print("准备回复用户")

    send_message(
        from_number,
        "收到你的消息：" + text
    )

    except Exception as e:
        print("错误:", e)

    return "EVENT_RECEIVED", 200



def send_message(to, text):

    url = f"https://graph.facebook.com/v26.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("发送结果:")
    print(response.text)



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
