# database.pу (дополненная версия с таблицей событий)
import hashlib
import psycopg2
from psycopg2 import OperationalError, IntegrityError
from datetime import datetime

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
                # Существующие таблицы
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
                
                # НОВЫЕ ТАБЛИЦЫ ДЛЯ ЛИГ И КЛУБОВ
                
                # Таблица Лиг
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS leagues (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        logo_path TEXT
                    );
                """)
                
                # Таблица Команд (Клубов)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS clubs (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        emblem_url TEXT,
                        league_id INTEGER REFERENCES leagues(id) ON DELETE SET NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(name, league_id)
                    );
                """)
                
                # Добавляем таблицу для достижений, если её нет
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        image_path TEXT,
                        condition_description TEXT
                    );
                """)
                
                # Таблица пользовательских достижений
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_achievements (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
                        achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
                        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, achievement_id)
                    );
                """)
                
                # НОВАЯ ТАБЛИЦА ДЛЯ СОБЫТИЙ (МАТЧЕЙ)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
                        team1 VARCHAR(100) NOT NULL,
                        team2 VARCHAR(100) NOT NULL,
                        score1 INTEGER DEFAULT 0,
                        score2 INTEGER DEFAULT 0,
                        status VARCHAR(20) DEFAULT 'Запланирован',
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Заполняем лиги начальными данными, если таблица пуста
                cur.execute("SELECT COUNT(*) FROM leagues")
                count = cur.fetchone()[0]
                if count == 0:
                    leagues_data = [
                        ('Ла Лига', r'Эмблемы\Ла Лига\Ла лига эмблема.png'),
                        ('Английская премьер лига', r'Эмблемы\АПЛ\АПЛ Эмблема.png'),
                        ('Бундеслига', r'Эмблемы\Бундеслига\Бундеслига Эмблема.png'),
                        ('Серия A', r'Эмблемы\Сериа А\Сериа А эмблема.png'),
                        ('Лига 1', r'Эмблемы\Лига 1\Лига 1 эмблема.png'),
                        ('Российская премьер лига', r'Эмблемы\РПЛ\РПЛ Эмблема.png')
                    ]
                    for league_name, logo_path in leagues_data:
                        cur.execute(
                            "INSERT INTO leagues (name, logo_path) VALUES (%s, %s)",
                            (league_name, logo_path)
                        )
                
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
    
    # Методы для работы с событиями (матчами)
    
    def add_event(self, user_id, team1, team2, score1, score2, status, comment):
        """Добавляет новое событие (матч) для пользователя"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (user_id, team1, team2, score1, score2, status, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, team1, team2, score1, score2, status, comment))
                event_id = cur.fetchone()[0]
                self.conn.commit()
                return True, event_id, "Событие успешно добавлено"
        except Exception as e:
            self.conn.rollback()
            return False, None, f"Ошибка добавления события: {e}"
    
    def get_user_events(self, user_id, limit=50):
        """Получает все события пользователя"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, team1, team2, score1, score2, status, comment, created_at
                    FROM events
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                events = cur.fetchall()
                
                result = []
                for ev in events:
                    result.append({
                        'id': ev[0],
                        'team1': ev[1],
                        'team2': ev[2],
                        'score1': ev[3],
                        'score2': ev[4],
                        'status': ev[5],
                        'comment': ev[6],
                        'created_at': ev[7]
                    })
                
                return result
        except Exception as e:
            print(f"Ошибка получения событий: {e}")
            return []
    
    # Методы для работы с лигами
    
    def get_all_leagues(self):
        """Получает список всех лиг"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name, logo_path FROM leagues ORDER BY name")
                leagues = cur.fetchall()
                return [
                    {'id': l[0], 'name': l[1], 'logo_path': l[2]}
                    for l in leagues
                ]
        except Exception as e:
            print(f"Ошибка получения лиг: {e}")
            return []
    
    def get_league_by_id(self, league_id):
        """Получает лигу по ID"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name, logo_path FROM leagues WHERE id = %s", (league_id,))
                league = cur.fetchone()
                if league:
                    return {'id': league[0], 'name': league[1], 'logo_path': league[2]}
                return None
        except Exception as e:
            print(f"Ошибка получения лиги: {e}")
            return None
    
    def add_league(self, name, logo_path=None):
        """Добавляет новую лигу"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO leagues (name, logo_path) VALUES (%s, %s) RETURNING id",
                    (name, logo_path)
                )
                league_id = cur.fetchone()[0]
                self.conn.commit()
                return True, league_id, "Лига успешно добавлена"
        except IntegrityError:
            self.conn.rollback()
            return False, None, "Лига с таким названием уже существует"
        except Exception as e:
            self.conn.rollback()
            return False, None, f"Ошибка добавления лиги: {e}"
    
    # Методы для работы с клубами
    
    def get_clubs_by_league(self, league_id):
        """Получает все клубы определенной лиги"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, emblem_url, league_id 
                    FROM clubs 
                    WHERE league_id = %s 
                    ORDER BY name
                """, (league_id,))
                clubs = cur.fetchall()
                return [
                    {'id': c[0], 'name': c[1], 'emblem_url': c[2], 'league_id': c[3]}
                    for c in clubs
                ]
        except Exception as e:
            print(f"Ошибка получения клубов: {e}")
            return []
    
    def get_all_clubs(self):
        """Получает все клубы"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, c.name, c.emblem_url, c.league_id, l.name as league_name
                    FROM clubs c
                    LEFT JOIN leagues l ON c.league_id = l.id
                    ORDER BY l.name, c.name
                """)
                clubs = cur.fetchall()
                return [
                    {
                        'id': c[0], 
                        'name': c[1], 
                        'emblem_url': c[2], 
                        'league_id': c[3],
                        'league_name': c[4]
                    }
                    for c in clubs
                ]
        except Exception as e:
            print(f"Ошибка получения клубов: {e}")
            return []
    
    def add_club(self, name, emblem_url, league_id):
        """Добавляет новый клуб"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO clubs (name, emblem_url, league_id) VALUES (%s, %s, %s) RETURNING id",
                    (name, emblem_url, league_id)
                )
                club_id = cur.fetchone()[0]
                self.conn.commit()
                return True, club_id, "Клуб успешно добавлен"
        except IntegrityError:
            self.conn.rollback()
            return False, None, "Клуб с таким названием уже существует в этой лиге"
        except Exception as e:
            self.conn.rollback()
            return False, None, f"Ошибка добавления клуба: {e}"
    
    def delete_club(self, club_id):
        """Удаляет клуб по ID"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM clubs WHERE id = %s", (club_id,))
                self.conn.commit()
                return True, "Клуб успешно удален"
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка удаления клуба: {e}"
    
    def update_club(self, club_id, name=None, emblem_url=None, league_id=None):
        """Обновляет данные клуба"""
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if emblem_url is not None:
                updates.append("emblem_url = %s")
                params.append(emblem_url)
            if league_id is not None:
                updates.append("league_id = %s")
                params.append(league_id)
            
            if not updates:
                return False, "Нет данных для обновления"
            
            params.append(club_id)
            query = f"UPDATE clubs SET {', '.join(updates)} WHERE id = %s"
            
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
                return True, "Клуб успешно обновлен"
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка обновления клуба: {e}"
    
    # Остальные существующие методы...
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
            print(f"Ошибка получения сообщений: {e}")
            return []
    
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
            print(f"Ошибка получения пользователя: {e}")
            return None

def get_user_events(self, user_id, limit=50):
    """Получает все события пользователя"""
    try:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, team1, team2, score1, score2, status, comment, created_at
                FROM events
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            events = cur.fetchall()
            
            result = []
            for ev in events:
                result.append({
                    'id': ev[0],
                    'team1': ev[1],
                    'team2': ev[2],
                    'score1': ev[3],
                    'score2': ev[4],
                    'status': ev[5],
                    'comment': ev[6],
                    'created_at': ev[7]
                })
            
            return result
    except Exception as e:
        print(f"Ошибка получения событий: {e}")
        return []
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()