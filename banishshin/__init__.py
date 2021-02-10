from .core import BanishShin


async def setup(bot):
    cog = BanishShin(bot)
    bot.add_cog(cog)
