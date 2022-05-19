from discord.ext import commands
from . import poe

class PoeCog(commands.Cog, name="PoE"):
    def __init__(self, bot):
        if bot:
            self.bot = bot
        self._last_member = None

        self.bulk_listings_to_display = 5

        self.poe_util = poe.PoeUtil()

    @commands.command(name="bce")
    async def bulk_check_ex(self, ctx, item):
        """
        Queries the official bulk exchange API for the item you input.
        Returns the first (configurable) number of listings with their bulk exchange rate in exalts.
        """
        listings = self.poe_util.price_check_bulk_ex(item, self.bulk_listings_to_display)
        response = 'Tataru says:\n'
        response += '```'
        for listing in listings:
            response += f'Price: {listing[0]} \t exalt \t Stock: {listing[1]}\n'
        response = response[:-1]
        response += '```'
        await ctx.send(response)

    @commands.command(name="bcc")
    async def bulk_check_chaos(self, ctx, item, min_stock=0):
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
            response = 'Tataru says:\n> Please input a minimum stock that is higher than 0.'
            await ctx.send(response)
            return

        listings = self.poe_util.price_check_bulk_chaos(item, min_stock, self.bulk_listings_to_display)
        response = 'Tataru says:\n'
        response += '```'
        for listing in listings:
            response += f'Price: {listing[1]:.1f} \t chaos \t Note: {listing[0]}\n'
        response = response[:-1]
        response += '```'
        await ctx.send(response)

    @commands.command(name="set_bulk_listings_to_display")
    async def set_bulk_listings_to_display(self, ctx, i):
        """
        Sets the number of listings returned by PoE Trade commands.
        Default is 5.
        """
        try:
            i = int(i)
            if i <= 0:
                response = 'Tataru says:\n> Cannot set to a number <= 0.'
            else:
                self.bulk_listings_to_display = i
                response = f'Tataru says:\n> Now displaying {self.bulk_listings_to_display} on bulk price checks...'
        except:
            response = 'Tataru says:\n> Invalid input.'

        await ctx.send(response)

    @commands.command(name="ex")
    async def get_exalt_price(self, ctx):
        """
        Retrieves current exalt price from poe.ninja.
        """
        price_rounded, price_unrounded = self.poe_util.ninja_get_exalt_price()
        response = 'Tataru says:\n' \
                   '```' \
                   f'Current Exalt price: {price_rounded} (rounded from {price_unrounded})' \
                   '```'
        await ctx.send(response)

    @commands.command(name="extoc")
    async def ex_to_c(self, ctx, exalts):
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

        chaos, ex_price = self.poe_util.exalt_to_chaos(float(exalts))
        response = 'Tataru says:\n' \
                   '```' \
                   f'Price in Chaos: {chaos} (current price: {ex_price})' \
                   '```'
        await ctx.send(response)

    @commands.command(name="breachstone")
    async def breachstone(self, ctx):
        """
        Lists the prices of all breachstones, organized by boss and tier.
        """
        prices = self.poe_util.get_breachstones()
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

    @commands.command(name="uberlab")
    async def uberlab(self, ctx):
        """
        Get today's Uberlab layout from poelab.
        """
        img_link = self.poe_util.get_lab(3)
        response = f'Tataru found:\n{img_link}'
        await ctx.send(response)

    @commands.command(name="lab3")
    async def lab3(self, ctx):
        """
        Get today's Lab3 layout from poelab.
        """
        img_link = self.poe_util.get_lab(2)
        response = f'Tataru found:\n{img_link}'
        await ctx.send(response)

    @commands.command(name="lab2")
    async def lab3(self, ctx):
        """
        Get today's Lab2 layout from poelab.
        """
        img_link = self.poe_util.get_lab(1)
        response = f'Tataru found:\n{img_link}'
        await ctx.send(response)

    @commands.command(name="lab")
    async def lab3(self, ctx):
        """
        Get today's Normal Lab layout from poelab.
        """
        img_link = self.poe_util.get_lab(0)
        response = f'Tataru found:\n{img_link}'
        await ctx.send(response)

    @commands.command(name="tags")
    async def tags(self, ctx):
        """
        Get link to trade website's "About" page that contains all API-searchable item tags.
        """
        response = 'Tataru says:\n> https://www.pathofexile.com/trade/about'
        await ctx.send(response)

    @commands.command(name="heist_gems")
    async def get_heist_gems(self, ctx, *args):
        """
        Search poe.ninja prices for skill gems matching the given names. Made for heisting.
        """
        gem_prices = self.poe_util.ninja_heist_gems(args)

        if len(gem_prices) == 0:
            response = 'Tataru says:\n> No results found.'
            await ctx.send(response)
            return

        max_gem_name_length = max(len(' '.join(gem.split()[1:])) for gem in gem_prices.keys())
        max_variant_length = 5  # 20/20

        response = 'Tataru says:\n' \
                   '```'
        for gem in gem_prices.keys():
            gem_name_split = gem.split()
            variant_indentation = ' ' * (max_variant_length - len(gem_name_split[0]))
            name_indentation = ' ' * (max_gem_name_length - len(' '.join(gem_name_split[1:])))
            response += f'\n{gem_name_split[0]}{variant_indentation}\t' \
                        f'{" ".join(gem_name_split[1:])}{name_indentation} :\t' \
                        f'{gem_prices[gem]}'
        response += '```'
        await ctx.send(response)
        return
