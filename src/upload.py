import os
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials_path = 'src/client_secret.json'
if not os.path.exists(credentials_path):
    print("Error: src/client_secret.json not found. Please add your Google service account credentials.")
    exit(1)
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(credentials)
spreadsheet = client.open('Northstar Sims')

def ImportCsv(csvFile, sheet, tabname):
    wks = sheet.worksheet(tabname)

    with open(csvFile, "r") as f:
        csvContents = f.read()
    body = {
        "requests": [
            {
                "pasteData": {
                    "coordinate": {
                        "sheetId": wks.id,
                        "rowIndex": 0,
                        "columnIndex": 0,
                    },
                    "data": csvContents,
                    "type": "PASTE_NORMAL",
                    "delimiter": ",",
                }
            }
        ]
    }
    return sheet.batch_update(body)

def directoryFinder(dir):
    directory = dir

    # below loops each file in that directory.
    for filename in os.listdir(directory):
        print(directory)

        f = os.path.join(directory, filename)
        tabname = Path(f).stem
        # Checking if it is a file
        if os.path.isfile(f):
            worksheet = spreadsheet.worksheet(f'{tabname}')
            print("Trying to update: " + tabname)
            ImportCsv(f, spreadsheet, tabname)

if __name__ == '__main__':
    directoryFinder('src/raidsims')
