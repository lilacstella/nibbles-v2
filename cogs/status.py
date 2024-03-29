import discord
from discord.ext import commands
import random


class Status(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.games = ['League of Legends', 'Genshin Impact', 'Minecraft', 'osu!', 'VALORANT']

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Status online')

    # commands
    @commands.Cog.listener()
    async def on_member_update(self, prev, cur):
        if prev.guild is not None and prev.guild.id != 607298393370394625:
            return
        if cur.nick is not None and cur.nick.lower() != cur.nick:
            await cur.edit(nick=cur.nick.lower())
        if cur.activity is not None and cur.activity.name in self.games:
            role = discord.utils.get(cur.guild.roles, name=cur.activity.name)
            try:
                await cur.add_roles(role)
            except AttributeError:
                pass

            if prev.activity is not None and prev.activity.name in self.games:
                old = discord.utils.get(prev.roles, name=prev.activity.name)
                if old != role:
                    try:
                        await prev.remove_roles(old)
                    except AttributeError:
                        pass
        else:
            try:
                for game in self.games:
                    await cur.remove_roles(discord.utils.get(prev.guild.roles, name=game))
            except AttributeError:
                pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev, cur):
        if (cur.channel is not None) and cur.channel.id == 625001001467772928:
            vc_names = ['🍩 Donut', '🍜 Ramen', '🥟 Dumpling', '🌮 Taco', '🥐 Croissant', '🍞 Bread', '🥞 Pancakes',
                        '🧇 Waffle', '🍕 Pizza', '🌯 Burrito', '🍣 Sushi', '🍙 Onigiri', '🧁 Cupcake', '🍪 Cookie',
                        '🥧 Pie', '🍫 Chocolate', '☕ Coffee']

            if member.activity is not None and member.activity.name in self.games:
                name = random.choice(['🎮', '🌎', '⭐', '🌠', '🌌']) + member.activity.name
            else:
                name = random.choice(vc_names)

            vc = await member.guild.create_voice_channel(name, category=discord.utils.get(member.guild.categories,
                                                                                          name='Void Zone'))
            await member.move_to(vc)

        if prev.channel is not None:
            if member.guild.id == 607298393370394625 and prev.channel.id not in [625001001467772928, 703248310634414183] \
                    and len(prev.channel.members) == 0:
                await prev.channel.delete()


def setup(client):
    client.add_cog(Status(client))
