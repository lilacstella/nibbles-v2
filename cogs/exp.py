import discord
from discord.ext import commands
import random
from datetime import datetime
from cogs import db


class Exp(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.vc = {}
        self.db = db.DataBase(client)

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Exp online')

    @commands.Cog.listener()
    async def on_message(self, message):
        now = datetime.now()
        _id = message.author.id
        record = await self.db.find_user(db='users', user=str(_id))
        if record is None:
            if not message.author.bot:
                await self.db.insert(db='users', init_val=f"({str(_id)}, 0, 160, '{now.strftime('%H:%M:%S')}')")
        else:
            last = datetime.strptime(record[3], '%H:%M:%S')
            tdelta = now - last
            if message.content[:1] == '.' or tdelta.seconds < random.randrange(45, 60):
                return
            val = random.randrange(6, 8)

            await self.db.update(db='users', var='pts', amount='+' + str(val), user=str(_id))
            await self.db.update(db='users', var='bal', amount='+' + str(val), user=str(_id))
            await self.db.set_time(db='users', user=str(_id))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev, cur):
        if member.bot:
            return
        if prev.channel is None:
            self.vc[member.id] = datetime.now()
        elif cur.channel is None:
            tdelta = datetime.now() - self.vc.pop(member.id)
            val = int(tdelta.seconds / 30)
            await self.db.update(db='users', var='pts', amount='+' + str(val), user=str(member.id))
            await self.db.update(db='users', var='bal', amount='+' + str(val), user=str(member.id))

    # commands
    @commands.command()
    async def bal(self, ctx):
        if len(ctx.message.mentions) == 0:
            temp = await self.db.find_user(db='users', user=str(ctx.author.id), var='bal')
            pronoun = 'Your'
        else:
            member = ctx.message.mentions[0]
            temp = await self.db.find_user(db='users', user=str(member.id), var='bal')
            pronoun = member.display_name + "'s"

        if temp is None:
            await ctx.send("this person does not have a nom nom stash")
        else:
            await ctx.send(f"{pronoun} current balance is: {str(temp[0])} nom noms :cookie:")

    @commands.command(aliases=['lb', 'xp_lb', 'pts_lb'])
    async def leaderboard(self, ctx):
        await ctx.channel.send(embed=await self.db.lb('pts'))

    @commands.command()
    async def bal_lb(self, ctx):
        embed_var = await self.db.lb('bal')
        bal = await self.db.find_user('users', str(ctx.author.id), var='bal')
        total = await self.db.find('users', 'SUM(bal)')
        embed_var.add_field(name='You', value=f'own {str(format(bal[0]/total[0]*100, ".2f"))}% '
                                              f'of the nom noms in the server!')
        await ctx.channel.send(embed=embed_var)


def setup(client):
    client.add_cog(Exp(client))
