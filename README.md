# Droptimizer Loot

A Discord bot that collects Raidbots droptimizer sim CSVs from your raid members, calculates item gain values per player, and outputs a ranked loot spreadsheet.

## Requirements

- Python 3.6+
- Install dependencies: `pip install -r src/requirements.txt`

## Installation

```bash
git clone https://github.com/aritonkaramani/droptimizer-loot.git
cd droptimizer-loot
python -m venv myenv
source myenv/bin/activate
pip install -r src/requirements.txt
```

## Configuration

Create `src/.env` with the following:

```
BOT_TOKEN=your_discord_bot_token
CHANNEL_ID=mythic_sims_channel_id
CHANNEL_ID_HC=heroic_sims_channel_id
CHANNEL_ID_NORMAL=normal_sims_channel_id
```

Add `src/client_secret.json` with your Google service account credentials for uploading to Google Sheets.

Make sure the Discord bot has permissions to read messages, download attachments, send messages, and delete messages in the sim channels.

## Workflow

### 1. Setup (once per raid tier)

```bash
python src/setup.py
```

You will be prompted for:

- **Zone ID(s)** — comma-separated IDs of the raid instance(s) from Raidbots
- **Expansion number** — for catalyst tier pieces (e.g. `11` for the new raid)

This downloads item data from Raidbots and builds `static_data/formatted_itemdata.json`.

### 2. Collect player sim data

Have raid members upload their Raidbots droptimizer CSVs to the designated Discord channels. Files must be named:

```
NAME_SPECIALIZATION.csv
```

Valid specializations: `blood`, `frost`, `unholy`, `havoc`, `vengeance`, `balance`, `feral`, `guardian`, `restoration`, `beastmastery`, `marksmanship`, `survival`, `arcane`, `fire`, `brewmaster`, `mistweaver`, `windwalker`, `holy`, `protection`, `retribution`, `discipline`, `shadow`, `assassination`, `outlaw`, `subtlety`, `elemental`, `enhancement`, `affliction`, `demonology`, `destruction`, `arms`, `fury`, `preservation`, `devastation`, `augmentation`

### 3. Run the bot

```bash
python src/gatherData.py
```

The bot downloads all CSVs, processes item gain values, and writes output to `src/raidsims/`.

### 4. Upload to Google Sheets

```bash
python src/upload.py
```

## Support

Reach out to Ari03024 on Discord.
