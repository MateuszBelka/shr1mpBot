# Authors:   Mateusz Belka, Emil Andrzejewski
# Created:  11-Jul-2020
from cogs.aws import Aws
from util import aws


async def clear(ctx, number):
    # Clears 'number' of messages in the channel that the command has been sent
    await ctx.channel.purge(limit=number)


async def reset_channel(ctx):
    name = ctx.channel.name
    guild = ctx.channel.guild

    await delete_channel(ctx)
    await create_new_channel(name, guild)


async def delete_channel(ctx):
    await ctx.channel.delete()


async def create_new_channel(name, guild):
    return await guild.create_text_channel(name)


async def perror(ctx, msg):
    final_msg = "ERROR: " + msg + "!"
    await ctx.send(final_msg)


async def aws_all_servers_status(client):
    awsChannel = None
    for guild in client.guilds:
        if (guild.name == "SHR1PM") or (guild.name == "shr1mpBot test"):
            for aws_channel_name in Aws.supported_channels:
                for guild_channel in guild.channels:
                    if guild_channel.name == aws_channel_name:
                        awsChannel = guild_channel
                        break

                if awsChannel is not None:
                    await purge(awsChannel)
                else:
                    awsChannel = await create_new_channel(aws_channel_name, guild)

                await aws_server_status_message_known_channel(awsChannel)
                awsChannel = None


async def aws_server_status_message_known_channel(channel):
    if channel is not None:
        print("{} server status: {}!".format(Aws.channel_game_map[channel.name], aws.get_state(channel).upper()))
        await channel.send("{} server status: **{}**!".format(Aws.channel_game_map[channel.name], aws.get_state(channel).upper()))


async def purge(channel):
    await channel.purge()
