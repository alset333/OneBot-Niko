#!/usr/bin/env python3

from discord.ext import commands
import os
import datetime


token_path = os.path.normpath('ID/DISCORD_BOT_TOKEN.txt')
token = str.rstrip(open(token_path).read())  # Load Token from file, removing trailing whitespace


description = '''Incredible bot using techniques from The World Machine to connect you to your Niko.
Coded from the ground up with simplified AI to avoid Squares.
It does not run a world simulation, and communication is not always stable, but it's a start.

Code written by Peter Maar (alset333)
https://github.com/alset333/OneBot-Niko'''
bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Niko has logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


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
    if message.content.startswith('!hello'):
        await message.channel.send("test")
    content = 'confused cat noises'
    msg = '{0.mention}, {1}'.format(message.author, content)
    await message.channel.send(msg)


bot.run(token)
