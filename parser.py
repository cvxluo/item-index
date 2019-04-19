from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
MONUMENTA_INDEX_ID = '1EZtImZ359RnuiKAVDqRVrkf39lVYyJ6IO7bvuf5ouXs'
REGION_1_SHEET = "Region 1 (King's Valley)" #:E"

def itemsFromSpreadsheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)






    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=MONUMENTA_INDEX_ID,
                                range=REGION_1_SHEET).execute()
    values = result.get('values', [])


    track = ['', '', '', '']#, '', '', '', '', '', '', '', '']

    items = []

    if not values:
        print('No data found.')
    else:
        for row in values:

            if (len(row) < 10) :
                for i in range(10 - len(row)) :
                    row.append('')

            if not (row[0]) :
                row[0] = track[0]
            else :
                track[0] = row[0]

            if not (row[1]) :
                row[1] = track[1]
            else :
                track[1] = row[1]

            if not (row[2]) :
                row[2] = track[2]
            else :
                track[2] = row[2]

            if not (row[3]) :
                row[3] = track[3]
            else :
                track[3] = row[3]

            for i in range(len(row)) :
                row[i] = row[i].strip()



            items.append(row)

    return items

if __name__ == '__main__':
    main()
