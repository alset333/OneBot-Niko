#!/usr/bin/env python3

from discord.ext import commands
import os

# Save you bot token in a txt file in a folder ID. The folder should be in the CWD when the program runs.
# This allows code portability, and you can disable version control of the token in .gitignore so it never uploads.
token_path = os.path.normpath('ID/DISCORD_BOT_TOKEN.txt')  # Gets a path to DISCORD_BOT_TOKEN.txt in directory ID
token = str.rstrip(open(token_path).read())  # Load Token from file, removing trailing whitespace

description = '''A test Discord bot using Discord.py Rewrite

Code written by Peter Maar (alset333)
https://github.com/alset333/OneBot-Niko'''
bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Bot has logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# Good code to get a sense of how it works at its basics
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
    """REMOVE THIS BEFORE PUTTING IT ON A PUBLIC SERVER
    Since PyCharm doesn't send/wait for Ctrl+C when stopping, use this command to gracefully disconnect to help tests.
    """
    await bot.logout()


@bot.listen()
async def on_message(message):  # Called when a message is received by the bot
    print(message)  # Displays the information of every single message the bot sees. Should only use for tests.

    if message.author.bot:  # If the bot sent the message
        return  # Don't do anything with it

    if message.content.startswith('test'):
        await message.channel.send("testing 123")

    content = 'I see your message! Try ' + bot.command_prefix + 'help for more info about commands!'
    msg = '{0.mention}, {1}'.format(message.author, content)  # Mention the sender, and reply with content
    await message.channel.send(msg)


bot.run(token)  # Start the bot
