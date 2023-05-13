import gspread
import os
import time
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('src/client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet_normal = client.open('Northstar Sims Normal')
spreadsheet_heroic = client.open('Northstar Sims Heroic')
spreadsheet_mythic = client.open('Northstar Sims Mythic')


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
    difficulty = directory.split('_')[1]
    if difficulty == "normal": 
        spreadsheet = spreadsheet_normal
    elif difficulty == "heroic":
        spreadsheet = spreadsheet_heroic   
    elif difficulty == "mythic": 
        spreadsheet = spreadsheet_mythic

    # below loops each file in that directory.
    for filename in os.listdir(directory):
        print(directory)

        f = os.path.join(directory, filename)
        tabname = Path(f).stem
        # Checking if it is a file
        if os.path.isfile(f):
            # Creating the new spreadsheet tab
            # print(spreadsheet.worksheet(f'{filename}'))
            worksheet = spreadsheet.worksheet(f'{tabname}')
            # else :
            #     print("Aint working")
            #     worksheet = spreadsheet.add_worksheet(f'{filename}', rows = 1000, cols = 100)

            print("Trying to update: " + tabname)
            ImportCsv(f, spreadsheet, tabname)

        
if __name__ == '__main__':
    directoryFinder('src/generated_heroic')
    time.sleep(60)
    directoryFinder('src/generated_mythic')
    time.sleep(60)
    directoryFinder('src/generated_normal')


            
