from twilio.rest import Client
from flask import Flask, request, redirect
from datetime import datetime
from twilio.twiml.messaging_response import Message, MessagingResponse
import os, redis, json, sys

account_sid = 'AC789b798bde070df6992f4f0fba84e89a'
auth_token = '54c50792327d057f2847007947f11cc3'
client = Client(account_sid, auth_token)
db=redis.from_url(os.environ['REDIS_URL'])

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
    return str("<Response></Response>")

#pairs data structure

userChannels = db.get('userChannels') or {}

pairs = db.get('pairs') or {}

def setPair(num1, num2):
    pairs[num1] = num2
    pairs[num2] = num1
    db.set('pairs', pairs)
    return

def getPair(num):
    result = pairs[num]
    db.set('pairs', pairs)
    return result

def deletePair(num):
    num2 = pairs[num]
    pairs.pop(num)
    pairs.pop(num2)
    db.set('pairs', pairs)
    return

#queues data structure and handling
queues = json.dumps({})
db.set('queues', queues)
                
queues = db.get('queues')

queueInfo = json.dumps({})
db.set('queueInfo', queueInfo)
                
queueInfo = db.get('queueInfo')

def getAllQueues():
    return queueInfo

def createQueue(number, topic, description):
    queues = db.get('queues')
    queues = json.loads(queues)
    queues[number] = list()
    queues = json.dumps(queues)
    db.set('queues', queues)
    queueInfo = db.get('queueInfo')
    queueInfo = json.loads(queueInfo)
    queueInfo[number] = {"topic":topic, "description":description, "number" : number}
    qI = json.dumps(queueInfo)
    db.set('queueInfo', qI)
    return

def deleteQueue(number):
    queues.pop(number)
    db.set('queues', queues)
    return

def addUserToQueue(userNumber, queueNumber):
    userChannels[userNumber] = queueNumber
    queues[queueNumber].append(userNumber)
    db.set('queues', queues)        
    return

def removeUserFromQueue(userNumber, queueNumber):
    queues[queueNumber].remove(userNumber)
    db.set('queues', queues)
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
    app.logger.info("Msg recd" + text + " " + userNumber)
    queue = db.get('queues')
    queue = json.loads(queues)

    createQueue("+13012347438", "Test", "Test Channel")
        
    app.logger.info(queueNumber)
    app.logger.info(queue)
    queueNumber = queueNumber[:]

    if text == "STOP":
        removeUserFromQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Thank you for using our service. See you again!", queueNumber)
        return
    elif text == "SWITCH":
        addUserToQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Please wait to be paired again.", queueNumber)
        sendMsg(getPair(userNumber), "The user has disconnected. Please wait to be paired again.", queueNumber)
        return
    elif userNumber in userChannels:
        relayMsg(userNumber, text, queueNumber)
        return
   
    elif queue is None:
        #todo bug probably
        addUserToQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Please wait to be paired with another user. Reply STOP to opt out of the service.", queueNumber)
        return
    else:
        app.logger.info("else")
        app.logger.info(queue)
        print('Hello world!', file=sys.stderr)
        print(queue, file=sys.stderr)
        pairedUser = queue[queueNumber][0]
        removeUserFromQueue[pairedUser]
        setPair(userNumber, pairedUser)
        sendMsg(pairedUser, "You have been paired, text SWITCH to switch to a new person or STOP to opt out of the service.", queueNumber)
        sendMsg(pairedUser, text, queueNumber)
        
if __name__ == '__main__':
    print("running")
    app.run(debug=True, use_reloader=True)
        
   
