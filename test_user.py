import bcrypt
import requests
import json

def create_test_user():
    username = "test4"
    password = "abc123"
    
    # Vygeneruj salt a hash hesla
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    salt_str = salt.decode('utf-8')
    hashed_str = hashed.decode('utf-8')
    
    print(f"Vytvářím testovacího uživatele:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Salt: {salt_str}")
    print(f"Hash: {hashed_str}")
    
    # Přidej uživatele do Google Sheetu
    data = {
        'username': username,
        'password': password  # Heslo se zahashuje na backendu
    }
    
    response = requests.post(
        'http://127.0.0.1:5000/add_user',
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print("Testovací uživatel byl úspěšně vytvořen!")
        
        # Otestuj přihlášení
        login_data = {
            'username': username,
            'password': password
        }
        
        login_response = requests.post(
            'http://127.0.0.1:5000/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Test přihlášení: {login_response.status_code}")
        print(f"Odpověď: {login_response.text}")
    else:
        print("Chyba při vytváření testovacího uživatele:", response.text)

if __name__ == '__main__':
    create_test_user() 