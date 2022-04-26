import requests
import json
from discord.ext import commands


class WarframeCog(commands.Cog, name="Warframe"):
    def __init__(self, bot):
        if bot:
            self.bot = bot
        self._last_member = None

        self.wfstatus_url = 'https://api.warframestat.us/pc'

    @commands.command()
    async def invasion(self, ctx):
        '''
        Checks current ongoing invasions and their rewards.
        '''
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

    @commands.command()
    async def cetus(self, ctx):
        '''
        Checks current day/night cycle in Cetus.
        '''
        r = requests.get(self.wfstatus_url + '/cetusCycle')
        #print(json.dumps(r.json(), indent=4))
        r = r.json()
        response = f'Tataru says:\n> {"Daytime" if r["isDay"] else "Nighttime"}, {r["timeLeft"]} left.'
        await ctx.send(response)

#cog = WarframeCog(None)
#cog.cetus()