from twilio.rest import Client
from flask import Flask, request, redirect
from datetime import datetime
from twilio.twiml.messaging_response import Message, MessagingResponse
import os, redis, json, sys, pickle

account_sid = 'AC789b798bde070df6992f4f0fba84e89a'
auth_token = '54c50792327d057f2847007947f11cc3'
client = Client(account_sid, auth_token)
db=redis.from_url(os.environ['REDIS_URL'])

app = Flask(__name__)
        
@app.route('/')
def homepage():
    return app.send_static_file('/index.html')

@app.route('/getNum/<area>')
def findAndCreateNum(area):
        account_sid = 'AC789b798bde070df6992f4f0fba84e89a'
        auth_token = '54c50792327d057f2847007947f11cc3'
        client = Client(account_sid, auth_token)
        numbers = client.available_phone_numbers("US").local.list(area_code= area)
        number = client.incoming_phone_numbers().create(phone_number=numbers[0].phone_number).update(sms_url = "https://testprojectdial.herokuapp.com/sms")
        print(number.friendly_name)
        return number

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    text = request.values.get('Body', None)
    fromNum = request.values.get('From', None)
    queueNum = request.values.get('To', None)
    handleMsg(fromNum, queueNum, text)
    return str("<Response></Response>")

#pairs data structure

userChannels = {}
pickle.dump( userChannels, open( "saveChannel.p", "wb" ) )

pairs = {}
pickle.dump( pairs, open( "savePair.p", "wb" ) )

def setPair(num1, num2):
    pairs = pickle.load( open( "savePair.p", "rb" ) ) 
    pairs[num1] = num2
    pairs[num2] = num1
    pickle.dump( pairs, open( "savePair.p", "wb" ) )
    return

def getPair(num):
    pairs = pickle.load( open( "savePair.p", "rb" ) )
    result = pairs[num]
    return result

def deletePair(num):
    pairs = pickle.load( open( "savePair.p", "rb" ) )
    num2 = pairs[num]
    pairs.pop(num)
    pairs.pop(num2)
    pickle.dump( pairs, open( "savePair.p", "wb" ) )
    return
        
#queues data structure and handling
queues = {}
pickle.dump( queues, open( "save.p", "wb" ) )
queueInfo = json.dumps({})
db.set('queueInfo', queueInfo)

queueInfo = db.get('queueInfo')

def getAllQueues():
    return queueInfo

def createQueue(number, topic, description):
    queues = pickle.load( open( "save.p", "rb" ) ) 
    queues[number] = []
    pickle.dump( queues, open( "save.p", "wb" ) )
    queueInfo = db.get('queueInfo')
    queueInfo = json.loads(queueInfo)
    queueInfo[number] = {"topic":topic, "description":description, "number" : number}
    qI = json.dumps(queueInfo)
    db.set('queueInfo', qI)
    return

def deleteQueue(number):
    queues = pickle.load( open( "save.p", "rb" ) )
    queues.pop(number)
    pickle.dump( queues, open( "save.p", "wb" ) )    
    return

def addUserToQueue(userNumber, queueNumber):
    userChannels = pickle.load( open( "saveChannel.p", "rb" ) )
    userChannels[userNumber] = queueNumber
    queues = pickle.load( open( "save.p", "rb" ) )
    queues[queueNumber].append(userNumber)
    pickle.dump( queues, open( "save.p", "wb" ) ) 
    pickle.dump( userChannels, open( "saveChannel.p", "wb" ) ) 
    print("added" + userNumber, file=sys.stderr)
    return

def removeUserFromQueue(userNumber, queueNumber, queues):
        print("removing" + userNumber, file=sys.stderr)
        print(queues, file=sys.stderr)
        qlist = queues[queueNumber]
        print(qlist, file=sys.stderr)
        qlist.remove(userNumber)
        print("removed" + userNumber, file=sys.stderr)
        print(queues, file=sys.stderr)
        pickle.dump( queues, open( "save.p", "wb" ) )
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
    userChannels = pickle.load( open( "saveChannel.p", "rb" ) )

    queues = pickle.load( open( "save.p", "rb" ) )

    createQueue("+13012347438", "Test", "Test Channel")
        
    app.logger.info(queueNumber)
    queueNumber = queueNumber[:]
    
    print("inside handler", file=sys.stderr)
    print(queues, file=sys.stderr)

    if text == "STOP":
        removeUserFromQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Thank you for using our service. See you again!", queueNumber)
        return
    elif text == "SWITCH":
        addUserToQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Please wait to be paired again.", queueNumber)
        sendMsg(getPair(userNumber), "The user has disconnected. Please wait to be paired again.", queueNumber)
        return
    elif userNumber in userChannels.keys():
        relayMsg(userNumber, text, queueNumber)
        return
   
    elif len(queues) == 0:
        print("elif", file=sys.stderr)
        queues = pickle.load( open( "save.p", "rb" ) )
        print(queues, file=sys.stderr)
        
        addUserToQueue(userNumber, queueNumber)
        sendMsg(userNumber, "Please wait to be paired with another user. Reply STOP to opt out of the service.", queueNumber)
        return
    else:
        print("else", file=sys.stderr)
        print(queues, file=sys.stderr)
        pairedUser = queues[queueNumber][0]
        removeUserFromQueue(pairedUser, queueNumber, queues)
        setPair(userNumber, pairedUser)
        sendMsg(pairedUser, "You have been paired, startb talking, or text SWITCH to switch to a new person or STOP to opt out of the service.", queueNumber)
        
if __name__ == '__main__':
    print("running")
    app.run(debug=True, use_reloader=True)
        
   
