# database.py
import hashlib
import psycopg2
from psycopg2 import OperationalError, IntegrityError
from datetime import datetime
import time
import atexit
import os
import shutil

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host=None, database=None, user=None, password=None, port=None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._initialized = True

        self.db_params = {
            'host': host or '5.183.188.132',
            'database': database or '2025_psql_gri',
            'user': user or '2025_psql_g_usr',
            'password': password or 'aYQ2XzT2plld4zli',
            'port': port or '5432'
        }
        self.conn = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 3

        self.user_data_dir = "user_data"
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)

        atexit.register(self.cleanup)
        self.connect()
        self.create_tables()
        self.init_achievements()
        self.init_sample_data()

    def cleanup(self):
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
            except:
                pass

    def connect(self):
        for attempt in range(self._max_reconnect_attempts):
            try:
                if self.conn and not self.conn.closed:
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.conn = None

                self.conn = psycopg2.connect(**self.db_params)
                self.conn.autocommit = False
                self._reconnect_attempts = 0
                return

            except OperationalError as e:
                if attempt < self._max_reconnect_attempts - 1:
                    wait_time = min(2 ** attempt, 8)
                    time.sleep(wait_time)
                else:
                    raise e

    def ensure_connection(self):
        if self.conn is None or self.conn.closed:
            self.connect()
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (OperationalError, Exception):
            self.connect()

    def close(self):
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
            except Exception:
                pass
            finally:
                self.conn = None

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        cursor = None
        try:
            self.ensure_connection()
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())

            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()

            if commit:
                self.conn.commit()

            return result

        except Exception as e:
            if self.conn:
                try:
                    self.conn.rollback()
                except:
                    pass
            raise e
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

    def get_user_data_dir(self, user_id):
        user_dir = os.path.join(self.user_data_dir, str(user_id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

    def save_user_file(self, user_id, file_path, file_type):
        if not os.path.exists(file_path):
            return None

        user_dir = self.get_user_data_dir(user_id)

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            ext = '.png'

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_type}_{timestamp}{ext}"
        dest_path = os.path.join(user_dir, filename)

        try:
            shutil.copy2(file_path, dest_path)
            return os.path.join(str(user_id), filename)
        except Exception:
            return None

    def get_user_file_path(self, relative_path):
        if not relative_path:
            return None
        full_path = os.path.join(self.user_data_dir, relative_path)
        if os.path.exists(full_path):
            return full_path
        return None

    def create_tables(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS credentials (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        is_blocked BOOLEAN DEFAULT FALSE,
                        role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin'))
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY REFERENCES credentials(id) ON DELETE CASCADE,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        favorite_club VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        avatar_path VARCHAR(500),
                        background_path VARCHAR(500)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS leagues (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        logo_path VARCHAR(500) 
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS clubs (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        emblem_url VARCHAR(500), 
                        league_id INTEGER REFERENCES leagues(id) ON DELETE SET NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(name, league_id)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
                        team1 INTEGER NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
                        team2 INTEGER NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
                        score1 INTEGER DEFAULT 0,
                        score2 INTEGER DEFAULT 0,
                        status VARCHAR(20) DEFAULT 'Запланирован',
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        birth_date DATE NOT NULL,
                        club_id INTEGER REFERENCES clubs(id) ON DELETE SET NULL,
                        photo_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # ИСПРАВЛЕНО: image_path вместо image_url
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        image_path VARCHAR(500),
                        condition_description TEXT
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_achievements (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
                        achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
                        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, achievement_id)
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
            if self.conn:
                self.conn.rollback()
            raise e

    def drop_player_ratings_table_if_exists(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS player_ratings CASCADE")
                self.conn.commit()
                return True
        except Exception:
            return False

    def init_achievements(self):
        """Инициализация достижений в базе данных"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                # Проверяем, есть ли уже достижения
                cur.execute("SELECT COUNT(*) FROM achievements")
                count = cur.fetchone()[0]

                if count == 0:
                    # Данные о достижениях
                    achievements_data = [
                        ('Новичок', 'Эмблемы/за один добавленный.png', 'Добавлено 1 событие'),
                        ('Любитель', 'Эмблемы/за 10.png', 'Добавлено 10 событий'),
                        ('Профи', 'Эмблемы/за 50.png', 'Добавлено 50 событий'),
                        ('Легенда', 'Эмблемы/за 100.png', 'Добавлено 100 событий'),
                    ]

                    for name, image_path, description in achievements_data:
                        cur.execute("""
                            INSERT INTO achievements (name, image_path, condition_description)
                            VALUES (%s, %s, %s)
                        """, (name, image_path, description))

                    self.conn.commit()
        except Exception as e:
            print(f"❌ Ошибка при инициализации достижений: {e}")

    def init_sample_data(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM leagues")
                if cur.fetchone()[0] == 0:
                    leagues_data = [
                        ('Ла Лига', 'Эмблемы/Ла Лига/Ла лига эмблема.png'),
                        ('Английская премьер лига', 'Эмблемы/АПЛ/АПЛ Эмблема.png'),
                        ('Бундеслига', 'Эмблемы/Бундеслига/Бундеслига Эмблема.png'),
                        ('Серия A', 'Эмблемы/Сериа А/Сериа А эмблема.png'),
                        ('Лига 1', 'Эмблемы/Лига 1/Лига 1 эмблема.png'),
                        ('Российская премьер лига', 'Эмблемы/РПЛ/РПЛ Эмблема.png')
                    ]
                    for league_name, logo_path in leagues_data:
                        cur.execute(
                            "INSERT INTO leagues (name, logo_path) VALUES (%s, %s)",
                            (league_name, logo_path)
                        )
                    self.conn.commit()
        except Exception:
            pass

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_username_exists(self, username):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM credentials WHERE username = %s", (username,))
                return cur.fetchone() is not None
        except Exception:
            return False

    def register_user(self, first_name, last_name, username, password, favorite_club=''):
        try:
            if username.lower() == 'admin':
                return False, None, "Логин 'admin' зарезервирован для администратора!"

            self.ensure_connection()
            hashed_password = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO credentials (username, password, is_blocked, role)
                    VALUES (%s, %s, FALSE, 'user')
                    RETURNING id
                """, (username, hashed_password))
                user_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO user_profiles (id, first_name, last_name, favorite_club, avatar_path, background_path)
                    VALUES (%s, %s, %s, %s, NULL, NULL)
                """, (user_id, first_name, last_name, favorite_club))

                self.conn.commit()
                return True, user_id, "Регистрация успешна"
        except IntegrityError:
            if self.conn:
                self.conn.rollback()
            return False, None, "Пользователь с таким логином уже существует"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка регистрации: {e}"

    def create_admin_user(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM credentials WHERE username = 'admin'")
                if cur.fetchone():
                    return False, None, "Admin уже существует"

                empty_password = self.hash_password('')
                cur.execute("""
                    INSERT INTO credentials (username, password, is_blocked, role)
                    VALUES ('admin', %s, FALSE, 'admin')
                    RETURNING id
                """, (empty_password,))
                user_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO user_profiles (id, first_name, last_name, favorite_club, avatar_path, background_path)
                    VALUES (%s, 'Admin', 'Admin', '', NULL, NULL)
                """, (user_id,))

                self.conn.commit()

                return True, {
                    'id': user_id,
                    'first_name': 'Admin',
                    'last_name': 'Admin',
                    'favorite_club': '',
                    'username': 'admin',
                    'avatar_path': None,
                    'background_path': None
                }, "Admin создан"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка создания admin: {e}"

    def login_user(self, username, password):
        try:
            self.ensure_connection()

            if username == 'admin':
                with self.conn.cursor() as cur:
                    cur.execute("""
                        SELECT c.id, p.first_name, p.last_name, p.favorite_club, c.is_blocked,
                            p.avatar_path, p.background_path
                        FROM credentials c
                        JOIN user_profiles p ON c.id = p.id
                        WHERE c.username = 'admin'
                    """)
                    user = cur.fetchone()

                    if user:
                        user_id, first_name, last_name, favorite_club, is_blocked, avatar_path, background_path = user

                        if is_blocked:
                            return False, None, "Аккаунт администратора заблокирован!"

                        # Проверка пароля для админа (если он установлен)
                        # Для пустого пароля (старый вариант) или для хешированного
                        admin_password_hash = self.hash_password(password) if password else self.hash_password('')
                        
                        # Проверяем пароль
                        cur.execute("SELECT password FROM credentials WHERE id = %s", (user_id,))
                        stored_hash = cur.fetchone()[0]
                        
                        if stored_hash != admin_password_hash:
                            return False, None, "Неверный пароль администратора!"

                        avatar_full_path = self.get_user_file_path(avatar_path) if avatar_path else None
                        background_full_path = self.get_user_file_path(background_path) if background_path else None

                        return True, {
                            'id': user_id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'favorite_club': favorite_club,
                            'username': 'admin',
                            'avatar_path': avatar_full_path,
                            'background_path': background_full_path
                        }, "Вход выполнен успешно"
                    else:
                        return self.create_admin_user()

            # Обычный пользователь
            if not username or not password:
                return False, None, "Заполните логин и пароль"

            hashed_password = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, p.first_name, p.last_name, p.favorite_club, c.is_blocked,
                        p.avatar_path, p.background_path
                    FROM credentials c
                    JOIN user_profiles p ON c.id = p.id
                    WHERE c.username = %s AND c.password = %s
                """, (username, hashed_password))
                user = cur.fetchone()

                if user:
                    user_id, first_name, last_name, favorite_club, is_blocked, avatar_path, background_path = user

                    if is_blocked:
                        return False, None, "Ваш аккаунт заблокирован. Обратитесь к администратору."

                    avatar_full_path = self.get_user_file_path(avatar_path) if avatar_path else None
                    background_full_path = self.get_user_file_path(background_path) if background_path else None

                    return True, {
                        'id': user_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'favorite_club': favorite_club,
                        'username': username,
                        'avatar_path': avatar_full_path,
                        'background_path': background_full_path
                    }, "Вход выполнен успешно"
                else:
                    return False, None, "Неверный логин или пароль"
        except Exception as e:
            return False, None, f"Ошибка входа: {e}"

    def get_all_leagues(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name, logo_path FROM leagues ORDER BY name")
                leagues = cur.fetchall()
                return [
                    {'id': l[0], 'name': l[1], 'logo_path': l[2]}
                    for l in leagues
                ]
        except Exception:
            return []

    def get_league_by_id(self, league_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name, logo_path FROM leagues WHERE id = %s", (league_id,))
                league = cur.fetchone()
                if league:
                    return {'id': league[0], 'name': league[1], 'logo_path': league[2]}
                return None
        except Exception:
            return None

    def add_league(self, name, logo_path=None):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO leagues (name, logo_path) VALUES (%s, %s) RETURNING id",
                    (name, logo_path)
                )
                league_id = cur.fetchone()[0]
                self.conn.commit()
                return True, league_id, "Лига успешно добавлена"
        except IntegrityError:
            if self.conn:
                self.conn.rollback()
            return False, None, "Лига с таким названием уже существует"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка добавления лиги: {e}"

    def update_league(self, league_id, name=None, logo_path=None):
        try:
            self.ensure_connection()
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if logo_path is not None:
                updates.append("logo_path = %s")
                params.append(logo_path)

            if not updates:
                return False, "Нет данных для обновления"

            params.append(league_id)
            query = f"UPDATE leagues SET {', '.join(updates)} WHERE id = %s"

            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
                return True, "Лига успешно обновлена"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка обновления лиги: {e}"

    def delete_league(self, league_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("UPDATE clubs SET league_id = NULL WHERE league_id = %s", (league_id,))
                cur.execute("DELETE FROM leagues WHERE id = %s", (league_id,))
                self.conn.commit()
                return True, "Лига успешно удалена"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка удаления лиги: {e}"

    def get_all_clubs(self):
        try:
            self.ensure_connection()
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
                        'league_name': c[4] if c[4] else "Без лиги"
                    }
                    for c in clubs
                ]
        except Exception:
            return []

    def get_all_clubs_for_select(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name FROM clubs ORDER BY name")
                clubs = cur.fetchall()
                return [{'id': c[0], 'name': c[1]} for c in clubs]
        except Exception:
            return []

    def get_clubs_by_league(self, league_id):
        try:
            self.ensure_connection()
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
        except Exception:
            return []

    def get_club_by_name(self, club_name):
        try:
            result = self.execute_query(
                "SELECT id, name FROM clubs WHERE LOWER(name) = LOWER(%s)",
                (club_name,),
                fetch_one=True
            )
            if result:
                return {'id': result[0], 'name': result[1]}
            return None
        except Exception:
            return None

    def get_club_by_id(self, club_id):
        try:
            result = self.execute_query(
                "SELECT id, name, emblem_url, league_id FROM clubs WHERE id = %s",
                (club_id,),
                fetch_one=True
            )
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'emblem_url': result[2],
                    'league_id': result[3]
                }
            return None
        except Exception:
            return None

    def add_club(self, name, emblem_url, league_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO clubs (name, emblem_url, league_id) VALUES (%s, %s, %s) RETURNING id",
                    (name, emblem_url, league_id)
                )
                club_id = cur.fetchone()[0]
                self.conn.commit()
                return True, club_id, "Клуб успешно добавлен"
        except IntegrityError:
            if self.conn:
                self.conn.rollback()
            return False, None, "Клуб с таким названием уже существует в этой лиге"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка добавления клуба: {e}"

    def update_club(self, club_id, name=None, emblem_url=None, league_id=None):
        try:
            self.ensure_connection()
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
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка обновления клуба: {e}"

    def delete_club(self, club_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM clubs WHERE id = %s", (club_id,))
                self.conn.commit()
                return True, "Клуб успешно удален"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка удаления клуба: {e}"

    def get_club_emblem_by_id(self, club_id):
        try:
            result = self.execute_query(
                "SELECT emblem_url FROM clubs WHERE id = %s",
                (club_id,),
                fetch_one=True
            )
            if result:
                return result[0]
            return None
        except Exception:
            return None

    def get_club_stats(self, club_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM events WHERE team1 = %s", (club_id,))
                as_team1 = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM events WHERE team2 = %s", (club_id,))
                as_team2 = cur.fetchone()[0]
                cur.execute("""
                    SELECT COUNT(*) FROM events
                    WHERE (team1 = %s AND score1 > score2) OR (team2 = %s AND score2 > score1)
                """, (club_id, club_id))
                wins = cur.fetchone()[0]
                cur.execute("""
                    SELECT COUNT(*) FROM events
                    WHERE (team1 = %s OR team2 = %s) AND score1 = score2
                """, (club_id, club_id))
                draws = cur.fetchone()[0]
                cur.execute("""
                    SELECT COUNT(*) FROM events
                    WHERE (team1 = %s AND score1 < score2) OR (team2 = %s AND score2 < score1)
                """, (club_id, club_id))
                losses = cur.fetchone()[0]
                total_matches = as_team1 + as_team2
                return {
                    'total_matches': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses
                }
        except Exception:
            return None

    def get_all_players(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.first_name, p.last_name, p.birth_date,
                           p.photo_url, c.id as club_id, c.name as club_name
                    FROM players p
                    LEFT JOIN clubs c ON p.club_id = c.id
                    ORDER BY p.last_name, p.first_name
                """)
                players = cur.fetchall()
                return [
                    {
                        'id': p[0],
                        'first_name': p[1],
                        'last_name': p[2],
                        'birth_date': p[3].strftime("%d.%m.%Y") if p[3] else "",
                        'photo_url': p[4],
                        'club_id': p[5],
                        'club_name': p[6] if p[6] else "Не указан"
                    }
                    for p in players
                ]
        except Exception:
            return []

    def get_players_by_club(self, club_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, first_name, last_name, birth_date, photo_url
                    FROM players
                    WHERE club_id = %s
                    ORDER BY last_name, first_name
                """, (club_id,))
                players = cur.fetchall()
                return [
                    {
                        'id': p[0],
                        'first_name': p[1],
                        'last_name': p[2],
                        'birth_date': p[3],
                        'photo_url': p[4]
                    }
                    for p in players
                ]
        except Exception:
            return []

    def add_player(self, first_name, last_name, birth_date, club_id, photo_url):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO players (first_name, last_name, birth_date, club_id, photo_url)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (first_name, last_name, birth_date, club_id, photo_url))
                player_id = cur.fetchone()[0]
                self.conn.commit()
                return True, player_id, "Игрок успешно добавлен"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка добавления игрока: {e}"

    def delete_player(self, player_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM players WHERE id = %s", (player_id,))
                self.conn.commit()
                return True, "Игрок успешно удален"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка удаления игрока: {e}"

    def add_event(self, user_id, team1_name, team2_name, score1, score2, status, comment):
        try:
            team1 = self.get_club_by_name(team1_name)
            team2 = self.get_club_by_name(team2_name)

            if team1 is None:
                return False, None, f"Команда '{team1_name}' не найдена в базе данных"

            if team2 is None:
                return False, None, f"Команда '{team2_name}' не найдена в базе данных"

            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (user_id, team1, team2, score1, score2, status, comment, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """, (user_id, team1['id'], team2['id'], score1, score2, status, comment))
                event_id = cur.fetchone()[0]
                self.conn.commit()
                return True, event_id, "Событие успешно добавлено"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка добавления события: {e}"

    def get_user_events(self, user_id, limit=50):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id,
                           c1.name as team1, c1.emblem_url as team1_emblem,
                           c2.name as team2, c2.emblem_url as team2_emblem,
                           e.score1, e.score2, e.status, e.comment, e.created_at
                    FROM events e
                    JOIN clubs c1 ON e.team1 = c1.id
                    JOIN clubs c2 ON e.team2 = c2.id
                    WHERE e.user_id = %s
                    ORDER BY e.created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                events = cur.fetchall()

                result = []
                for ev in events:
                    result.append({
                        'id': ev[0],
                        'team1': ev[1],
                        'team1_emblem': ev[2],
                        'team2': ev[3],
                        'team2_emblem': ev[4],
                        'score1': ev[5],
                        'score2': ev[6],
                        'status': ev[7],
                        'comment': ev[8],
                        'created_at': ev[9]
                    })
                return result
        except Exception:
            return []

    def get_all_events_for_admin(self, limit=200):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.user_id,
                           c1.name as team1, c1.emblem_url as team1_emblem,
                           c2.name as team2, c2.emblem_url as team2_emblem,
                           e.score1, e.score2, e.status, e.comment, e.created_at,
                           cred.username, up.first_name, up.last_name
                    FROM events e
                    JOIN clubs c1 ON e.team1 = c1.id
                    JOIN clubs c2 ON e.team2 = c2.id
                    JOIN credentials cred ON e.user_id = cred.id
                    JOIN user_profiles up ON e.user_id = up.id
                    ORDER BY e.created_at DESC
                    LIMIT %s
                """, (limit,))
                events = cur.fetchall()

                result = []
                for ev in events:
                    result.append({
                        'id': ev[0],
                        'user_id': ev[1],
                        'team1': ev[2],
                        'team1_emblem': ev[3],
                        'team2': ev[4],
                        'team2_emblem': ev[5],
                        'score1': ev[6],
                        'score2': ev[7],
                        'status': ev[8],
                        'comment': ev[9],
                        'created_at': ev[10],
                        'username': ev[11],
                        'first_name': ev[12],
                        'last_name': ev[13]
                    })
                return result
        except Exception:
            return []

    def get_all_events_count_for_admin(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM events")
                result = cur.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def get_user_events_count(self, user_id):
        try:
            result = self.execute_query(
                "SELECT COUNT(*) FROM events WHERE user_id = %s",
                (user_id,),
                fetch_one=True
            )
            return result[0] if result else 0
        except Exception:
            return 0

    def update_event(self, event_id, team1_name, team2_name, score1, score2, status, comment):
        try:
            team1 = self.get_club_by_name(team1_name)
            team2 = self.get_club_by_name(team2_name)

            if team1 is None:
                return False, f"Команда '{team1_name}' не найдена в базе данных"

            if team2 is None:
                return False, f"Команда '{team2_name}' не найдена в базе данных"

            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE events
                    SET team1 = %s, team2 = %s, score1 = %s, score2 = %s,
                        status = %s, comment = %s
                    WHERE id = %s
                """, (team1['id'], team2['id'], score1, score2, status, comment, event_id))
                self.conn.commit()
                return True, "Событие успешно обновлено"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка обновления события: {e}"

    def get_event_by_id(self, event_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.user_id,
                        c1.name as team1, c1.emblem_url as team1_emblem,
                        c2.name as team2, c2.emblem_url as team2_emblem,
                        e.score1, e.score2, e.status, e.comment, e.created_at
                    FROM events e
                    JOIN clubs c1 ON e.team1 = c1.id
                    JOIN clubs c2 ON e.team2 = c2.id
                    WHERE e.id = %s
                """, (event_id,))
                event = cur.fetchone()

                if event:
                    return {
                        'id': event[0],
                        'user_id': event[1],
                        'team1': event[2],
                        'team1_emblem': event[3],
                        'team2': event[4],
                        'team2_emblem': event[5],
                        'score1': event[6],
                        'score2': event[7],
                        'status': event[8],
                        'comment': event[9],
                        'created_at': event[10]
                    }
                return None
        except Exception:
            return None

    def get_all_achievements(self):
        """Получение всех достижений из базы данных"""
        try:
            result = self.execute_query(
                "SELECT id, name, image_path, condition_description FROM achievements ORDER BY id",
                fetch_all=True
            )
            if result:
                return [
                    {'id': r[0], 'name': r[1], 'image_path': r[2], 'description': r[3]}
                    for r in result
                ]
            return []
        except Exception as e:
            print(f"Ошибка получения достижений: {e}")
            return []

    def get_user_achievements(self, user_id):
        """Получение достижений пользователя"""
        try:
            result = self.execute_query("""
                SELECT a.id, a.name, a.image_path, a.condition_description, ua.earned_at
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = %s
                ORDER BY ua.earned_at
            """, (user_id,), fetch_all=True)

            if result:
                return [
                    {
                        'id': r[0],
                        'name': r[1],
                        'image_path': r[2],
                        'description': r[3],
                        'earned_at': r[4]
                    }
                    for r in result
                ]
            return []
        except Exception as e:
            print(f"Ошибка получения достижений пользователя: {e}")
            return []

    def check_and_award_achievements(self, user_id):
        """Проверка и выдача достижений пользователю"""
        try:
            events_count = self.get_user_events_count(user_id)
            print(f"📊 Пользователь {user_id}: количество событий = {events_count}")
            
            all_achievements = self.get_all_achievements()
            user_achievements = self.get_user_achievements(user_id)
            user_achievement_ids = [a['id'] for a in user_achievements]

            # Соответствие ID достижений пороговым значениям
            # (предполагаем, что ID идут по порядку: 1-Новичок, 2-Любитель, 3-Профи, 4-Легенда)
            thresholds = {1: 1, 2: 10, 3: 50, 4: 100}

            awarded = []

            for achievement in all_achievements:
                ach_id = achievement['id']
                if ach_id in thresholds and ach_id not in user_achievement_ids:
                    if events_count >= thresholds[ach_id]:
                        print(f"🏆 Выдаём достижение {achievement['name']} (id={ach_id})")
                        if self.award_achievement(user_id, ach_id):
                            awarded.append(achievement)

            if awarded:
                print(f"✅ Выдано достижений: {[a['name'] for a in awarded]}")
            return awarded
        except Exception as e:
            print(f"❌ Ошибка проверки достижений: {e}")
            return []

    def award_achievement(self, user_id, achievement_id):
        """Выдача достижения пользователю"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO user_achievements (user_id, achievement_id, earned_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, achievement_id) DO NOTHING
                    RETURNING id
                """, (user_id, achievement_id))
                result = cur.fetchone()
                self.conn.commit()
                return result is not None
        except Exception as e:
            print(f"Ошибка выдачи достижения: {e}")
            return False

    def get_all_users(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, c.username, c.is_blocked, p.first_name, p.last_name
                    FROM credentials c
                    JOIN user_profiles p ON c.id = p.id
                    ORDER BY p.last_name, p.first_name
                """)
                users = cur.fetchall()
                return [
                    {
                        'id': u[0],
                        'username': u[1],
                        'is_blocked': u[2],
                        'first_name': u[3],
                        'last_name': u[4]
                    }
                    for u in users
                ]
        except Exception:
            return []

    def get_user_by_id(self, user_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, first_name, last_name, favorite_club, avatar_path, background_path
                    FROM user_profiles WHERE id = %s
                """, (user_id,))
                user = cur.fetchone()
                if user:
                    return {
                        'id': user[0],
                        'first_name': user[1],
                        'last_name': user[2],
                        'favorite_club': user[3],
                        'avatar_path': self.get_user_file_path(user[4]) if user[4] else None,
                        'background_path': self.get_user_file_path(user[5]) if user[5] else None
                    }
                return None
        except Exception:
            return None

    def block_user(self, user_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT username FROM credentials WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result and result[0] == 'admin':
                    return False, "Нельзя заблокировать администратора"
                
                cur.execute("""
                    UPDATE credentials SET is_blocked = TRUE WHERE id = %s RETURNING id
                """, (user_id,))
                result = cur.fetchone()
                self.conn.commit()
                return (True, "Пользователь успешно заблокирован") if result else (False, "Пользователь не найден")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка блокировки: {e}"

    def unblock_user(self, user_id):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT username FROM credentials WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result and result[0] == 'admin':
                    return False, "Нельзя разблокировать администратора (он и так не заблокирован)"
                
                cur.execute("""
                    UPDATE credentials SET is_blocked = FALSE WHERE id = %s RETURNING id
                """, (user_id,))
                result = cur.fetchone()
                self.conn.commit()
                return (True, "Пользователь успешно разблокирован") if result else (False, "Пользователь не найден")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка разблокировки: {e}"

    def update_user_avatar(self, user_id, avatar_file_path):
        try:
            relative_path = self.save_user_file(user_id, avatar_file_path, 'avatar')
            if relative_path:
                self.execute_query(
                    "UPDATE user_profiles SET avatar_path = %s WHERE id = %s",
                    (relative_path, user_id),
                    commit=True
                )
                return True, relative_path
            return False, None
        except Exception:
            return False, None

    def update_user_background(self, user_id, background_file_path):
        try:
            relative_path = self.save_user_file(user_id, background_file_path, 'background')
            if relative_path:
                self.execute_query(
                    "UPDATE user_profiles SET background_path = %s WHERE id = %s",
                    (relative_path, user_id),
                    commit=True
                )
                return True, relative_path
            return False, None
        except Exception:
            return False, None

    def get_user_avatar_path(self, user_id):
        result = self.execute_query(
            "SELECT avatar_path FROM user_profiles WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        if result and result[0]:
            return self.get_user_file_path(result[0])
        return None

    def get_user_background_path(self, user_id):
        result = self.execute_query(
            "SELECT background_path FROM user_profiles WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        if result and result[0]:
            return self.get_user_file_path(result[0])
        return None

    def save_message(self, user_id, message):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_messages (user_id, message, sent_at)
                    VALUES (%s, %s, %s)
                    RETURNING id, sent_at
                """, (user_id, message, datetime.now()))
                result = cur.fetchone()
                self.conn.commit()
                return True, {'id': result[0], 'sent_at': result[1]}
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка сохранения сообщения: {e}"

    def get_chat_messages(self, limit=50):
        try:
            self.ensure_connection()
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
        except Exception:
            return []

    def __del__(self):
        self.cleanup()