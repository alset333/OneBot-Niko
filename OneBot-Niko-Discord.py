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
from discord import Game, Status, embeds
import os, sys
import WatsonAssistantV2Utility
import WatsonTranslatorV3Utility
from Logger import log, close_log
import json
from concurrent.futures._base import CancelledError
import asyncio
from datetime import datetime, timezone

VERSION = '2019-05-20'
GROUP_TIME = 3  # How long to keep the queue grouped

# Watson keys
assistant_api_path = os.path.normpath('ID/ASSISTANT_API_KEY.txt')
assistant_id_path = os.path.normpath('ID/ASSISTANT_ID.txt')
translator_api_path = os.path.normpath('ID/TRANSLATOR_API_KEY.txt')
ASSISTANT_API_KEY = str.rstrip(open(assistant_api_path).read())  # Load API Key from file, removing trailing whitespace
ASSISTANT_ID = str.rstrip(open(assistant_id_path).read())  # Load Assistant ID from file, removing trailing whitespace
TRANSLATOR_API_KEY = str.rstrip(open(translator_api_path).read())

translator = WatsonTranslatorV3Utility.WatsonTranslator(VERSION, TRANSLATOR_API_KEY)


# Discord keys
token_path = os.path.normpath('ID/DISCORD_BOT_TOKEN.txt')
token = str.rstrip(open(token_path).read())  # Load Token from file, removing trailing whitespace


description = """
OneBot-Niko  Copyright (C) 2019  Peter Maar
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to
redistribute it under certain conditions.
Type '?about' for more details.
------------------------------------------------

Incredible bot using techniques from The World Machine to connect you to your Niko.
Coded from the ground up with simplified AI to avoid Squares.
It does not run a world simulation, and communication is not always stable, but it's a start.
"""
bot = commands.Bot(command_prefix='?', description=description)

logged_out = False

# Note, the authors are matched to the bot even across servers.
# You can start a conversation in one and continue in another. Only one Niko per person!
assistants = {}  # A dictionary matching each "message.author" to their "assistant" as {author : assistant}
contexts = {}  # A dictionary matching each "message.author" to their "context" as {author : context}
queues = {}  # A dictionary matching each "message.author" to their "queue" as {author : queue}


# Load save data
save_file_path = os.path.normpath('save_data.json')
save_file = open(save_file_path, 'r+')  # Open the save file for writing

update_channel_id_path = os.path.normpath("update_channel_id")
if os.path.isfile(update_channel_id_path):
    update_channel_id = int(open(update_channel_id_path).read())
    os.remove(update_channel_id_path)
    print("Update channel ID is", update_channel_id)
else:
    update_channel_id = None


def load_context():
    save_file_contents = save_file.read()  # Read the contents

    if len(str.rstrip(save_file_contents)) != 0:
        save_data = json.loads(save_file_contents)  # Read and decode the JSON from the file
        print(save_data)

        # Turn the keys back into ints from strings
        for save_data_key in save_data:
            contexts[int(save_data_key)] = save_data[save_data_key]


def save_context():
    log("Saving...")
    save_data = contexts  # Replace the save data
    save_file.seek(0)
    save_file.write(json.dumps(save_data))  # Write the save data
    save_file.truncate()
    log("Saved!")

bot_emoji_names = []

@bot.event
async def on_ready():
    global bot_emoji_names
    global update_channel_id
    log('Niko has logged in as')
    log(bot.user.name)
    log(bot.user.id)
    log("Available Emojis:", bot.emojis)

    bot_emoji_names = []
    for emoji in bot.emojis:
        bot_emoji_names.append(emoji.name)

    log('------', flush=True)

    game = Game("with friends!")
    await bot.change_presence(status=Status.online, activity=game)

    if update_channel_id:
        channel = bot.get_channel(update_channel_id)
        await channel.send("[Update complete!]")
        # In case we end up here again somehow (bot seemed to restart once) be sure it won't announce update again
        update_channel_id = None


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
    await ctx.send("Logging out")
    save_context()
    await logout_bot_async()



@bot.command()
async def save(ctx):
    save_context()


@bot.command()
async def about(ctx):
    """More information about the program."""
    await ctx.send("""    
```
Copyright (C) 2019  Peter Maar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact Peter Maar via email to petermaar@protonmail.com
The program's source can be found at https://github.com/alset333/OneBot-Niko
```
    """)


def logout_bot():
    global logged_out
    logged_out = True
    for assistant_key in assistants:
        a = assistants[assistant_key]
        a.disconnect()

    log("Contexts:", contexts)
    log("Assistants:", assistants)

    print("Saving on exit...")
    save_context()
    print("Saved!")

    save_file.close()

    close_log()

    print("Done.")


async def logout_bot_async():
    try:
        await bot.logout()
    except CancelledError as e:
        print("Exception", type(e), "on logout. This should be fine.")

    logout_bot()


@bot.command()
async def embed_test(ctx, desc="Do you think it would be better if I talked like this?"):

    from discord import embeds, colour as color
    em = embeds.Embed(color=0xFFDE29,
                      url='http://example.com',
                      description=desc)
    em.set_thumbnail(url="https://vignette.wikia.nocookie.net/oneshot/images/0/02/Niko.png/")
    em.set_footer(text="Ignore this for now: " + str(ctx.message.author.id))

    await ctx.send(embed=em)

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx):
    # Get information about the command
    message = ctx.message
    author = message.author

    # Delete the command
    await message.delete()

    # Write the response
    response = "[Updating at the request of "\
               + str(author.mention) + " '" + str(author.nick) + "' " + str(author) + " (" + str(author.id) + ")]"

    # Print the response, and send the response
    print(response)
    await ctx.send(response)

    # save the ctx to a file temporarily so we can reply when the update is done
    chan_out = open(update_channel_id_path, 'w')
    chan_out.write(str(message.channel.id))
    chan_out.close()

    # Shut down the bot and save/close files
    save_context()
    await logout_bot_async()

    # Update
    os.system("git fetch && git pull")

    # Start again

    args = sys.argv[:]
    print('Re-spawning %s' % ' '.join(args))

    args.insert(0, sys.executable)
    if sys.platform == 'win32':
        args = ['"%s"' % arg for arg in args]

    os.chdir(sys.path[0])
    os.execv(sys.executable, args)


def get_response(message, contextVar):
    if message.author.id in assistants:  # If they already have an assistant
        log("they have an assistant")
        a = assistants[message.author.id]  # Use their assistant
        lines, contextVar = a.message(message.content, contextVar)  # And send their message
    else:  # If they don't have an assistant yet
        a = WatsonAssistantV2Utility.WatsonAssistant(VERSION, ASSISTANT_API_KEY, ASSISTANT_ID)  # Make one
        assistants[message.author.id] = a  # And save it

        if contextVar == []:  # If their context is empty
            lines, contextVar = a.message('', contextVar)  # Then send the welcome trigger
        else:  # Otherwise
            lines, contextVar = a.message(message.content, contextVar)  # send their message

    return lines, contextVar


async def send_response(lines, message):

    for line in lines:
        rt = line["response_type"]

        # Bot gave text, so show it
        if rt == "text":
            log("Send:", line['text'])
            await reply(message, line['text'])

        # Bot 'typing' or waiting, so wait for a moment
        elif rt == "pause":
            if line['typing']:
                log("Send:", 'User is typing...')
                await reply(message, 'User is typing...')

            # Sleep for typing duration (or just print it if debugging mode)
            seconds = line['time'] / 1000  # Convert from ms to s
            # sleep(seconds)
            # await asyncio.sleep(seconds)

        elif rt == "option":
            log(line['title'])
            if line['title']:  # Can't send empty lines, often have empty title for questions
                message.channel.send(line['title'])
            for o in line['options']:
                log(o['label'], ": ", o['value']['input']['text'], sep="")
                await reply(message, o['label'] + ": " + o['value']['input']['text'])

        log()  # Newline


@bot.listen()
async def on_message(message, recursed=False):
    global bot_emoji_names
    log("Message:", message)
    log("Message content:", message.content)
    if message.author.bot:  # If the bot sent the message
        return  # Don't do anything with it

    if message.content[0] == bot.command_prefix:  # If the message is a command
        return  # Don't do anything with it

    if message.author.id in contexts:  # If they have a context
        log("they have a context")
        contextVar = contexts[message.author.id]  # Use their context
    else:
        log(message.author.id, 'is not in', contexts)
        contextVar = []  # Otherwise, use an empty one

    if message.author.id in queues:  # If they have a queue
        log("they have a queue")
        queue = queues[message.author.id]   # Use their queue
        if not recursed:  # If we haven't done this message before
            queue += [message] #  add this message to the queue
            return  # If there's a queue going and we're not here on recursion, leave now
    else:
        log(message.author.id, 'is not in', queues)
        queue = [message]  # Set the queue with this message

    queues[message.author.id] = queue  # Save queue back into dictionary


    oldest_message_time = queue[0].created_at
    latest_message_time = queue[-1].created_at

    current_time = datetime.now(timezone.utc).replace(tzinfo=None)

    seconds_elapsed = (current_time - oldest_message_time).total_seconds()
    print(seconds_elapsed)

    if seconds_elapsed > GROUP_TIME:
        total_content = ""
        for msg in queue:
            total_content += msg.content + " "
        message.content = total_content

        print("Full content to send is", message.content, "Recursive is", recursed)

        # Translate user's message to English
        message.content, userlang = translator.auto_translate(message.content)

        # Use the user's message to get a response from Watson Assistant. Update the context.
        lines, contextVar = get_response(message, contextVar)

        # Translate the response lines
        for i in range(0, len(lines)):
            if lines[i]['response_type'] == 'text':
                lines[i]['text'] = translator.translate_text(lines[i]['text'], 'en', userlang, emoji_names=bot_emoji_names)

        # Send the response from Watson Assistant to the User as a reply to the message.
        await send_response(lines, message)

        contexts[message.author.id] = contextVar  # Save their new context

        # Once we're done sending, remove entirely from queue
        del queues[message.author.id]
    else:
        print("Not enough time to send yet.")
        await asyncio.sleep(GROUP_TIME - seconds_elapsed)
        await on_message(message, recursed=True)

    log("Contexts:\n", contextVar, contexts)


async def reply(message, response):
    lastEmojiIndex = -1  # The position of the last/furthest emoji. This one is the face to make.
    lastEmojiName = ""  # The name of the last/furthest emoji. This one is the face to make.
    EMOJI_URL_PATH = "https://raw.githubusercontent.com/alset333/OneBot-Niko/master/Resources/Images/"

    # Find the last emoji, this is the one that should be used as the face
    for e in bot.emojis:  # look through all visible emojis (all servers the bot is in)
        thisEmojiIndex = response.rfind(":" + e.name + ":")  # Get the last occurrence of the emoji
        if lastEmojiIndex < thisEmojiIndex:  # If this is later than the current-latest...
            lastEmojiIndex = thisEmojiIndex  # Update this to be the new-latest
            lastEmojiName = e.name  # And save the name too

    # Remove the last emoji from the message
    if lastEmojiIndex > -1:  # If we found one
        pre = response[:lastEmojiIndex]
        post = response[lastEmojiIndex + len(lastEmojiName) + 2:]
        response = pre + post

    # Replace any name-text emojis (looks like :niko:)
    # with corresponding name-id text for discord (looks like <:niko:012345678901234567>)
    # This assumes there are no duplicate names, or the replace could cause problems
    for e in bot.emojis:  # look through all visible emojis (all servers the bot is in)
        response = response.replace(":" + e.name + ":", "<:" + e.name + ":" + str(e.id) + ">")

    # Embed-ify the message!
    em = embeds.Embed(color=0xFFDE29,
                      description=response)
    em.set_thumbnail(url=EMOJI_URL_PATH + lastEmojiName + ".png")
    # em.set_footer(text="Ignore this for now: " + str(message.author.id))

    if message.guild is None:  # DMs, just respond
        await message.channel.send(embed=em)
    else:  # Servers, be sure to mention them
        await message.channel.send(message.author.mention, embed=em)

load_context()
bot.run(token)

if not logged_out:
    logout_bot()

