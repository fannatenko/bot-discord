from telethon import TelegramClient, events
from telethon.tl.types import InputChannel
import yaml
import discord
import asyncio

message = []

with open('config.yml', 'rb') as f:
    config = yaml.safe_load(f)



"""
TELEGRAM CLIENT STUFF
"""
client = TelegramClient("forwardgram", config["api_id"], config["api_hash"])
client.start()

#Find input telegram channels
input_channels_entities = []

for d in client.iter_dialogs():
    if d.name in config["input_channel_names"]: #or d.entity.id in config["input_channel_id"]:
        print(d.entity.id, d.entity.access_hash)
        print(config["input_channel_names"])
        input_channels_entities.append( InputChannel(d.entity.id, d.entity.access_hash) )
      
        
if input_channels_entities == []:
    print("No input channels found, exiting")
    exit()


#TELEGRAM NEW MESSAGE
@client.on(events.NewMessage(chats=input_channels_entities))
async def handler(event):
    # If the message contains a URL, parse and send Message + URL
    try:
        parsed_response = (event.message.message + '\n' + event.message.entities[0].url )
        parsed_response = ''.join(parsed_response)
    # Or we only send Message    
    except:
        parsed_response = event.message.message

    globals()['message'].append(parsed_response)



"""
DISCORD CLIENT STUFF
"""
discord_client = discord.Client()

async def background_task():
    global message
    await discord_client.wait_until_ready()
    discord_channel = discord_client.get_channel(config["discord_channel"])
    while True:
        if message != []:
            await discord_channel.send(message[0])
            message.pop(0)
        await asyncio.sleep(0.1)

discord_client.loop.create_task(background_task())



"""
RUN EVERYTHING ASYNCHRONOUSLY
"""

print("Listening now")
asyncio.run( discord_client.run(config["discord_bot_token"]) )
asyncio.run( client.run_until_disconnected() )
