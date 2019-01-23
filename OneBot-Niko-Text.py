#!/usr/bin/env python3

import WatsonAssistantV2Utility
import os

DEBUG = True

USER_NAME = 'Peter'

__author__ = 'Peter Maar'
__version__ = '0.2.0'

VERSION = '2019-01-05'

api_path = os.path.normpath('ID/API_KEY.txt')
assistant_path = os.path.normpath('ID/ASSISTANT_ID.txt')
API_KEY = str.rstrip(open(api_path).read())  # Load API Key from file, removing trailing whitespace
ASSISTANT_ID = str.rstrip(open(assistant_path).read())  # Load Assistant ID from file, removing trailing whitespace

userInp = ''  # Sending empty string will give back the welcome message, so initialize it to that
contextVar = {'skills': {'main skill': {'user_defined': {'person': USER_NAME}}}}

print("Connected. Send exit to disconnect at any time.")

assistant = WatsonAssistantV2Utility.WatsonAssistant(VERSION, API_KEY, ASSISTANT_ID)

# Main Loop
while userInp.lower() != 'exit':

    lines, contextVar = assistant.message(userInp, contextVar)

    WatsonAssistantV2Utility.display_response(lines)

    if DEBUG:
        print("------------------")
        print(contextVar)
        print("------------------")

    if userInp.lower().find("bye") != -1:
        print("To disconnect, enter 'exit' (no quotes) at any time.", end="")

    userInp = input("\n>> ")

assistant.disconnect()
