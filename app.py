from flask import Flask, request
import openai
import json
import mysql.connector
from twilio.rest import Client

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/dynamic-chatbot', methods=['GET', 'POST'])
def dynamic_chatbot():

    #get from phone number
    fromNumFile = open('phonenumbers.json')
    fromNumber = json.load(fromNumFile)["from"]
    fromNumFile.close()

    # get twilio auth info, prep twilio client
    twilioFile = open('twilioauth.json')
    twilioInfo = json.load(twilioFile)
    twilioFile.close()
    twilioClient = Client(twilioInfo["accountSid"], twilioInfo["authToken"])

    # get openai auth info
    openAiFile = open('openaiauth.json')
    openai.api_key =  json.load(openAiFile)["key"]
    openAiFile.close()

    # get db config and auth info
    dbInfoFile = open('db.json')
    dbInfo = json.load(dbInfoFile)
    dbInfoFile.close()

    #create db connection and cursor
    dbConn = mysql.connector.connect(
        host=dbInfo['address'],
        user=dbInfo['user'],
        password=dbInfo['password']
    )
    dbCursor = dbConn.cursor()

    phoneNumber = request.values.get('From', None)
    userInput = request.values.get('Body', None)

    getQuery = f"SELECT * FROM rejection.chatbot_settings where phoneNumber = '{phoneNumber}'"
    dbCursor.execute(getQuery)

    getResult = dbCursor.fetchone()
    botPerson = "Donald Trump"
    if getResult == None:
        createQuery = "INSERT INTO rejection.chatbot_settings (phoneNumber, chatPerson) VALUES (%s, %s)"
        dbCursor.execute(createQuery, (phoneNumber, botPerson))
        dbConn.commit()
    else:
        botPerson = getResult[2]
    chatMessages = [{"role": "system", "content": f"You are {botPerson}. You should respond to all messages in the speaking style of {botPerson}"}]

    # Check for command
    if userInput[0:1] == "#":
        if userInput[1:].split()[0] == "changeperson":
            botPerson = ' '.join(userInput.split()[1:])
            updateQuery = f"UPDATE rejection.chatbot_settings SET chatPerson = '{botPerson}' where phoneNumber = {phoneNumber}"
            dbCursor.execute(updateQuery)
            dbConn.commit()

            # text user confirmation
            confirmMsg = twilioClient.messages.create(
                body=f"Your chatbot person was successfully changed to {botPerson}",
                from_=fromNumber,
                to=phoneNumber
            )


    else:
        chatMessages.append({"role": "user", "content": userInput})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chatMessages
        )
        chatMessages.append({"role": response['choices'][0]['message']['role'], "content": response['choices'][0]['message']['content']})

        responseMsg = twilioClient.messages.create(
                body=response['choices'][0]['message']['content'],
                from_=fromNumber,
                to=phoneNumber
            )
    return "yeet"
        


if __name__ == '__main__':
    app.run()
