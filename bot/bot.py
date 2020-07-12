import boto3
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

from aws import factorio_server, util
from util import messages

load_dotenv(find_dotenv())
TOKEN = os.environ.get("TOKEN")
INSTANCE_ID = os.environ.get("INSTANCE_ID")

client = commands.Bot(command_prefix='$')  # When typing bot commands, always start with '!'
client.remove_command('help')

ec2 = boto3.resource('ec2')
instance = ec2.Instance(INSTANCE_ID)

@client.event
async def on_ready():
    print('Logged in as')
    print('Name: {}'.format(client.user.name))
    print('ID: {}'.format(client.user.id))
    print('Factorio server status: {}!'.format(util.get_state()))
    print('------------')
    factorio_channel = await messages.clear_factorio_text_channel(client)
    await messages.factorio_welcome_message(factorio_channel)
    await factorio_channel.send(embed=messages.help_embed())


@client.event
async def on_member_join(member, context):
    await context.send(f'{member} joined the SHR1MP Clan!')
    # print jest do terminala a nie do discorda
    # ciebie interesuje chyba context.send(string)


@client.event
async def on_member_remove(member):
    print(f'{member} left the SHR1MP Clan...')
    # print jest do terminala a nie do discorda
    # ciebie interesuje chyba context.send(string)


@client.event
async def on_command_error(ctx, e):
    if isinstance(e, commands.CommandNotFound):
        await messages.perror(ctx, "Invalid command used")


@client.command()
async def help(context):
    author = context.message.author
    await author.send(embed=messages.help_embed())
    await messages.clear(context, 1)


@client.command()
async def shrimp(ctx):
    await ctx.send(f'shromp (latency: {round(client.latency * 1000)} ms)')


@client.command(aliases=['8ball', 'przepowiednia'])
async def _8ball(ctx, *, question):
    responses = ['+1 byczku',
                 '+0.7 byczku',
                 'Si si toro',
                 'To jest niemozliwe do przewidzenia',
                 'Ooooj tak',
                 'Nie ma chuja',
                 'Ta ta jasne',
                 'We zapytaj jeszcze raz',
                 'Matematyczna szansa']
    await ctx.send(f'{random.choice(responses)}')


@client.command()
async def factorio_on(context):
    if util.get_state() == "stopped":
        await factorio_server.turn_on_instance(context, instance)
    elif util.get_state() == "running":
        await context.send("Factorio server is already **ONLINE**!")
    else:
        await messages.perror(context, "Server is either being turned off or on right now. Wait")


@client.command()
async def factorio_off(context):
    if util.get_state() == "running":
        await factorio_server.turn_off_instance(context, instance)
    elif util.get_state() == "stopped":
        await context.send("Factorio server is already **OFFLINE**!")
    else:
        await messages.perror(context, "Server is either being turned off or on right now. Wait")


@client.command()
async def factorio_status(context):
    channel = context.channel
    await messages.purge(channel)
    await util.send_state_message(channel, "Factorio")


@client.command()
async def clear(context, number: int):
    await messages.clear(context, number + 1)


@client.command()
async def nuke(context):
    return await messages.reset_channel(context, discord)

@client.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)

@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Zbanowano {member.mention}')

@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if(user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Odbanowano {user.mention}')
            return

client.run(TOKEN)
