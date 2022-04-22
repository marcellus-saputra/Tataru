import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
import requests
import asyncio
from lib import bj_mw

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

doujin_max = 1000000

pities = {}

bot = commands.Bot(command_prefix="%")

bj_model = bj_mw.Blackjack_mw()

@bot.command(name="bj_chance")
async def bj_chance(ctx, player_hand, player_has_ace, dealer_hand):
    dealer_has_ace = False
    try:
        player_hand = int(player_hand)
        player_has_ace = player_has_ace.lower() == 't'
        dealer_hand = int(dealer_hand)
        dealer_has_ace = dealer_hand == 11
    except:
        response = f'Tatary says:\n> Invalid input. Please input your game state as follows: ' \
                   f'"<your hand> <T or t if you have an ace, anything else otherwise> <dealer hand>.'
        await ctx.send(response)
        return

    stay_chance, hit_chance, best_action = bj_model.chance(player_hand, player_has_ace, dealer_hand, dealer_has_ace)
    response = f'Tataru says:\n> Chance to win if STAY: {stay_chance:.2f}%\n> Chance to win if HIT: {hit_chance:.2f}%\n> Best course of action: {best_action}'
    await ctx.send(response)

@bot.command(name="roll")
async def roll(ctx, *args):
    response = f'Tataru says:\n> {random.choice(args)}'
    await ctx.send(response)

@bot.command(name="doujin_no")
async def doujin_no(ctx):
    if type(ctx.channel) is not discord.DMChannel:
        try:
            if ctx.channel.name != "lewd" and ctx.channel.name != "nsfw":
                response = 'Tataru recommends:\n> Doing this in an NSFW channel.'
                await ctx.send(response)
                return
        except AttributeError:
            response = 'Channel unclear. This command can only be used in DMs or in the lewd/nsfw channels'
            await ctx.send(response)
            return
    id_exists = False
    tries = 0
    while not id_exists:
        id = random.randrange(0, doujin_max)
        #print(f'Trying id: {id}...')
        url = f'https://nhentai.net/g/{id}'
        r = requests.get(url)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            tries += 1
            await asyncio.sleep(0.5)
            continue
        id_exists = True
    response = f'Tataru recommends (after {tries} tries):\n> {id}'
    await ctx.send(response)

@bot.command(name="doujin")
async def doujin(ctx):
    if type(ctx.channel) is not discord.DMChannel:
        try:
            if ctx.channel.name != "lewd" and ctx.channel.name != "nsfw":
                response = 'Tataru recommends:\n> Doing this in an NSFW channel.'
                await ctx.send(response)
                return
        except AttributeError:
            response = 'Channel unclear. This command can only be used in DMs or in the lewd/nsfw channels'
            await ctx.send(response)
            return
    id_exists = False
    tries = 0
    while not id_exists:
        id = random.randrange(0, doujin_max)
        #print(f'Trying id: {id}...')
        url = f'https://nhentai.net/g/{id}'
        r = requests.get(url)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            tries += 1
            await asyncio.sleep(0.5)
            continue
        id_exists = True
    response = f'Tataru recommends (after {tries} tries):\n{url}'
    await ctx.send(response)

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user} has connected to {guild.name}!')
    print("Populating Blackjack model...")
    bj_model.populate()

bot.run(TOKEN)
