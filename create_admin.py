import hashlib
from database import Database

def create_admin():
    db = Database()
    
    if db.check_username_exists('admin'):
        print("Администратор уже существует!")
        return

    import getpass
    password = getpass.getpass("Введите пароль администратора: ")
    confirm = getpass.getpass("Подтвердите пароль: ")
    
    if password != confirm:
        print("Пароли не совпадают!")
        return
    
    if len(password) < 6:
        print("Пароль должен быть не менее 6 символов!")
        return
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        db.ensure_connection()
        with db.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO credentials (username, password, is_blocked, role)
                VALUES ('admin', %s, FALSE, 'admin')
                RETURNING id
            """, (hashed,))
            user_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO user_profiles (id, first_name, last_name, favorite_club)
                VALUES (%s, 'Administrator', 'System', '')
            """, (user_id,))
            
            db.conn.commit()
            print("Администратор успешно создан!")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    create_admin()