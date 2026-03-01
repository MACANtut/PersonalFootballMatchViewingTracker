import hashlib
import psycopg2
from psycopg2 import OperationalError, IntegrityError
from datetime import datetime

class Database:
    def __init__(self, host='localhost', port='5432', database='bbc_db', 
                 user='postgres', password='89635441904GRgr'):
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
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
                        message TEXT NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def save_message(self, user_id, message):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_messages (user_id, message, sent_at)
                    VALUES (%s, %s, %s)
                    RETURNING id, sent_at
                """, (user_id, message, datetime.now()))
                result = cur.fetchone()
                self.conn.commit()
                return True, {
                    'id': result[0],
                    'sent_at': result[1]
                }
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка сохранения сообщения: {e}"
    
    def get_chat_messages(self, limit=50):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT cm.id, cm.user_id, cm.message, cm.sent_at,
                           p.first_name, p.last_name
                    FROM chat_messages cm
                    JOIN user_profiles p ON cm.user_id = p.id
                    ORDER BY cm.sent_at DESC
                    LIMIT %s
                """, (limit,))
                messages = cur.fetchall()
                
                result = []
                for msg in messages:
                    result.append({
                        'id': msg[0],
                        'user_id': msg[1],
                        'message': msg[2],
                        'sent_at': msg[3],
                        'first_name': msg[4],
                        'last_name': msg[5]
                    })
                
                return list(reversed(result))
        except Exception as e:
            return f"Ошибка получения сообщений: {e}"
    
    def get_user_by_id(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, first_name, last_name, favorite_club
                    FROM user_profiles
                    WHERE id = %s
                """, (user_id,))
                user = cur.fetchone()
                if user:
                    return {
                        'id': user[0],
                        'first_name': user[1],
                        'last_name': user[2],
                        'favorite_club': user[3]
                    }
                return None
        except Exception as e:
            return None
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()