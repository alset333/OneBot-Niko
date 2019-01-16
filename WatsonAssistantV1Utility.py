import watson_developer_cloud.assistant_v1 as av1
from time import sleep

DEBUG = False


def display_response(response_lines):
    """ Displays the lines of the response """

    for line in response_lines:
        rt = line["response_type"]

        # Bot gave text, so show it
        if rt == "text":
            print(line['text'])

        # Bot 'typing' or waiting, so wait for a moment
        elif rt == "pause":
            if line['typing']:
                print('User is typing...')

            # Sleep for typing duration (or just print it if debugging mode)
            seconds = line['time'] / 1000  # Convert from ms to s
            if DEBUG:
                print(seconds, "second sleep")
            else:
                sleep(seconds)

        elif rt == "option":
            print(line['title'])
            for o in line['options']:
                print(o['label'], ": ", o['value']['input']['text'], sep="")

        # Short pause between anything, even if no 'typing' (unless debugging mode)
        if not DEBUG:
            sleep(1)

        print()  # Newline


class WatsonAssistant:
    contextVar = None  # Initialize for scope

    def __init__(self, version, api_key, workspace_id):
        # Create assistant object
        self.assistant = av1.AssistantV1(
            version=version,
            iam_apikey=api_key,
            url='https://gateway-wdc.watsonplatform.net/assistant/api'
        )

        self.workspace_id = workspace_id


    def connect(self):
        print("Connect.")
        None

    def disconnect(self):
        print("Disconnect.")
        None

    def message(self, sendText):

        if sendText.lower() == 'exit':
            self.disconnect()

        # Create InputData object for text to send
        userInpData = av1.InputData(sendText)

        # Send our message and store it all to 'message'
        message = self.assistant.message(
            workspace_id=self.workspace_id,
            input=userInpData,
            context=self.contextVar
        )

        # Get/isolate and store the response to the message
        response = message.result

        # Get the context variable
        self.contextVar = response['context']

        # Get just the array of the different lines (text, pause, etc)
        lines = response["output"]["generic"]

        if DEBUG:
            print("------------------")
            print(message)
            print("------------------")
            print(response)
            print("------------------")

        return lines
