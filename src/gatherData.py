import os
from dotenv import load_dotenv
import glob
import csv
import numpy as np
import pandas as pd
import json
import discord
import asyncio
import time
from pathlib import Path
from datetime import datetime


load_dotenv('src/.env')

# Get the token and channel IDs from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_ID_HC = os.getenv('CHANNEL_ID_HC')
CHANNEL_ID_NORMAL = os.getenv('CHANNEL_ID_NORMAL')

# If any of the values is not available, use the fallback values
if BOT_TOKEN is None:
    BOT_TOKEN = ''
if CHANNEL_ID is None:
    CHANNEL_ID = ''
if CHANNEL_ID_HC is None:
    CHANNEL_ID_HC = ''
if CHANNEL_ID_NORMAL is None:
    CHANNEL_ID_NORMAL = ''

# Set up Discord client with intents to access members
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

def parse_filename(filename):
    """Parses the filename and extracts the name and specialization"""
    parts = filename.split("_")
    if len(parts) == 2:
        name = parts[0].lower()
        specialization = parts[1].lower().split(".")[0]
        if specialization in ["blood", "frost", "unholy", "havoc", "vengeance", "balance", "feral", "guardian", "restoration", "beastmastery", "marksmanship", "survival", "arcane", "fire", "frost", "brewmaster", "mistweaver", "windwalker", "holy", "protection", "retribution", "discipline", "shadow", "assassination", "outlaw", "subtlety", "elemental", "enhancement", "restoration", "affliction", "demonology", "destruction", "arms", "fury", "protection", "preservation", "devastation"]:
            return name, specialization
    return None, None

async def download_files(channel, filename_prefix):
    """Downloads CSV files attached to messages in a Discord channel"""
    print(channel)
    async for message in channel.history():
        try:
            if message.attachments:
                for attachment in message.attachments:
                    filename = attachment.filename
                    print(filename)
                    if filename.endswith('.csv'):
                        name, specialization = parse_filename(filename)
                        if name is not None and specialization is not None:
                            new_filename = f'{name}_{specialization}.csv'
                            row_name = f'{name}_{specialization}'
                            await attachment.save(f'src/{filename_prefix}_data/{new_filename}')
                            await replace_second_row(f'src/{filename_prefix}_data/{new_filename}', row_name)
                            await message.delete()
                        else:
                            user = message.author.mention
                            await channel.send(f"{user}, the format of the filename '{filename}' is incorrect. Please use the following way of naming the file: NAME_SPECIALIZATION")
        except discord.errors.NotFound:
            # Handle the exception here, such as logging the error or skipping the current message
            print(f"Error: Message not found - {message.id}")
            print("Retrying in 10 seconds...")
            time.sleep(10)  # Delay for 10 seconds before retrying

async def replace_second_row(filepath, filename):
    """Replaces the second row in the first column of a CSV file with the given filename"""
    with open(filepath, 'r', newline='', encoding='utf-8') as file:
        data = list(csv.reader(file))
        if len(data) > 1:
            data[1][0] = filename

    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

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
    file = glob.glob('static_data/formatted_itemdata.json', recursive=True)
    with open(file) as boss_file:
        file_contents = boss_file.read()
    parsed_json = json.loads(file_contents)
    df = pd.DataFrame.from_records(parsed_json['drops'])
    for player in players:
        df[[player['name']]] = 0
        df = df.set_index('id')
        for item in player['simmed_items']:
            item_id = item['item_id']
            gain = item['gain']
            if int(item_id) in df.index:
                current_gain = df.loc[int(item_id), player['name']]
                if gain > current_gain:
                    df.loc[int(item_id), player['name']] = gain
            else:
                print("")
        df = df.reset_index()
    df = df.transpose()
    df.to_csv(f"src/generated_{filename_prefix}/{parsed_json['name']}.csv")
    # print(df)
@client.event
async def on_ready():
    """Main event loop that downloads files, loads data and creates CSVs"""
    print('Bot is ready')
    channel = await client.fetch_channel(CHANNEL_ID) # Mythic Sims
    await download_files(channel, "mythic")
    json_loader("mythic")

    await asyncio.sleep(5)
    
    channel_HC = await client.fetch_channel(CHANNEL_ID_HC) # Heroic Sims
    await download_files(channel_HC, "heroic")
    json_loader("heroic")
    
    await asyncio.sleep(5)

    channel_NORMAL = await client.fetch_channel(CHANNEL_ID_NORMAL) # Heroic Sims
    await download_files(channel_NORMAL, "normal")
    json_loader("normal")
    
    await asyncio.sleep(5)

    

if __name__ == '__main__':
    today = datetime.now().strftime("%d/%m/%Y %H:%M")
    client.run(BOT_TOKEN)