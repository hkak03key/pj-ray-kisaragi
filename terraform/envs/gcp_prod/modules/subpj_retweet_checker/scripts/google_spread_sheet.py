import googleapiclient.discovery
import google.auth


SPREADSHEET_ID = "1ynw1Ytf3pckZIPykhM5eLPguTJnj3PUAC8PwBBLTQC8"

SHEET_NAME_FOR_BUILDING = "system_for_building"
SHEET_RANGE_FOR_BUILDING = "{}!A:C".format(SHEET_NAME_FOR_BUILDING)

SHEET_NAME_FOR_RESULTS = "results"

credentials, pj_id = google.auth.default()
service = googleapiclient.discovery.build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False
    )


def collect_spreadsheet_infos(spreadsheet_id):
    response = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute() \
        .get("sheets")
    return {r["properties"].get("title", "Sheet1"): r["properties"] for r in response}

def clear_sheet_using_delete_range(spreadsheet_id, sheet_name):
    spreadsheet_infos = collect_spreadsheet_infos(spreadsheet_id)

    request = {
        "deleteRange": {
            "range": {
                "sheetId": spreadsheet_infos[sheet_name]["sheetId"],
                "startRowIndex": 0,
                "endRowIndex": spreadsheet_infos[sheet_name]["gridProperties"]["rowCount"],
                "startColumnIndex": 0,
                "endColumnIndex": spreadsheet_infos[sheet_name]["gridProperties"]["columnCount"]
            },
            "shiftDimension": "ROWS",
            }
    }
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body = {"requests": [request]}
    ).execute()

    print("end: clear sheet \"{}\"".format(sheet_name))


def overwrite_sheet(spreadsheet_id, src_sheet_name, dst_sheet_name):
    spreadsheet_infos = collect_spreadsheet_infos(spreadsheet_id)

    clear_sheet_using_delete_range(spreadsheet_id, dst_sheet_name)

    request = {
        "copyPaste": {
            "source": {
                "sheetId": spreadsheet_infos[src_sheet_name]["sheetId"],
                "startRowIndex": 0,
                "endRowIndex": spreadsheet_infos[src_sheet_name]["gridProperties"]["rowCount"],
                "startColumnIndex": 0,
                "endColumnIndex": spreadsheet_infos[src_sheet_name]["gridProperties"]["columnCount"]
            },
            "destination": {
                "sheetId": spreadsheet_infos[dst_sheet_name]["sheetId"],
                "startRowIndex": 0,
                "endRowIndex": spreadsheet_infos[dst_sheet_name]["gridProperties"]["rowCount"],
                "startColumnIndex": 0,
                "endColumnIndex": spreadsheet_infos[dst_sheet_name]["gridProperties"]["columnCount"]
            },
            "pasteType": "PASTE_NORMAL",
            "pasteOrientation": "NORMAL"
        }
    }
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body = {"requests": [request]}
    ).execute()

    print("end: copy/paste sheet \"{}\" to \"{}\"".format(src_sheet_name, dst_sheet_name))


def build_sheet(tweets, is_new):
    values = []
    if is_new:
        print("flag: is_new is True")
        clear_sheet_using_delete_range(SPREADSHEET_ID, SHEET_NAME_FOR_BUILDING)
        values.append(["tweet_date", "tweet_id", "username"])

    values.extend(sum([
        [
            [
                tweet["tweet_date"],
                tweet["tweet_id"],
                username
            ] for username in tweet["usernames"]
        ]
        for tweet in tweets
    ], []))

    body = {
        "values": values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE_FOR_BUILDING,
        valueInputOption="USER_ENTERED", 
        body=body).execute()

    print("end: build sheet")


def edit_spreadsheet(tweets, is_new, is_final):
    build_sheet(tweets, is_new)

    if is_final:
        print("flag: is_final is True")
        overwrite_sheet(SPREADSHEET_ID, SHEET_NAME_FOR_BUILDING, SHEET_NAME_FOR_RESULTS)

    print("end: edit spreadsheet")

