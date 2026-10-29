import gspread
from google.oauth2.service_account import Credentials

@st.cache_resource
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Kinukuha ang credentials nang direkta mula sa TOML table
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(credentials)

def get_sheet_data(worksheet_name):
    gc = get_gspread_client()
    sh = gc.open("MalolosJailDB")
    worksheet = sh.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def update_sheet_data(df, worksheet_name):
    gc = get_gspread_client()
    sh = gc.open("MalolosJailDB")
    worksheet = sh.worksheet(worksheet_name)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
