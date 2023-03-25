from flask import Flask
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

    twilioFile = open('twilioAuth.json')
    twilioInfo = json.load(twilioFile)
    twilioFile.close()

    twilioClient = Client(twilioInfo["accountSid"], twilioInfo["authToken"])

    openAiFile = open('openaiauth.json')
    openai.api_key =  json.load(openAiFile)["key"]
    openAiFile.close()

    dbInfoFile = open('db.json')
    dbInfo = json.load(dbInfoFile)
    dbInfoFile.close()

    dbConn = mysql.connector.connect(
        host=dbInfo['address'],
        user=dbInfo['user'],
        password=dbInfo['password']
    )
    dbCursor = dbConn.cursor()

    phoneNumber = "+13135551234"

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

    userInput = input("Enter a message to send: ")

    # Check for command
    if userInput[0:1] == "#":
        if userInput[1:].split()[0] == "changeperson":
            botPerson = ' '.join(userInput.split()[1:])
            updateQuery = f"UPDATE rejection.chatbot_settings SET chatPerson = '{botPerson}' where phoneNumber = {phoneNumber}"
            dbCursor.execute(updateQuery)
            dbConn.commit()

    else:
        chatMessages.append({"role": "user", "content": userInput})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chatMessages
        )
        chatMessages.append({"role": response['choices'][0]['message']['role'], "content": response['choices'][0]['message']['content']})

        print("Response: " + response['choices'][0]['message']['content'])


if __name__ == '__main__':
    app.run()
