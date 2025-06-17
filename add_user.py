import bcrypt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Nastavení
SPREADSHEET_ID = '1XAFv60X9g_NaTOrJL_9gb67pFNw04cfLKJ01Zr98FC4'  # Změň na své ID
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Cesta k tvému service account JSON

# Uživatelské údaje
username = 'samekt'
password = 'shaman'
role = 'admin'
typ = 'školka,škola'

# Vygeneruj salt a hash
salt = bcrypt.gensalt().decode()
hash_ = bcrypt.hashpw(password.encode(), salt.encode()).decode()
print('Salt:', salt)
print('Hash:', hash_)

# Připojení ke Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet('Uživatelé')

# Najdi řádek pro uživatele nebo přidej nový
users = sheet.col_values(1)
if username in users:
    row = users.index(username) + 1
    sheet.update_cell(row, 2, salt)
    sheet.update_cell(row, 3, hash_)
    sheet.update_cell(row, 4, role)
    sheet.update_cell(row, 5, typ)
    print(f"Uživatel {username} aktualizován.")
else:
    sheet.append_row([username, salt, hash_, role, typ])
    print(f"Uživatel {username} přidán.")

print('Hotovo!') 