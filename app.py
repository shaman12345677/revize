from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import bcrypt
import os
from dotenv import load_dotenv

# Načtení proměnných prostředí
load_dotenv()

app = Flask(__name__)

# Bezpečnější CORS nastavení
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# Bezpečnostní hlavičky
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    return response

# Konfigurace Google Sheets API
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1XAFv60X9g_NaTOrJL_9gb67pFNw04cfLKJ01Zr98FC4')
SHEET_NAME = 'List 1'

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
except Exception as e:
    print(f"Chyba při inicializaci Google Sheets API: {str(e)}")
    raise

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'Revize backend běží',
        'endpoints': {
            'login': '/login',
            'get_revisions': '/get_revisions',
            'add_revision': '/add_revision',
            'edit_revision': '/edit_revision',
            'delete_revision': '/delete_revision',
            'get_revisions_school': '/get_revisions_school',
            'add_revision_school': '/add_revision_school',
            'edit_revision_school': '/edit_revision_school',
            'delete_revision_school': '/delete_revision_school',
            'get_users': '/get_users',
            'add_user': '/add_user',
            'edit_user': '/edit_user',
            'delete_user': '/delete_user'
        }
    })

@app.route('/add_revision', methods=['POST'])
def add_revision():
    data = request.json
    values = [[
        data['title'],
        data['lastDate'],
        data['nextDate'],
        data['intervalMonths'],
        data['daysToNext'],
        data['status'],
        data.get('company', ''),
        data.get('person', ''),
        data.get('email', ''),
        data.get('phone', '')
    ]]
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:J",
        valueInputOption="RAW",
        body=body
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/get_revisions', methods=['GET'])
def get_revisions():
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A2:J"
    ).execute()
    values = result.get('values', [])
    return jsonify({'revisions': values})

@app.route('/delete_revision', methods=['POST'])
def delete_revision():
    data = request.json
    row_index = data['row_index']
    requests = [{
        'deleteDimension': {
            'range': {
                'sheetId': 0,
                'dimension': 'ROWS',
                'startIndex': row_index + 1,
                'endIndex': row_index + 2
            }
        }
    }]
    result = sheet.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/edit_revision', methods=['POST'])
def edit_revision():
    data = request.json
    row_index = data['row_index']
    values = [[
        data['title'],
        data['lastDate'],
        data['nextDate'],
        data['intervalMonths'],
        data['daysToNext'],
        data['status'],
        data.get('company', ''),
        data.get('person', ''),
        data.get('email', ''),
        data.get('phone', '')
    ]]
    body = {
        'range': f"{SHEET_NAME}!A{row_index+2}:J{row_index+2}",
        'values': values
    }
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A{row_index+2}:J{row_index+2}",
        valueInputOption="RAW",
        body=body
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    print(f"Přihlašovací pokus pro uživatele: {username}")
    
    users_result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Uživatelé!A2:E"
    ).execute()
    users = users_result.get('values', [])
    
    print(f"Načteno uživatelů: {len(users)}")
    
    for row in users:
        if len(row) >= 3 and row[0].strip() == username:
            print(f"Nalezen uživatel: {username}")
            stored_salt = str(row[1]).strip()
            stored_hash = str(row[2]).strip()
            try:
                password_bytes = password.encode('utf-8')
                salt_bytes = stored_salt.encode('utf-8')
                new_hash = bcrypt.hashpw(password_bytes, salt_bytes)
                new_hash_str = new_hash.decode('utf-8')
                if stored_hash == new_hash_str:
                    print("Heslo je správné!")
                    role = row[3].strip() if len(row) > 3 and row[3].strip() else ('admin' if username == 'samekt' else 'user')
                    user_type = row[4].strip() if len(row) > 4 and row[4].strip() else 'školka'
                    return jsonify({'success': True, 'role': role, 'user_type': user_type})
                else:
                    print("Nesprávné heslo!")
            except Exception as e:
                print(f"Chyba při ověřování hesla: {str(e)}")
            break
    print("Přihlášení selhalo")
    return jsonify({'success': False, 'error': 'Nesprávné jméno nebo heslo.'}), 401

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'user').strip() if data.get('role') else 'user'
    user_type = data.get('user_type', 'školka').strip() if data.get('user_type') else 'školka'
    if role == 'admin':
        user_type = 'školka,škola'
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    values = [[
        username,
        salt.decode('utf-8'),
        hashed.decode('utf-8'),
        role,
        user_type
    ]]
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Uživatelé!A:E",
        valueInputOption="RAW",
        body=body
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/get_users', methods=['GET'])
def get_users():
    users_result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Uživatelé!A2:E"
    ).execute()
    users = users_result.get('values', [])
    user_objs = []
    for row in users:
        if row and len(row) >= 1:
            user_objs.append({
                'username': row[0],
                'role': row[3] if len(row) > 3 else 'user',
                'user_type': row[4] if len(row) > 4 else ''
            })
    return jsonify({'users': user_objs})

@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.json
    username = data.get('username', '').strip()
    users_result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Uživatelé!A2:E"
    ).execute()
    users = users_result.get('values', [])
    user_index = None
    for i, row in enumerate(users):
        if row and row[0] == username:
            user_index = i + 2
            break
    if user_index is None:
        return jsonify({'success': False, 'error': 'Uživatel nenalezen'}), 404
    result = sheet.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"Uživatelé!A{user_index}:E{user_index}"
    ).execute()
    return jsonify({'success': True})

@app.route('/edit_user', methods=['POST'])
def edit_user():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('password', '')
    new_role = data.get('role', 'user')
    new_user_type = data.get('user_type', 'školka')
    if new_role == 'admin':
        new_user_type = 'školka,škola'
    if not username:
        return jsonify({'success': False, 'error': 'Chybí uživatelské jméno.'}), 400
    
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Uživatelé!A2:E").execute()
    users = result.get('values', [])
    user_row = None
    for idx, row in enumerate(users):
        if len(row) > 0 and row[0] == username:
            user_row = idx + 2
            break
    if not user_row:
        return jsonify({'success': False, 'error': 'Uživatel nenalezen.'}), 404
    
    if new_password:
        salt = bcrypt.gensalt().decode()
        hash_ = bcrypt.hashpw(new_password.encode(), salt.encode()).decode()
    else:
        row = users[user_row-2]
        salt = row[1]
        hash_ = row[2]
    
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"Uživatelé!B{user_row}:E{user_row}",
        valueInputOption="RAW",
        body={"values": [[salt, hash_, new_role, new_user_type]]}
    ).execute()
    return jsonify({'success': True})

@app.route('/get_revisions_school', methods=['GET'])
def get_revisions_school():
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="List 2!A2:J"
    ).execute()
    values = result.get('values', [])
    return jsonify({'revisions': values})

@app.route('/add_revision_school', methods=['POST'])
def add_revision_school():
    data = request.json
    values = [[
        data['title'],
        data['lastDate'],
        data['nextDate'],
        data['intervalMonths'],
        data['daysToNext'],
        data['status'],
        data.get('company', ''),
        data.get('person', ''),
        data.get('email', ''),
        data.get('phone', '')
    ]]
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="List 2!A:J",
        valueInputOption="RAW",
        body=body
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/edit_revision_school', methods=['POST'])
def edit_revision_school():
    data = request.json
    row_index = data['row_index']
    values = [[
        data['title'],
        data['lastDate'],
        data['nextDate'],
        data['intervalMonths'],
        data['daysToNext'],
        data['status'],
        data.get('company', ''),
        data.get('person', ''),
        data.get('email', ''),
        data.get('phone', '')
    ]]
    body = {
        'range': f"List 2!A{row_index+2}:J{row_index+2}",
        'values': values
    }
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"List 2!A{row_index+2}:J{row_index+2}",
        valueInputOption="RAW",
        body=body
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/delete_revision_school', methods=['POST'])
def delete_revision_school():
    data = request.json
    row_index = data['row_index']
    requests = [{
        'deleteDimension': {
            'range': {
                'sheetId': 1,
                'dimension': 'ROWS',
                'startIndex': row_index + 1,
                'endIndex': row_index + 2
            }
        }
    }]
    result = sheet.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()
    return jsonify({'success': True, 'result': result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # V produkci vypnout debug mód
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 