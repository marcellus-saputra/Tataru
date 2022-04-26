import requests
from discord.ext import commands
import discord
import random


class NsfwCog(commands.Cog, name="NSFW"):
    def __init__(self, bot):
        if bot:
            self.bot = bot
        self._last_member = None
        self.doujin_max = 1000000

    @commands.command()
    async def doujin_no(self, ctx):
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
            id = random.randrange(0, self.doujin_max)
            # print(f'Trying id: {id}...')
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

    @commands.command()
    async def doujin(self, ctx):
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
            id = random.randrange(0, self.doujin_max)
            # print(f'Trying id: {id}...')
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