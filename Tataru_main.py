import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
from lib import ff_blackjack
from lib import poe_cog
from lib import warframe
from lib import nsfw

class BotData:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('DISCORD_TOKEN')
        self.GUILD = os.getenv('DISCORD_GUILD')
        self.ENV = os.getenv('ENVIRONMENT')

        print("Initializing PoE Trade integration...")
        self.bulk_listings_to_display = 5

        self.bj_model = ff_blackjack.Blackjack()


bd = BotData()
bot = commands.Bot(command_prefix=
                   "*" if bd.ENV == 'dev' else "%")
bot.add_cog(warframe.WarframeCog(bot))
bot.add_cog(poe_cog.PoeCog(bot))
bot.add_cog(nsfw.NsfwCog(bot))

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=bd.GUILD)
    #print(f'{bot.user} has connected to {guild.name}!')
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

bot.run(bd.TOKEN)
