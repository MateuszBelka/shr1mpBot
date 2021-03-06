# Author:   Mateusz Belka
# Created:  11-Jul-2020
import cogs.aws
import boto3
from util import aws


async def turn_off_instance(channel, instance):
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')

    # Stop the instance
    client.stop_instances(InstanceIds=[instance])
    await aws.server_state_change_update(channel, "stopped")

    # change instance types
    if ec2.Instance(instance).instance_type != "t2.micro":
        print("Initiating Instance Type change")
        client.modify_instance_attribute(InstanceId=instance, Attribute='instanceType', Value='t2.micro')
        print("{} server now has {} type".format(cogs.aws.Aws.channel_game_map[channel.name],
                                                 ec2.Instance(instance).instance_type))


async def turn_on_instance(channel, instance):
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    if (channel.name in cogs.aws.Aws.t2small_instance_channels) and (ec2.Instance(instance).instance_type != "t2.small"):
        print("Initiating Instance Type change")

        # change instance types
        client.modify_instance_attribute(InstanceId=instance, Attribute='instanceType', Value='t2.small')
        print("{} server now has {} type".format(cogs.aws.Aws.channel_game_map[channel.name],
                                                 ec2.Instance(instance).instance_type))

    # Start the instance
    client.start_instances(InstanceIds=[instance])
    await aws.server_state_change_update(channel, "running")
    if channel.name == "bot-minecraft-vanilla":
        await aws.turn_off_mcserver_check_loop(channel)


async def reboot_instance(channel, instance):
    client = boto3.client('ec2')
    client.reboot_instances(InstanceIds=[instance])
    await aws.server_state_change_update(channel, "running")
