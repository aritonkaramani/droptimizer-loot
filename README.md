# Discord CSV Downloader

This script is designed to download CSV files attached to messages in Discord channels and process them to generate output files. Before running the script, there are a few important things to know:

## Requirements

- Python 3.6 or higher
- Required Python packages can be installed using `pip install -r requirements.txt`
- Discord.py library (can be installed via `pip install discord.py`)
- Numpy library (can be installed via `pip install numpy`)
- Pandas library (can be installed via `pip install pandas`)
- dotenv library (can be installed via `pip install python-dotenv`)

## Installation

1. Clone the repository:

   ```bash
    git clone https://github.com/aritonkaramani/droptimizer-loot.git
   ```

2. Navigate to the project directory:
    ```
    cd droptimizer-loot
    ```

3. Create and activate a virtual environment (optional but recommended):
    ```
    python -m venv venv
    source venv/bin/activate
    ```
4. Install the required dependencies
    ```
    pip install -r requirements.txt
    ```

## Setup

1. Obtain a Discord bot token:
   - Create a new application in the Discord Developer Portal (https://discord.com/developers/applications)
   - Under the "Bot" section, click on "Add Bot" to create a bot for your application
   - Copy the bot token

2. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Define the following environment variables in the `.env` file:
     - `BOT_TOKEN`: Set it to the bot token you obtained in the previous step
     - `CHANNEL_ID`: Set it to the channel ID where the mythic sims CSV files will be downloaded from
     - `CHANNEL_ID_HC`: Set it to the channel ID for heroic sims
     - `CHANNEL_ID_NORMAL`: Set it to the channel ID for normal sims

3. Prepare the file structure:
   - Create the following directories relative to the script file:
     - `src/mythic_data`
     - `src/heroic_data`
     - `src/normal_data`
     - `src/generated_mythic`
     - `src/generated_heroic`
     - `src/generated_normal`
   - Make sure you have write permissions for these directories

## Usage

1. Run the script:
   - Open a command prompt or terminal
   - Navigate to the directory containing the script file
   - Run the script using the command `python gatherData.py`

2. Discord bot setup:
   - Make sure the Discord bot is invited to the channels where the CSV files are located
   - Ensure the bot has appropriate permissions to read messages, download attachments, and send messages

3. CSV file naming convention:
   - The CSV files must follow a specific naming convention: `NAME_SPECIALIZATION.csv`
   - `NAME` should be replaced with the player's name
   - `SPECIALIZATION` should be replaced with the player's specialization. Important to know it has to be one of the valid specializations.
   - Valid specializations include: `blood`, `frost`, `unholy`, `havoc`, `vengeance`, `balance`, `feral`, `guardian`, `restoration`, `beastmastery`, `marksmanship`, `survival`, `arcane`, `fire`, `frost`, `brewmaster`, `mistweaver`, `windwalker`, `holy`, `protection`, `retribution`, `discipline`, `shadow`, `assassination`, `outlaw`, `subtlety`, `elemental`, `enhancement`, `restoration`, `affliction`, `demonology`, `destruction`, `arms`, `fury`, `protection`, `preservation`, `devastation`

4. Uploading CSV files:
   - Attach the CSV files to messages in the designated Discord channels
   - The bot will automatically download the attached CSV files and process them

5. Output files:
   - The processed data will be saved as CSV files in the `src/generated_mythic` and `src/generated_heroic` directories
   - The output files will be named based on the boss names

6. Other considerations:
   - The script will replace the second row in the first column of each downloaded CSV file with the corresponding filename

## Support

If you encounter any issues or have any questions, please feel free to reach out to Ari at [Ari#3533] (Discord).

## Acknowledgements

This script was developed by Ari. Special thanks to the following resources:

- Discord.py documentation: [https://discordpy.readthedocs.io](https://discordpy.readthedocs.io)
- Numpy documentation: [https://numpy.org/doc](https://numpy.org/doc)
- Pandas documentation: [https://pandas.pydata.org/docs](https://pandas.pydata.org/docs)

## License

This project is licensed under the [MIT License](LICENSE).
