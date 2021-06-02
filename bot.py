import asyncio

import discord
import os
import random
import pytz

from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from itertools import cycle
from threading import Thread
import time
from datetime import datetime, date, timedelta

client = commands.Bot(command_prefix='.',
                      intents=discord.Intents.all())
client.remove_command('help')

status = cycle([
    'cookie nomming', 'sleeping', 'being a ball of fluff', 'wheel running',
    'tunnel digging', 'wires nibbling', 'food stashing', 'treasure burying',
    'grand adventure', 'collecting taxes'
])

for filename in os.listdir('./util'):
    if filename.endswith('.py'):
        client.load_extension(f'util.{filename[:-3]}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

loop = asyncio.get_event_loop()
servers = client.get_cog('ServerManage')


@client.event
async def on_ready():
    change_status.start()
    print("Nibbles is awake!")

    _thread = Thread(target=launch_tasks)
    _thread.start()


def launch_tasks():
    asyncio.set_event_loop(client.loop)
    now = pytz.utc.localize(datetime.utcnow()).astimezone(
        pytz.timezone("America/Chicago"))
    midnight = datetime.combine(date.today() + timedelta(days=1),
                                datetime.min.time()) + timedelta(hours=6)
    midnight = midnight.astimezone(pytz.timezone("America/Chicago"))
    tdelta = midnight - now
    midnight_time = tdelta.total_seconds() % (24 * 3600)
    if midnight_time > 43200:
        time.sleep(midnight_time-43200)
    else:
        time.sleep(midnight_time)
    announcement_manager.start()


async def announce_year_progress(channels):
    tdelta = datetime.today() - datetime(datetime.today().year, 1, 1)
    percent = (float(tdelta.days) / 365)
    whole = int(percent * 15)
    partial = int(percent * 90) % 6
    empty = 15 - whole - partial
    braille = {
        0: '',
        1: '⣄',
        2: '⣆',
        3: '⣇',
        4: '⣧',
        5: '⣷',
        6: '⣿'
    }
    partial = braille[partial]
    year_progress = f'[{(whole * "⣿")}{partial}{(empty * "⣀")}]'
    for channel in channels:
        await channel.send(f'{datetime.today().year} Progress Bar: \n{year_progress} {(percent * 100):.2f}%')


@tasks.loop(hours=12)
async def announcement_manager():
    channels = servers.all_primary_channel()
    announce_to = []
    opt_gacha = []
    for index, ch_id in enumerate(channels):
        channel = await client.fetch_channel(ch_id[1])
        if ch_id[2]:
            opt_gacha.append(channel)
        send = True
        async for message in channel.history(limit=10):
            if message.author.bot and message.content == 'Your free wheel of fortune is now available!':
                send = False
        if send and channel.guild.me.guild_permissions.send_messages:
            announce_to.append(channel)
    now = datetime.utcnow()
    await client.get_cog('Gamble').announce_wheel(announce_to)
    if now.hour != 18:
        await client.get_cog('Summon').birthday(channels)
        await announce_year_progress(announce_to)
        await client.get_cog('Summon').new_banner_rotation(opt_gacha)


@tasks.loop(minutes=random.randrange(10, 45))
async def change_status():
    await client.change_presence(activity=discord.Streaming(
        name=next(status), url='https://twitch.tv/bitnoms'))


@client.event
async def on_member_join(member):
    prim = servers.find_primary_channel(member.guild.id)
    if prim is None:
        return
    await member.guild.get_channel(prim).send(
        f'Heyaa {member.name}, '
        f'I\'m nibbles! <:kayaya:778399319803035699>')
    if member.guild.id != 607298393370394625:
        return
    await member.add_roles(discord.utils.get(member.guild.roles, name='Moons'))
    await member.edit(nick=member.name.lower())


@client.event
async def on_member_remove(member):
    prim = servers.find_primary_channel(member.guild.id)
    if prim is None:
        return
    await member.guild.get_channel(prim).send(
        f'Bai bai {member.name} <:qiqi:813767632904781915>')


@client.event
async def on_command_error(ctx, error):
    if '.transfer' in ctx.message.content:
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "nibbles can't do anything, something is missing! <:ShibaNervous:703366029425901620>"
        )
    else:
        if not isinstance(error, commands.CommandNotFound):
            print(f'[{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}] {error}\n')


async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.guild.me.guild_permissions.send_messages:
            await channel.send('Please use .set_channel <channel_id> to tell nibbles where to speak!')
            await channel.send('Use .opt_in_banner afterwards to receive the new genshin gacha banner daily!')
            return

utility = ['choose', 'poll', 'get_pfp', 'size', 'profile', 'set_desc', 'set_birthday']
genshin = ['banner', 'event_wish', 'reg_wish', 'genshin_inventory', 'character', 'pity']
economy = ['gamble_black_jack', 'gamble_coin', 'bal', 'transfer']
leaderboard = ['leaderboard', 'rank']
todo = ['todo_list', 'todo_add', 'todo_check']


@client.command(name='help', hidden=True)
async def descriptions(ctx):
    desc = 'Here are the categories of nibbles\'s commands! React to the corresponding category to learn more!'
    embed = discord.Embed(title="Nibbles is here to help", color=random.randint(0, 0xFFFFFF), description=desc)

    embed.add_field(name='**Utility** 🔧', value=str(utility))
    embed.add_field(name='**Genshin** <:genshin:849405822781227069>', value=str(genshin))
    embed.add_field(name='**Economy** 💰', value=str(economy))
    if ctx.guild.id == 607298393370394625:
        embed.add_field(name='**Leaderboard** 🌟', value=str(leaderboard))
    embed.add_field(name='**To-do** ✅', value=str(todo))
    help_msg = await ctx.send(content='Help menu', embed=embed)
    await help_msg.add_reaction('🔧')
    await help_msg.add_reaction('<:genshin:849405822781227069>')
    await help_msg.add_reaction('💰')
    if ctx.guild.id == 607298393370394625:
        await help_msg.add_reaction('🌟')
    await help_msg.add_reaction('✅')


@client.command(hidden=True)
@has_permissions(manage_guild=True)
async def mod_help(ctx):
    output = ''
    for command in client.commands:
        if command.hidden:
            output += command.name + '\n'
    await ctx.send(output)


@client.event
async def on_message(message):
    if message.reference is None and client.user.mentioned_in(message):
        eight_ball = [
            'Nibbles agree.', 'Yesssu!', 'Yes yes.', 'Nibbles approve.',
            'You can count on it.', 'Nibbles thinks that is correct.',
            'Most likely.', 'Good good.', 'Ooooo wats dat?',
            'My nom noms said yes.', 'Huh? What did you say?.',
            'I\'m sleepy... ask later.', 'Its a secret hehe.',
            'Mommy says stranger danger!.', 'Daddy said he doesn\'t know.',
            'Nibbles thinks that is wrong.', 'My nom noms said no.',
            'Nibbles disagree.', 'Noooooo!', 'That is incorrect.'
        ]
        await message.channel.send(f'{random.choice(eight_ball)}\nuse .help for more!')
    else:
        await client.process_commands(message)


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.content == 'Help menu' and not user.bot:
        embed = discord.Embed.Empty
        if reaction.emoji == '🔧':
            embed = discord.Embed(title='Utility')
            for comm_name in utility:
                embed.add_field(name=comm_name, value=help_embed_value(comm_name), inline=False)
        elif str(reaction.emoji) == '<:genshin:849405822781227069>':
            embed = discord.Embed(title='Genshin')
            for comm_name in genshin:
                embed.add_field(name=comm_name, value=help_embed_value(comm_name), inline=False)
            print(embed)
        elif reaction.emoji == '💰':
            embed = discord.Embed(title='Economy')
            for comm_name in economy:
                embed.add_field(name=comm_name, value=help_embed_value(comm_name), inline=False)
        elif reaction.emoji == '🌟':
            embed = discord.Embed(title='Leaderboard')
            for comm_name in leaderboard:
                embed.add_field(name=comm_name, value=help_embed_value(comm_name), inline=False)
        elif reaction.emoji == '✅':
            embed = discord.Embed(title='To-do List')
            for comm_name in todo:
                embed.add_field(name=comm_name, value=help_embed_value(comm_name), inline=False)
        await reaction.message.edit(embed=embed)


def help_embed_value(comm_name):
    command = client.get_command(comm_name)
    value = command.description
    if len(command.aliases) != 0:
        value += f"\n{'aliases' if len(command.aliases) > 1 else 'alias'}: {command.aliases}"
    return value


@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == '🍪' and payload.message_id == 804860150195945493:
        guild = await client.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        await member.add_roles(
            discord.utils.get(guild.roles, name='Cookie Squad'))


@client.event
async def on_raw_reaction_remove(payload):
    if payload.emoji.name == '🍪' and payload.message_id == 804860150195945493:
        guild = await client.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        await member.remove_roles(
            discord.utils.get(guild.roles, name='Cookie Squad'))


client.run('NzM2MDEzNjQ1MDQ1MzAxMzAx.XxooHw.90H7LW32mCJIzmtVyZTQehjhfSE')
