import bcrypt
import requests
import json

def create_admin_user():
    username = "samekt"
    password = "shaman"
    
    # Vygeneruj salt a hash hesla
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    salt_str = salt.decode('utf-8')
    hashed_str = hashed.decode('utf-8')
    
    print(f"Vytvářím administrátorský účet:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Salt: {salt_str}")
    print(f"Hash: {hashed_str}")
    
    # Přidej uživatele do Google Sheetu
    data = {
        'username': username,
        'password': password
    }
    
    response = requests.post(
        'http://127.0.0.1:5000/add_user',
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print("\nAdministrátorský účet byl úspěšně vytvořen!")
        print("Můžete se nyní přihlásit s těmito údaji:")
        print(f"Uživatelské jméno: {username}")
        print(f"Heslo: {password}")
    else:
        print("Chyba při vytváření administrátorského účtu:", response.text)

if __name__ == '__main__':
    create_admin_user() 