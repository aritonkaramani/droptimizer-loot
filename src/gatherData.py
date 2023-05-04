import glob
import csv
import numpy as np
import pandas as pd
import json
import discord
import asyncio
from pathlib import Path
from datetime import datetime

# Set up Discord client with intents to access members
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

async def download_files(channel, filename_prefix):
    """Downloads CSV files attached to messages in a Discord channel"""
    print(channel)
    async for message in channel.history():
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.endswith('.csv'):
                    filename = f'{filename_prefix}_{attachment.filename}'
                    await attachment.save(f'src/{filename_prefix}_data/{filename}')
                    # await message.delete()

def json_loader(filename_prefix):
    """Loads data from downloaded CSV files into a list of dictionaries"""
    global players
    players = []
    files = glob.glob(f'src/{filename_prefix}_data/*.csv', recursive=True)
    for file in files:
        player_count = 0
        with open(file, 'r') as f:
            try:
                csv_reader = csv.DictReader(f)
                line_count = 0
                for row in csv_reader:
                    if (line_count == 0):
                        players.insert(0,
                                      dict({
                                          'name': row['name'],
                                          'sim_dps': row['dps_mean'],
                                          'simmed_items': []
                                      }))
                        line_count += 1
                    else:
                        line_count += 1
                        players[player_count]['simmed_items'].append(dict({
                            'item_id': row['name'].split("/", 3)[-1].split("/",1)[-2],
                            'gain': -np.round(float(players[player_count]['sim_dps']) - float(row['dps_mean'])),
                        }))
            except KeyError:
                print(f'Skipping {file}')
        player_count += 1
    create_csv(filename_prefix)

def create_csv(filename_prefix):
    """Creates a CSV file for each boss with simmed data for each player"""
    files = glob.glob('static_data/*.json', recursive=True)
    for file in files:
        with open(file) as boss_file:
            file_contents = boss_file.read()
        parsed_json = json.loads(file_contents)
        df = pd.DataFrame.from_records(parsed_json['drops'])
        for player in players:
            df[[player['name']]] = 0
            df = df.set_index('id')
            for item in player['simmed_items']:
                    if int(item['item_id']) in df.index:
                        print("MATCH")
                        df.loc[int(item['item_id']), player['name']] = item['gain'] if item['gain'] > 0 else 0
                    else:
                        print("Item not in loot table")
            df = df.reset_index()
        df = df.transpose()
        df.to_csv(f"src/generated_{filename_prefix}/{parsed_json['name']}.csv")
        print(df)

@client.event
async def on_ready():
    """Main event loop that downloads files, loads data and creates CSVs"""
    print('Bot is ready')
    channel = await client.fetch_channel(CHANNEL_ID) # Mythic Sims
    await download_files(channel, "mythic")
    json_loader("mythic")
    await channel.send(f"Last checked: {today}")

    await asyncio.sleep(1)
    
    channel_HC = await client.fetch_channel(CHANNEL_ID_HC) # Heroic Sims
    await download_files(channel_HC, "heroic")
    json_loader("heroic")
    await channel_HC.send(f"Last checked: {today}")
    
    await asyncio.sleep(1)
    

if __name__ == '__main__':
    today = datetime.now().strftime("%d/%m/%Y %H:%M")
    CHANNEL_ID=""
    CHANNEL_ID_HC=""
    BOT_TOKEN=""
    client.run(BOT_TOKEN)