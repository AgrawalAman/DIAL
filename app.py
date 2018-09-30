from twilio.rest import Client
from flask import Flask, request, redirect
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
    text = request.values.get('Body', None)
    fromNum = request.values.get('From', None)
    queueNum = request.values.get('To', None)
    handleMsg(fromNum, queueNum, text)

#pairs data structure

userChannels={}

pairs = {}

def setPair(num1, num2):
    pairs[num1] = num2
    pairs[num2] = num1
    return

def getPair(num):
    result = pairs[num]
    return result

def deletePair(num):
    num2 = pairs[num]
    pairs.pop(num)
    pairs.pop(num2)
    return

#queues data structure and handling

queues = {}

queueInfo = {}

def getAllQueus():
    return queueInfo

def createQueue(number, topic, description):
    queues[number] = []
    queueInfo[number] = {"topic":topic, "description":description, "number" : number}
    return

def deleteQueue(number):
    queues.pop(number)
    return

def addUserToQueue(userNumber, queueNumber):
    userChannels[userNumber] = queueNumber
    queues[queueNumber].append(userNumber)
    return

def removeUserFromQueue(userNumber, queueNumber):
    queues[queueNumber].remove(userNumber)
    return

#relaying and handling stuff

def relayMsg(sender, text, queueNumber):
    receiver = getPair(sender)
    sendMsg(receiver, text, queueNumber)

def sendMsg(receiver, text, fromNum):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body = text,
        from_ = fromNum,
        to = receiver
    )


def handleMsg(userNumber, queueNumber, text):
        
    createQueue("+13012347438", "Test", "Test Channel")

    if text == "STOP":
        removeUserFromQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Thank you for using our service. See you again!", queueNumber)
        return
    elif text == "SWITCH":
        addUserToQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Please wait to be paired again.", queueNumber)
        sendMsg(getPair(userNumber), "The user has disconnected. Please wait to be paired again.", queueNumber)
    elif userNumber in userChannels:
        relayMsg(userNumber, text, queueNumber)
        return
    elif len(queues[queueNumber]) == 0:      
        addUserToQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Please wait to be paired with another user. Reply STOP to opt out of the service.", queueNumber)
        return
    else:
        pairedUser = queues[queueNumber][0]
        removeUserFromQueue[pairedUser]
        setPair(userNumber, pairedUser)
        sendMsg(pairedUser, "You have been paired, text SWITCH to switch to a new person or STOP to opt out of the service.", queueNumber)
        sendMsg(pairedUser, text, queueNumber)
        
if __name__ == '__main__':
    print("running")
    app.run(debug=True, use_reloader=True)
        
   
