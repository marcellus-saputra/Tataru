import requests
import json
from discord.ext import commands


class WarframeCog(commands.Cog, name="Warframe Cog"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

        self.wfstatus_url = 'https://api.warframestat.us/pc'

    @commands.command()
    async def invasion(self, ctx):
        invasions = self.get_invasion_data()
        response = 'Tataru says:\n```'
        for invasion in invasions:
            response += invasion[0] + ('\n' + invasion[1] if invasion[1] != '' else '') + '\n' + invasion[2] + '\n\n'
        response += '\n```'
        await ctx.send(response)

    def get_invasion_data(self):
        r = requests.get(self.wfstatus_url + '/invasions')
        invasion_list = []
        for invasion in r.json():
            invasion_list.append((
                invasion['node'],
                invasion['attackerReward']['asString'],
                invasion['defenderReward']['asString']
            ))
            #print(invasion['attackingFaction'])
            #print(invasion['defendingFaction'])
        return invasion_list

#cog = WarframeCog()
#cog.get_invasion_data()