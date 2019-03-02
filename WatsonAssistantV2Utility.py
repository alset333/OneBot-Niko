#!/usr/bin/env python3

"""
A Watson-Assistant Utility/Interface for the API v2.
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

from watson_developer_cloud import AssistantV2, assistant_v2
from time import sleep

DEBUG = True

# 0 Dallas, 1 Washington DC, 2 Frankfurt, 3 Sydney, 4 Tokyo, 5 London
LOCATION_NUMBER = 1

url_locations = ["", "-wdc", "-fra", "-syd", "-tok", "-lon"]
url_location = url_locations[LOCATION_NUMBER]


def timed_print(text):
    for char in text:
        print(char, end='')
        if not DEBUG:
            sleep(0.01)


def display_response(response_lines):
    """ Displays the lines of the response """

    for line in response_lines:
        rt = line["response_type"]

        # Bot gave text, so show it
        if rt == "text":
            timed_print(line['text'])

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
            sleep(0.1)

        print()  # Newline


class WatsonAssistant:
    def __init__(self, version, api_key, assistant_id):
        self.assistant_id = assistant_id

        # Create assistant object
        self.assistant = AssistantV2(
            version=version,
            iam_apikey=api_key,
            url='https://gateway' + url_location + '.watsonplatform.net/assistant/api'
        )

        # Start a session
        self.session_id = self.assistant.create_session(
            assistant_id=self.assistant_id
        ).get_result()["session_id"]

    def disconnect(self):
        """
        End the session
        """
        self.assistant.delete_session(self.assistant_id, self.session_id)
        print("Disconnected")

    def message(self, text, context):
        """
        Send a message from the user to the assistant, and get the response.

        :param text: The text to send.
        :param context: The context to send.
        :return: The assistant's response and the context
        """

        if text.lower() == 'exit':
            self.disconnect()
            return

        # Create InputData object for text to send
        opt = assistant_v2.MessageInputOptions(return_context=True)
        message_input = assistant_v2.MessageInput(text=text, options=opt)

        response = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=self.session_id,
            input=message_input,
            context=context
        ).get_result()

        # Get just the array of the different lines (text, pause, etc)
        lines = response["output"]["generic"]

        # Get just the context dictionary
        context = response['context']

        if DEBUG:
            print("------------------")
            print(response)
            print("------------------")

        return lines, context
