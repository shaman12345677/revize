import bcrypt

def generate_password_hash():
    password = input("Zadejte heslo pro nového uživatele: ")
    
    # Vygeneruj salt a hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    salt_str = salt.decode('utf-8')
    hashed_str = hashed.decode('utf-8')
    
    print("\nZkopírujte tyto hodnoty do Google Sheetu:")
    print(f"Salt (sloupec B): {salt_str}")
    print(f"Hash (sloupec C): {hashed_str}")
    
    # Ověření
    print("\nOvěření hashe:")
    if bcrypt.checkpw(password.encode('utf-8'), hashed):
        print("✓ Hash je správný")
    else:
        print("✗ Hash není správný")

if __name__ == '__main__':
    generate_password_hash() 