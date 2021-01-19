import discord
import os
import random
from discord.ext import commands, tasks
from itertools import cycle

client = commands.Bot(command_prefix='.',
                      intents=discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True,
                                              voice_states=True))
client.remove_command('help')

status = cycle(['cookie nomming', 'sleeping', 'being a ball of fluff', 'wheel running', 'tunnel digging',
                'wires nibbling', 'food stashing', 'treasure burying', 'grand adventure'])

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    change_status.start()
    print("Nibbles is awake!")


@tasks.loop(minutes=random.randrange(10, 45))
async def change_status():
    await client.change_presence(activity=discord.Streaming(name=next(status), url='https://twitch.tv/bitnoms'))


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.event
async def on_member_join(member):
    await member.guild.get_channel(681149093858508834).send(f'Heyaa {member.name}, '
                                                            f'I\'m nibbles! <:kayaya:778399319803035699>')
    await member.add_roles(discord.utils.get(member.guild.roles, name='Moons'))
    await member.edit(nick=member.name.lower())


@client.event
async def on_member_remove(member):
    await member.guild.get_channel(681149093858508834).send(f'Bai bai {member.name} <:qiqi:781667748031103036>')


# @client.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.MissingRequiredArgument) and ctx.message.content != '.help':
#         await ctx.send("nibbles can't do anything because you didn't gib something! <:ShibaNervous:703366029425901620>")


@client.command()
async def help(ctx, command):
    embed_var = discord.Embed(title="Nibbles is here to help", color=0x8109e9)
    desc = {
        'choose': 'Nibbles helps you choose because you\'re too indecisive',
        'coin_flip': 'flips a coin!',
        'poll': 'Nibbles helps you discover that other people are indecisive too',
        'purge': 'pew pew destroy messages',
        'bal': 'count the nom noms in your stash, ooo so many <:wow:788914745008586763>',
        'leaderboard': 'check the top ten people with the highest points!',
        'gamble_coin': 'flip a coin with the face you predict and how much you want to bet for it',
        'gamble_wheel': 'spin a wheel of fortune, paying 320 nom noms for a range of prizes from 77 to 10000',
        'gamble_black_jack': 'bet against any player that accepts the challenge by playing black_jack',
        'transfer': 'give your money to someone else, but why would you do that if you could give them all to nibbles'
    }

    if command is None:
        embed_var.add_field(name='choose', value=desc.get('choose'), inline=False)
        embed_var.add_field(name='coin_flip', value=desc.get('coin_flip'), inline=False)
        embed_var.add_field(name='poll', value=desc.get('poll'), inline=False)
        embed_var.add_field(name='purge', value=desc.get('purge'), inline=False)
        embed_var.add_field(name='bal', value=desc.get('bal'), inline=False)
        embed_var.add_field(name='leaderboard', value=desc.get('leaderboard'), inline=False)
        embed_var.add_field(name='gamble_coin', value=desc.get('gamble_coin'), inline=False)
        embed_var.add_field(name='gamble_wheel', value=desc.get('gamble_wheel'), inline=False)
        embed_var.add_field(name='gamble_black_jack', value=desc.get('gamble_black_jack'), inline=False)
        embed_var.set_footer(text="ask for more help on specific commands by using .help <command>")
        await ctx.channel.send(embed=embed_var)
    else:
        example = {
            'choose': '.choose go to work, play video games, something else',
            'coin_flip': '.coin_flip',
            'poll': '.poll Do you like nibbles?',
            'purge': '.purge 5',
            'bal': '.bal',
            'leaderboard': '.leaderboard',
            'gamble_coin': '.gamble_coin heads 160',
            'gamble_wheel': '.wheel',
            'gamble_black_jack': '.gamble_black_jack 160',
            'transfer': '.transfer @kit 160'
        }
        if desc.get(command, 'no such command') == 'no such command':
            await ctx.send('this command doesn\'t exist!')
        else:
            embed_var.add_field(name='Command name', value=command, inline=False)
            embed_var.add_field(name='Command description', value=desc.get(command, 'no such command'), inline=False)
            embed_var.add_field(name='Command usage', value=example.get(command, 'no such command'), inline=False)
            await ctx.channel.send(embed=embed_var)


@help.error
async def help_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await help(ctx, None)


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send("nom")
    if 'say it back' in message.content.lower() and message.author.id == 437033597803692033:
        await message.channel.send(random.choice("how about no, vincent", "no", "don't do it", ";-;"))
    else:
        await client.process_commands(message)


client.run('')
