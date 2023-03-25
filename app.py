from flask import Flask
import openai
import json

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/dynamic-chatbot')
def dynamic_chatbot():

    openAiFile = open('openaiauth.json')
    openai.api_key =  json.load(openAiFile)["key"]
    openAiFile.close()

    botPerson = "Joe Biden"

    chatMessages = [{"role": "system", "content": f"You are {botPerson}. You should respond to all messages in the speaking style of {botPerson}"}]

    userInput = input("Enter a message to send: ")
    chatMessages.append({"role": "user", "content": userInput})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chatMessages
    )

    print("Response: " + response['choices'][0]['message']['content'])


if __name__ == '__main__':
    app.run()
