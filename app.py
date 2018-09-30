from twilio.rest import Client
from flask import Flask
from datetime import datetime
from twilio.twiml.messaging_response import Message, MessagingResponse

account_sid = 'AC789b798bde070df6992f4f0fba84e89a'
auth_token = '54c50792327d057f2847007947f11cc3'
client = Client(account_sid, auth_token)

app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body:
        resp.message(body)
        
    return str(resp)


def sms_send():
    """Send messages to users."""
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body = "This is a test.",
        from_ = "+13012347438",
        to = "+17035012119"
    )
    print(message.sid)
        
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
