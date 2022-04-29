import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
from lib import ff_blackjack
from lib import poe
from lib import warframe
from lib import nsfw

class BotData:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.GUILD = os.getenv('DISCORD_GUILD')

        print("Initializing PoE Trade integration...")
        self.poe_cog = poe.PoeCog()
        self.bulk_listings_to_display = 5

        self.bj_model = ff_blackjack.Blackjack()


bd = BotData()
bot = commands.Bot(command_prefix="%")
bot.add_cog(warframe.WarframeCog(bot))
bot.add_cog(nsfw.NsfwCog(bot))

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
    except ValueError:
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
    listings = bd.poe_cog.price_check_bulk_ex(item, bd.bulk_listings_to_display)
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

    listings = bd.poe_cog.price_check_bulk_chaos(item, min_stock, bd.bulk_listings_to_display)
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

@bot.command(name="ex")
async def get_exalt_price(ctx):
    """
    Retrieves current exalt price from poe.ninja.
    """
    price_rounded, price_unrounded = bd.poe_cog.ninja_get_exalt_price()
    response = 'Tataru says:\n' \
               '```' \
               f'Current Exalt price: {price_rounded} (rounded from {price_unrounded})' \
               '```'
    await ctx.send(response)

@bot.command(name="extoc")
async def ex_to_c(ctx, exalts):
    """
    Converts given number of exalts to chaos.
    """
    try:
        exalts = exalts.replace(',', '.')
        exalts = float(exalts)
    except ValueError:
        response = 'Tataru says:\n> Please input a number.'
        await ctx.send(response)
        return

    chaos, ex_price = bd.poe_cog.exalt_to_chaos(float(exalts))
    response = 'Tataru says:\n' \
               '```' \
               f'Price in Chaos: {chaos} (current price: {ex_price})' \
               '```'
    await ctx.send(response)

@bot.command(name="breachstone")
async def breachstone(ctx):
    """
    Lists the prices of all breachstones, organized by boss and tier.
    """
    prices = bd.poe_cog.get_breachstones()
    response = 'Tataru says:\n' \
               '```'
    for boss in prices.keys():
        for tier in prices[boss].keys():
            indent_offset = 8
            # longest combo = Uul-Netol Flawless (17)
            # non-vanilla tiers also add another space
            indent_offset += 17 - (len(boss) + (len(tier) if tier != 'Vanilla' else -1))
            indent = indent_offset * ' '
            response += f"{boss}'s{' ' + tier if tier != 'Vanilla' else ''} Breachstone:{indent}{prices[boss][tier]}\n"
        response += '\n'
    response += '```'
    await ctx.send(response)

@bot.command(name="uberlab")
async def uberlab(ctx):
    """
    Get today's Uberlab layout from poelab.
    """
    img_link = bd.poe_cog.get_uberlab()
    response = f'Tataru says:\n{img_link}'
    await ctx.send(response)

bot.run(bd.TOKEN)
