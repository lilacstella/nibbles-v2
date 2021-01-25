import sqlite3

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from datetime import datetime


class DataBase(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('user.db')
        self.c = self.conn.cursor()
        self.scheduler = AsyncIOScheduler()
        self.c.execute("DELETE from users WHERE user_id = 529083253571977218")
        self.conn.commit()

    # add cog to main system
    @commands.Cog.listener()
    async def on_ready(self):
        print('DataBase online')

    # database utility functions
    async def lb(self, category: str):
        self.c.execute("SELECT * FROM users ORDER BY " + category + " DESC LIMIT 10")
        title = 'most active!' if category == 'pts' else 'richest!'
        unit = category if category == 'pts' else ':cookie:'
        embed_var = discord.Embed(title="People who are the " + title, color=0x8109e9)
        lb = self.c.fetchall()
        rank = ''
        name = ''
        val = ''
        for i in range(0, len(lb)):
            rank += str(i + 1) + '\n'
            name += self.client.get_user(lb[i][0]).display_name + '\n'
            val += str(lb[i][1 if category == 'pts' else 2]) + unit + '\n'
        embed_var.add_field(name='Rank', value=rank, inline=True)
        embed_var.add_field(name='Name', value=name, inline=True)
        embed_var.add_field(name='Points' if category == 'pts' else 'Balance', value=val, inline=True)
        return embed_var

    async def set_time(self, db: str, user: str):
        self.c.execute(f"UPDATE {db} SET time = '{datetime.now().strftime('%H:%M:%S')}' WHERE user_id = {user}")
        self.conn.commit()

    async def find_user(self, db: str, user: str, var: str = '*'):
        self.c.execute(f"SELECT {var} FROM {db} WHERE user_id = {user}")
        return self.c.fetchone()

    async def insert(self, db: str, init_val: str):
        # c.execute("INSERT INTO users VALUES (123456789, 0, 0)")
        self.c.execute(f"INSERT INTO {db} VALUES {init_val}")
        self.conn.commit()

    async def update(self, db: str, var: str, amount: str, user: str):
        # amount here must have + or -
        self.c.execute(f"UPDATE {db} SET {var} = {var}{amount} WHERE user_id = {user}")
        self.conn.commit()

    async def set(self, db: str, var: str, amount: str, user: str):
        self.c.execute(f"UPDATE {db} SET {var} = {amount} WHERE user_id = {user}")
        self.conn.commit()

    async def find(self, db: str, var: str):
        self.c.execute(f'SELECT {var} FROM {db}')
        return self.c.fetchone()

    @tasks.loop(hours=12)
    async def vacuum(self):
        self.c.execute("VACUUM")
        self.conn.commit()

    @commands.command()
    async def profile(self, ctx):
        user_info = self.find_user(db='users', user=str(ctx.author.id))

    def start_scheduler(self, scheduler: AsyncIOScheduler):
        wheel = self.client.get_cog('Gamble').init_announce
        banner = self.client.get_cog('Summon').init_banner_rotation
        self.scheduler.start()
        launch_time = datetime.date.today() + datetime.timedelta(days=1)
        wheel_job = scheduler.add_job(wheel, launch_time)
        vacuum_job = scheduler.add_job(self.vacuum.start, launch_time)
        banner_job = scheduler.add_job(banner, launch_time)

    @commands.command()
    @has_permissions(manage_guild=True)
    async def close_table(self, ctx):
        self.conn.close()
        await ctx.send('db connection closed')


def setup(client):
    client.add_cog(DataBase(client))
