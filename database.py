import hashlib
import psycopg2
from psycopg2 import OperationalError, IntegrityError

class Database:
    def __init__(self, host='localhost', port='5432', database='bbc_db', 
                 user='postgres', password='12345'):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.connection_params)
        except OperationalError as e:
            raise e
    
    def create_tables(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS credentials (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL
                    );
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY REFERENCES credentials(id) ON DELETE CASCADE,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        favorite_club VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
        except Exception as e:
            raise e
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_username_exists(self, username):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM credentials WHERE username = %s", (username,))
                return cur.fetchone() is not None
        except Exception:
            return False
    
    def register_user(self, first_name, last_name, username, password, favorite_club=''):
        try:
            hashed_password = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO credentials (username, password)
                    VALUES (%s, %s)
                    RETURNING id
                """, (username, hashed_password))
                user_id = cur.fetchone()[0]
                
                cur.execute("""
                    INSERT INTO user_profiles (id, first_name, last_name, favorite_club)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, first_name, last_name, favorite_club))
                
                self.conn.commit()
                return True, user_id, "Регистрация успешна"
        except IntegrityError:
            self.conn.rollback()
            return False, None, "Пользователь с таким логином уже существует"
        except Exception as e:
            self.conn.rollback()
            return False, None, f"Ошибка регистрации: {e}"
    
    def login_user(self, username, password):
        try:
            hashed_password = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, p.first_name, p.last_name, p.favorite_club 
                    FROM credentials c
                    JOIN user_profiles p ON c.id = p.id
                    WHERE c.username = %s AND c.password = %s
                """, (username, hashed_password))
                user = cur.fetchone()
                
                if user:
                    return True, {
                        'id': user[0],
                        'first_name': user[1],
                        'last_name': user[2],
                        'favorite_club': user[3]
                    }, "Вход выполнен успешно"
                else:
                    return False, None, "Неверный логин или пароль"
        except Exception as e:
            return False, None, f"Ошибка входа: {e}"
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()