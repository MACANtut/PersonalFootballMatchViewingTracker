# database.py - исправленная версия с правильным управлением соединениями
import hashlib
import psycopg2
from psycopg2 import OperationalError, IntegrityError
from datetime import datetime
import time
import atexit


class Database:
    _instance = None  # Singleton pattern для одного соединения
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, host=None, database=None, user=None, password=None, port=None):
        # Проверяем, инициализирован ли уже экземпляр
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        
        # Use provided parameters or defaults
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
        
        # Регистрируем закрытие соединения при завершении
        atexit.register(self.cleanup)
        
        self.connect()
        self.create_tables()
    
    def cleanup(self):
        """Принудительное закрытие соединения при завершении"""
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
                print("Соединение с БД закрыто при завершении программы")
            except:
                pass
    
    def connect(self):
        """Подключение к базе данных с повторными попытками"""
        for attempt in range(self._max_reconnect_attempts):
            try:
                # Закрываем существующее соединение, если оно есть
                if self.conn and not self.conn.closed:
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.conn = None
                
                self.conn = psycopg2.connect(**self.db_params)
                self.conn.autocommit = False
                self._reconnect_attempts = 0
                print("Соединение с БД установлено")
                return
                
            except OperationalError as e:
                print(f"Ошибка подключения (попытка {attempt + 1}): {e}")
                if attempt < self._max_reconnect_attempts - 1:
                    wait_time = min(2 ** attempt, 8)  # 1, 2, 4 секунды
                    time.sleep(wait_time)
                else:
                    print(f"Не удалось подключиться после {self._max_reconnect_attempts} попыток")
                    raise e
    
    def ensure_connection(self):
        """Проверяет и восстанавливает соединение при необходимости"""
        if self.conn is None or self.conn.closed:
            self.connect()
            return
        
        try:
            # Проверяем соединение, выполняя простой запрос
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (OperationalError, Exception) as e:
            print(f"Соединение потеряно, переподключаюсь...")
            self.connect()
    
    def close(self):
        """Закрывает соединение с БД"""
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
                print("Соединение с БД закрыто")
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")
            finally:
                self.conn = None
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Универсальный метод для выполнения запросов с автоматическим управлением курсором"""
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
            print(f"Ошибка выполнения запроса: {e}")
            raise e
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def create_tables(self):
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                # Существующие таблицы с добавлением поля is_blocked
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS credentials (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        is_blocked BOOLEAN DEFAULT FALSE
                    );
                """)
                
                # Добавляем колонку is_blocked если её нет (для существующих таблиц)
                cur.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name='credentials' AND column_name='is_blocked') 
                        THEN
                            ALTER TABLE credentials ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE;
                        END IF;
                    END $$;
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
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS leagues (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        logo_path TEXT
                    );
                """)
                
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
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        image_path TEXT,
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
                
                # Проверяем существование таблицы events
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'events'
                    );
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    # Создаем таблицу events
                    cur.execute("""
                        CREATE TABLE events (
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
                
                # НОВАЯ ТАБЛИЦА ДЛЯ ИГРОКОВ
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
            if self.conn:
                self.conn.rollback()
            print(f"Ошибка создания таблиц: {e}")
            raise e
    
    def get_club_by_name(self, club_name):
        """Получает ID и правильное название клуба по введенному названию (без учета регистра)"""
        try:
            result = self.execute_query(
                "SELECT id, name FROM clubs WHERE LOWER(name) = LOWER(%s)",
                (club_name,),
                fetch_one=True
            )
            if result:
                return {'id': result[0], 'name': result[1]}
            return None
        except Exception as e:
            print(f"Ошибка получения клуба: {e}")
            return None
    
    def get_club_id_by_name(self, club_name):
        """Получает ID клуба по названию (без учета регистра)"""
        try:
            result = self.execute_query(
                "SELECT id FROM clubs WHERE LOWER(name) = LOWER(%s)",
                (club_name,),
                fetch_one=True
            )
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Ошибка получения ID клуба: {e}")
            return None
    
    def add_event(self, user_id, team1, team2, score1, score2, status, comment):
        """Добавляет новое событие (матч) для пользователя"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (user_id, team1, team2, score1, score2, status, comment, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """, (user_id, team1, team2, score1, score2, status, comment))
                event_id = cur.fetchone()[0]
                self.conn.commit()
                return True, event_id, "Событие успешно добавлено"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Ошибка добавления события: {e}")
            return False, None, f"Ошибка добавления события: {e}"
    
    def get_user_events(self, user_id, limit=50):
        """Получает все события пользователя"""
        try:
            self.ensure_connection()
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
            if self.conn:
                self.conn.rollback()
            return []
    
    def get_all_leagues(self):
        """Получает список всех лиг"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name, logo_path FROM leagues ORDER BY name")
                leagues = cur.fetchall()
                return [
                    {'id': l[0], 'name': l[1], 'logo_path': l[2]}
                    for l in leagues
                ]
        except Exception as e:
            print(f"Ошибка получения лиг: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def get_league_by_id(self, league_id):
        """Получает лигу по ID"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, name, logo_path FROM leagues WHERE id = %s", (league_id,))
                league = cur.fetchone()
                if league:
                    return {'id': league[0], 'name': league[1], 'logo_path': league[2]}
                return None
        except Exception as e:
            print(f"Ошибка получения лиги: {e}")
            if self.conn:
                self.conn.rollback()
            return None
    
    def add_league(self, name, logo_path=None):
        """Добавляет новую лигу"""
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
    
    def get_clubs_by_league(self, league_id):
        """Получает все клубы определенной лиги"""
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
        except Exception as e:
            print(f"Ошибка получения клубов: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def get_all_clubs(self):
        """Получает все клубы"""
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
                        'league_name': c[4]
                    }
                    for c in clubs
                ]
        except Exception as e:
            print(f"Ошибка получения клубов: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def get_all_clubs_for_select(self):
        """Получает список клубов для выпадающего списка"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name FROM clubs ORDER BY name
                """)
                clubs = cur.fetchall()
                return [
                    {'id': c[0], 'name': c[1]}
                    for c in clubs
                ]
        except Exception as e:
            print(f"Ошибка получения клубов: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def add_club(self, name, emblem_url, league_id):
        """Добавляет новый клуб"""
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
    
    def delete_club(self, club_id):
        """Удаляет клуб по ID"""
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
    
    def update_club(self, club_id, name=None, emblem_url=None, league_id=None):
        """Обновляет данные клуба"""
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
    
    def add_player(self, first_name, last_name, birth_date, club_id, photo_url):
        """Добавляет нового игрока в базу данных"""
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
    
    def get_all_players(self):
        """Получает всех игроков из базы данных"""
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
        except Exception as e:
            print(f"Ошибка получения игроков: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def delete_player(self, player_id):
        """Удаляет игрока по ID"""
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
    
    def block_user(self, user_id):
        """Блокирует пользователя по ID"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE credentials 
                    SET is_blocked = TRUE 
                    WHERE id = %s
                    RETURNING id
                """, (user_id,))
                result = cur.fetchone()
                self.conn.commit()
                if result:
                    return True, "Пользователь успешно заблокирован"
                return False, "Пользователь не найден"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка блокировки пользователя: {e}"
    
    def unblock_user(self, user_id):
        """Разблокирует пользователя по ID"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE credentials 
                    SET is_blocked = FALSE 
                    WHERE id = %s
                    RETURNING id
                """, (user_id,))
                result = cur.fetchone()
                self.conn.commit()
                if result:
                    return True, "Пользователь успешно разблокирован"
                return False, "Пользователь не найден"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, f"Ошибка разблокировки пользователя: {e}"
    
    def is_user_blocked(self, user_id):
        """Проверяет, заблокирован ли пользователь"""
        try:
            self.ensure_connection()
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT is_blocked FROM credentials WHERE id = %s
                """, (user_id,))
                result = cur.fetchone()
                if result:
                    return result[0]
                return False
        except Exception as e:
            print(f"Ошибка проверки блокировки: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_all_users(self):
        """Получает всех пользователей с информацией о блокировке"""
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
        except Exception as e:
            print(f"Ошибка получения пользователей: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
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
            self.ensure_connection()
            hashed_password = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO credentials (username, password, is_blocked)
                    VALUES (%s, %s, FALSE)
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
            if self.conn:
                self.conn.rollback()
            return False, None, "Пользователь с таким логином уже существует"
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, None, f"Ошибка регистрации: {e}"
    
    def login_user(self, username, password):
        try:
            self.ensure_connection()
            hashed_password = self.hash_password(password)
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id, p.first_name, p.last_name, p.favorite_club, c.is_blocked
                    FROM credentials c
                    JOIN user_profiles p ON c.id = p.id
                    WHERE c.username = %s AND c.password = %s
                """, (username, hashed_password))
                user = cur.fetchone()
                
                if user:
                    user_id, first_name, last_name, favorite_club, is_blocked = user
                    
                    if is_blocked:
                        return False, None, "Ваш аккаунт заблокирован. Обратитесь к администратору."
                    
                    return True, {
                        'id': user_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'favorite_club': favorite_club
                    }, "Вход выполнен успешно"
                else:
                    return False, None, "Неверный логин или пароль"
        except Exception as e:
            return False, None, f"Ошибка входа: {e}"
    
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
                return True, {
                    'id': result[0],
                    'sent_at': result[1]
                }
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
        except Exception as e:
            print(f"Ошибка получения сообщений: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def get_user_by_id(self, user_id):
        try:
            self.ensure_connection()
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
    
    def __del__(self):
        self.cleanup()