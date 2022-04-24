import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
import requests
import asyncio
from lib import bj_mw
from lib import poe_trade

class BotData:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.GUILD = os.getenv('DISCORD_GUILD')

        self.doujin_max = 1000000

        print("Initializing PoE Trade integration...")
        self.trade = poe_trade.PoeTrade()
        self.bulk_listings_to_display = 5

        self.bj_model = bj_mw.Blackjack_mw()


bd = BotData()
bot = commands.Bot(command_prefix="%")

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=bd.GUILD)
    print(f'{bot.user} has connected to {guild.name}!')
    print("Populating Blackjack model...")
    bd.bj_model.populate()

@bot.command(name="bj_chance")
async def bj_chance(ctx, player_hand, player_has_ace, dealer_hand):
    """
    Given the value of your hand, whether you have received an ace, and the value of the dealer's current hand,
    calculates the probability of you winning if you choose to HIT and if you choose to STAY.
    If you have an ace, use 't' or 'T'. Otherwise, inputting anything else will be considered a False.
    If the dealer has an ace, use 1 as the value of the dealer's hand.
    """
    try:
        player_hand = int(player_hand)
        player_has_ace = player_has_ace.lower() == 't'
        dealer_hand = int(dealer_hand)
        dealer_has_ace = dealer_hand == 1
    except:
        response = f'Tataru says:\n> Invalid input. Please input your game state as follows: ' \
                   f'"<your hand> <T or t if you have an ace, anything else otherwise> <dealer hand>.'
        await ctx.send(response)
        return

    stay_chance, hit_chance, best_action = bd.bj_model.chance(player_hand, player_has_ace, dealer_hand, dealer_has_ace)
    response = f'Tataru says:\n> Chance to win if STAY: {stay_chance:.2f}%\n> Chance to win if HIT: {hit_chance:.2f}%\n> Best course of action: {best_action}'
    await ctx.send(response)

@bot.command(name="roll")
async def roll(ctx, *args):
    """
    Returns one of the arguments randomly.
    For multi-word choices, use "" around them.
    """
    response = f'Tataru says:\n> {random.choice(args)}'
    await ctx.send(response)

@bot.command(name="bce")
async def bulk_check_ex(ctx, item):
    """
    Queries the official bulk exchange API for the item you input.
    Returns the first (configurable) number of listings with their bulk exchange rate in exalts.
    """
    listings = bd.trade.price_check_bulk_ex(item, bd.bulk_listings_to_display)
    response = 'Tataru says:\n'
    response += '```'
    for listing in listings:
        response += f'Price: {listing[0]} \t exalt \t Stock: {listing[1]}\n'
    response = response[:-1]
    response += '```'
    await ctx.send(response)

@bot.command(name="bcc")
async def bulk_check_chaos(ctx, item, min_stock):
    """
    Queries the official bulk exchange API for the item you input along with a minimum stock.
    Returns the first (configurable) number of listings with their price in chaos and the bulk exchange rate attached in the note.
    """
    try:
        min_stock = int(min_stock)
    except ValueError:
        response = 'Tataru says:\n> Please input an (integer) minimum stock.'
        await ctx.send(response)
        return

    if min_stock <= 0:
        response = 'Tataru says:\n> Minimum stock must be 1 or higher.'
        await ctx.send(response)
        return

    listings = bd.trade.price_check_bulk_chaos(item, min_stock, bd.bulk_listings_to_display)
    response = 'Tataru says:\n'
    response += '```'
    for listing in listings:
        response += f'Price: {listing[1]:.1f} \t chaos \t Note: {listing[0]}\n'
    response = response[:-1]
    response += '```'
    await ctx.send(response)

@bot.command(name="set_bulk_listings_to_display")
async def set_bulk_listings_to_display(ctx, i):
    """
    Sets the number of listings returned by PoE Trade commands.
    Default is 5.
    """
    try:
        i = int(i)
        if i <= 0:
            response = 'Tataru says:\n> Cannot set to a number <= 0.'
        else:
            bd.bulk_listings_to_display = i
            response = f'Tataru says:\n> Now displaying {bd.bulk_listings_to_display} on bulk price checks...'
    except:
        response = 'Tataru says:\n> Invalid input.'

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
        id = random.randrange(0, bd.doujin_max)
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
        id = random.randrange(0, bd.doujin_max)
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

bot.run(bd.TOKEN)
