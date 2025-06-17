from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import bcrypt
import os
from dotenv import load_dotenv
import logging
import sys

# Nastavení logování
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/output.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

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
    logging.debug(f"Request headers: {dict(request.headers)}")
    logging.debug(f"Response headers: {dict(response.headers)}")
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
def index():
    logging.info("Root endpoint called")
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running',
        'endpoints': {
            'login': '/login',
            'test': '/test',
            'add_user': '/add_user',
            'get_revisions': '/get_revisions',
            'add_revision': '/add_revision',
            'update_revision': '/update_revision',
            'delete_revision': '/delete_revision'
        }
    })

@app.route('/test', methods=['GET'])
def test():
    logging.info("Test endpoint called")
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/add_revision', methods=['POST'])
def add_revision():
    data = request.json
    values = [[
        data['title'],
        data['lastDate'],
        data['nextDate'],
        data['intervalMonths'],
        data['status'],
        data.get('company', ''),
        data.get('person', ''),
        data.get('email', ''),
        data.get('phone', '')
    ]]
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:D,F:J",
        valueInputOption="RAW",
        body={'values': values}
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
    # Zápis A-D
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A{row_index+2}:D{row_index+2}",
        valueInputOption="RAW",
        body={'values': [[data['title'], data['lastDate'], data['nextDate'], data['intervalMonths']]]}
    ).execute()
    # Zápis F-J
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!F{row_index+2}:J{row_index+2}",
        valueInputOption="RAW",
        body={'values': [[data['status'], data.get('company', ''), data.get('person', ''), data.get('email', ''), data.get('phone', '')]]}
    ).execute()
    return jsonify({'success': True})

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        logging.debug("OPTIONS request received")
        return '', 200
        
    try:
        logging.info("Login attempt received")
        logging.debug(f"Request headers: {dict(request.headers)}")
        
        if not request.is_json:
            logging.error("Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        logging.debug(f"Login data: {data}")
        
        if not data or 'username' not in data or 'password' not in data:
            logging.error("Missing username or password in request")
            return jsonify({'error': 'Chybí uživatelské jméno nebo heslo'}), 400

        username = data['username']
        password = data['password']
        
        logging.info(f"Attempting login for user: {username}")

        # Inicializace Google Sheets API
        try:
            credentials = service_account.Credentials.from_service_account_file(
                'service_account.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            service = build('sheets', 'v4', credentials=credentials)
            logging.debug("Google Sheets API initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Google Sheets API: {str(e)}")
            return jsonify({'error': 'Chyba při připojení k Google Sheets'}), 500
        
        # Načtení uživatelů
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=os.getenv('SPREADSHEET_ID'),
                range='Uživatelé!A2:E'
            ).execute()
            
            users = result.get('values', [])
            logging.info(f"Found {len(users)} users in sheet")
        except Exception as e:
            logging.error(f"Failed to fetch users from sheet: {str(e)}")
            return jsonify({'error': 'Chyba při načítání uživatelů'}), 500
        
        # Kontrola přihlašovacích údajů
        for user in users:
            if len(user) >= 3 and user[0] == username:
                stored_salt = user[1]
                stored_hash = user[2]
                try:
                    password_bytes = password.encode('utf-8')
                    salt_bytes = stored_salt.encode('utf-8')
                    new_hash = bcrypt.hashpw(password_bytes, salt_bytes).decode()
                    if stored_hash == new_hash:
                        logging.info(f"Successful login for user: {username}")
                        role = user[3] if len(user) > 3 and user[3].strip() else ('admin' if username == 'samekt' else 'user')
                        user_type = user[4] if len(user) > 4 and user[4].strip() else 'školka'
                        return jsonify({'success': True, 'username': username, 'role': role, 'user_type': user_type})
                    else:
                        logging.warning(f"Invalid password for user: {username}")
                        return jsonify({'error': 'Nesprávné heslo'}), 401
                except Exception as e:
                    logging.error(f"Error checking password: {str(e)}")
                    return jsonify({'error': 'Chyba při ověřování hesla'}), 500
        
        logging.warning(f"User not found: {username}")
        return jsonify({'error': 'Uživatel nenalezen'}), 401
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Chyba při přihlašování: {str(e)}'}), 500

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
        data['status'],
        data.get('company', ''),
        data.get('person', ''),
        data.get('email', ''),
        data.get('phone', '')
    ]]
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="List 2!A:D,F:J",
        valueInputOption="RAW",
        body={'values': values}
    ).execute()
    return jsonify({'success': True, 'result': result})

@app.route('/edit_revision_school', methods=['POST'])
def edit_revision_school():
    data = request.json
    row_index = data['row_index']
    # Zápis A-D
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"List 2!A{row_index+2}:D{row_index+2}",
        valueInputOption="RAW",
        body={'values': [[data['title'], data['lastDate'], data['nextDate'], data['intervalMonths']]]}
    ).execute()
    # Zápis F-J
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"List 2!F{row_index+2}:J{row_index+2}",
        valueInputOption="RAW",
        body={'values': [[data['status'], data.get('company', ''), data.get('person', ''), data.get('email', ''), data.get('phone', '')]]}
    ).execute()
    return jsonify({'success': True})

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