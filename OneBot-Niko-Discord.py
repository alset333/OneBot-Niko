#!/usr/bin/env python3

"""
Links an IBM Watson-Assistant instance to Discord by running a bot using Discord.py Rewrite.
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

from discord.ext import commands
from discord import Game, Status
import os
import WatsonAssistantV2Utility
from time import sleep

VERSION = '2019-01-05'

api_path = os.path.normpath('ID/API_KEY.txt')
assistant_path = os.path.normpath('ID/ASSISTANT_ID.txt')
API_KEY = str.rstrip(open(api_path).read())  # Load API Key from file, removing trailing whitespace
ASSISTANT_ID = str.rstrip(open(assistant_path).read())  # Load Assistant ID from file, removing trailing whitespace


token_path = os.path.normpath('ID/DISCORD_BOT_TOKEN.txt')
token = str.rstrip(open(token_path).read())  # Load Token from file, removing trailing whitespace


description = '''Incredible bot using techniques from The World Machine to connect you to your Niko.
Coded from the ground up with simplified AI to avoid Squares.
It does not run a world simulation, and communication is not always stable, but it's a start.

Code written by Peter Maar (alset333)
https://github.com/alset333/OneBot-Niko'''
bot = commands.Bot(command_prefix='?', description=description)

# Note, the authors are matched to the bot even across servers.
# You can start a conversation in one and continue in another. Only one Niko per person!
assistants = {}  # A dictionary matching each "message.author" to their "assistant" as {author : assistant}
contexts = {}  # A dictionary matching each "message.author" to their "context" as {author : context}


@bot.event
async def on_ready():
    print('Niko has logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print("Available Emojis:", bot.emojis)
    print('------')

    game = Game("with friends!")
    await bot.change_presence(status=Status.online, activity=game)


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def ping(ctx):
    """Pong!"""

    # Ping method based on this, but modified for discord.py rewrite
    # https://stackoverflow.com/questions/46307035/ping-command-with-discord-py/52754269#52754269

    # When the command is received, send a message.
    t = await ctx.send('Calculating...')

    # Get difference in timestamps between command and our message
    ms = (t.created_at-ctx.message.created_at).total_seconds() * 1000

    # Edit our message to display the ping times
    answer = 'Pong!\nHeartbeat latency is {}ms,\nMessage took: {}ms'.format(int(bot.latency * 1000), int(ms))
    await t.edit(content=answer)


@bot.command()
async def logout(ctx):
    """Since PyCharm doesn't send/wait for Ctrl+C, use this to gracefully disconnect"""
    await bot.logout()


@bot.listen()
async def on_message(message):
    print(message)
    if message.author.bot:  # If the bot sent the message
        return  # Don't do anything with it

    if message.author in contexts:  # If they have a context
        print("they have a context")
        contextVar = contexts[message.author]  # Use their context
    else:
        contextVar = []  # Otherwise, use an empty one

    if message.author in assistants:  # If they already have an assistant
        print("they have an assistant")
        a = assistants[message.author]  # Use their assistant
        lines, contextVar = a.message(message.content, contextVar)  # And send their message
    else:  # If they don't have an assistant yet
        a = WatsonAssistantV2Utility.WatsonAssistant(VERSION, API_KEY, ASSISTANT_ID)  # Make one
        assistants[message.author] = a  # And save it
        lines, contextVar = a.message('', contextVar)  # Then send the welcome trigger

    for line in lines:
        rt = line["response_type"]

        # Bot gave text, so show it
        if rt == "text":
            print("Send:", line['text'])
            await reply(message, line['text'])

        # Bot 'typing' or waiting, so wait for a moment
        elif rt == "pause":
            if line['typing']:
                print("Send:", 'User is typing...')
                await reply(message, 'User is typing...')

            # Sleep for typing duration (or just print it if debugging mode)
            seconds = line['time'] / 1000  # Convert from ms to s
            sleep(seconds)

        elif rt == "option":
            print(line['title'])
            if line['title']:  # Can't send empty lines, often have empty title for questions
                message.channel.send(line['title'])
            for o in line['options']:
                print(o['label'], ": ", o['value']['input']['text'], sep="")
                await reply(message, o['label'] + ": " + o['value']['input']['text'])

        # Short pause between anything, even if no 'typing'
        sleep(0.1)

        print()  # Newline

    contexts[message.author] = contextVar  # Save their new context

    print("Contexts:\n", contextVar, contexts)

    # if message.content.startswith('!hello'):
    #     await message.channel.send("test")
    # content = 'confused cat noises'
    # msg = '{0.mention}, {1}'.format(message.author, content)
    # await message.channel.send(msg)


async def reply(message, response):

    # Replace any name-text emojis (looks like :niko:)
    # with corresponding name-id text for discord (looks like <:niko:012345678901234567>)
    # This assumes there are no duplicate names, or the replace could cause problems
    for e in bot.emojis:  # look through all visible emojis (all servers the bot is in)
        response = response.replace(":" + e.name + ":", "<:" + e.name + ":" + str(e.id) + ">")

    msg = '{0.mention}\n{1}'.format(message.author, response)
    await message.channel.send(msg)

bot.run(token)

for a in assistants:
    a.disconnect()
