#!/usr/bin/env python3

import WatsonAssistantV2Utility
import tkinter as tk
import os


__author__ = 'Peter Maar'
__version__ = '0.3.0'

DEBUG = False
STEAM_LIBRARY_PATH = "D:\\Steam"

VERSION = '2019-01-11'

steam_location = os.path.normpath(STEAM_LIBRARY_PATH + "/steamapps/common/OneShot/")
if os.path.isdir(steam_location):
    faces_location = os.path.normpath(steam_location + "/Graphics/Faces")

print(steam_location)

api_path = os.path.normpath('ID/API_KEY.txt')
assistant_path = os.path.normpath('ID/ASSISTANT_ID.txt')
API_KEY = open(api_path).read()
ASSISTANT_ID = open(assistant_path).read()

userInp = ''  # Sending empty string will give back the welcome message, so initialize it to that
contextVar = None  # Initialize for scope

# Create assistant object
assistant = WatsonAssistantV2Utility.WatsonAssistant(VERSION, API_KEY, ASSISTANT_ID)
print("Connected. Send exit to disconnect at any time.")


""" GUI things """


def clean_exit():
    assistant.disconnect()
    exit(0)


def send():
    None


root = tk.Tk()

# Get screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
if screen_height < screen_width:
    screen_size = screen_height
else:
    screen_size = screen_width

# Determine main canvas size
mainSize = 2 * screen_size // 3

# Canvases
userCanvas = tk.Canvas(root)  # Buttons and user input
nikoCanvas = tk.Canvas(root, height=0.25*mainSize, width=mainSize)  # Response and Niko's face

user_input_field = tk.Entry(root)
user_input_field.pack()

# Send Button
sendButton = tk.Button(userCanvas, text="Send", command=send)
sendButton.pack(side=tk.LEFT)

# Exit Button
exitButton = tk.Button(userCanvas, text="Quit", command=clean_exit)
exitButton.pack(side=tk.RIGHT)


# Pack canvases
userCanvas.pack()
nikoCanvas.pack()

root.mainloop()








# Text Main Loop
while userInp.lower() != 'exit':

    lines = assistant.message(userInp)

    WatsonAssistantV2Utility.display_response(lines)

    if DEBUG:
        print("------------------")

    if userInp.lower().find("bye") != -1:
        print("To disconnect, enter 'exit' (no quotes) at any time.", end="")

    userInp = input("\n>> ")

assistant.disconnect()
