# Author:   Mateusz Belka
# Created:  13-Jul-2020
import os
import boto3
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

from util import messages, aws_instance_state, aws


class Aws(commands.Cog):
    load_dotenv(find_dotenv())
    ec2 = boto3.resource('ec2')
    factorio_instance = ec2.Instance(os.environ.get("INSTANCE_ID_FACTORIO"))
    minecraft_vanilla_instance = ec2.Instance(os.environ.get("INSTANCE_ID_MINECRAFT"))
    terraria_instance = ec2.Instance(os.environ.get("INSTANCE_ID_TERRARIA"))

    supported_channels = ["bot-factorio", "bot-minecraft-vanilla", "bot-terraria"]
    channel_game_map = {"bot-factorio": "Factorio",
                        "bot-minecraft-vanilla": "Minecraft",
                        "bot-terraria": "Terraria"}
    channel_instance_map = {"bot-factorio": factorio_instance,
                            "bot-minecraft-vanilla": minecraft_vanilla_instance,
                            "bot-terraria": terraria_instance}

    def __init__(self, client):
        self.client = client

    async def is_proper_server_cmd_length(self, ctx, *cmds):
        if len(cmds) != 1:
            print("Wrong number of arguments")
            await messages.perror(ctx, "Wrong number of arguments")
            return False
        print("Correct number of arguments")
        return True

    def is_proper_discord_channel(self, ctx):
        channel_name = ctx.channel.name
        if channel_name in self.supported_channels:
            return True
        return False

    # Commands
    @commands.command()
    async def server(self, ctx, *cmds):
        print("\nProcessing server command")
        if not await self.is_proper_server_cmd_length(ctx, *cmds):
            return
        if not self.is_proper_discord_channel(ctx):
            return

        if 'on' in cmds or 'start' in cmds:
            print("Turning the server on!")
            await self.server_start(ctx)
        elif 'off' in cmds or 'stop' in cmds:
            print("Turning the server off!")
            await self.server_stop(ctx)
        elif 'status' in cmds:
            print("Checking server status!")
            await messages.aws_server_status_message_known_channel(ctx.channel)
        else:
            await messages.perror(ctx, "Try: $server + {on, start, off, stop, status}")

    async def server_start(self, ctx):
        if aws.get_state(ctx.channel) == "stopped":
            await aws_instance_state.turn_on_instance(ctx, self.channel_instance_map[ctx.channel.name])
        elif aws.get_state(ctx.channel) == "running":
            await ctx.send("The {} server is already **ONLINE**!".format(self.channel_game_map[ctx.channel.name].lower()))
        else:
            await messages.perror(ctx, "Server is either being turned off or on right now. Wait")

    async def server_stop(self, ctx):
        if aws.get_state(ctx.channel) == "running":
            await aws_instance_state.turn_off_instance(ctx, self.channel_instance_map[ctx.channel.name])
        elif aws.get_state(ctx.channel) == "stopped":
            await ctx.send("The {} server is already **OFFLINE**!".format(self.channel_game_map[ctx.channel.name].lower()))
        else:
            await messages.perror(ctx, "Server is either being turned off or on right now. Wait")


def setup(client):
    client.add_cog(Aws(client))