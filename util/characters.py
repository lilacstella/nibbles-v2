import sqlite3

from discord.ext import commands
from discord.ext.commands import has_permissions


class Characters(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('./data/characters.db')
        # character information library
        self.c = self.conn.cursor()

    # add cog to main system
    @commands.Cog.listener()
    async def on_ready(self):
        print('Characters online')

    def all_characters(self):
        self.c.execute(f'SELECT name FROM characters WHERE rarity = 5')
        fives = self.c.fetchall()
        self.c.execute(f'SELECT name FROM characters WHERE rarity = 4')
        fours = self.c.fetchall()

        for index, five in enumerate(fives):
            fives[index] = five[0]
        for index, four in enumerate(fours):
            fours[index] = four[0]
        return fives, fours

    def find_character(self, char_name: str, var: str = '*'):
        self.c.execute(
            f"SELECT {var} FROM characters WHERE name = '{char_name}'")
        if var != '*':
            return self.c.fetchone()[0]
        else:
            return self.c.fetchone()

    def find(self, var: str):
        self.c.execute(f'SELECT {var} FROM characters')
        return self.c.fetchall()

    def level_calc(self, xp: int):
        xp += 1
        self.c.execute('SELECT level, total FROM xp')
        level = 1
        for total_req in self.c.fetchall():
            if isinstance(total_req[1], int) and xp > total_req[1]:
                level = total_req[0]
        self.c.execute(f'SELECT total, next_lvl FROM xp WHERE level = {level}')
        temp = self.c.fetchone()
        xp -= 1
        if temp[0] == '':
            cur_xp = xp
        else:
            cur_xp = xp - temp[0]
        next_lvl = temp[1]
        if next_lvl == '':
            next_lvl = 'MAX'
        # current level, current level xp, next level xp
        output = (level, cur_xp, next_lvl)
        # print(output)
        return output

    def fetch_levels(self):
        self.c.execute(f'SELECT level, total FROM xp')
        return self.c.fetchall()


def setup(client):
    client.add_cog(Characters(client))
