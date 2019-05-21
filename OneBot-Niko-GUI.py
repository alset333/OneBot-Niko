#!/usr/bin/env python3

"""
A Watson assistant GUI.
Copyright (C) 2019 Peter Maar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

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

api_path = os.path.normpath('ID/ASSISTANT_API_KEY.txt')
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
