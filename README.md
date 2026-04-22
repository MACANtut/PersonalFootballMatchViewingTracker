# Personal Football Match Tracker

**_Приложение для отслеживания футбольных матчей с системой достижений, чатом и админ-панелью._**

![Demo](https://otkritkis.com/wp-content/uploads/2022/06/njbjj.gif)

## 📦 **Установка**

```bash
pip install PySide6 psycopg2-binary matplotlib requests numpy
```

## 🚀 **Запуск**

```bash
python program.py
```

## 🔑 **Логин**

```bash
| Пользователь | Логин | Пароль |
|------------- |-------|--------|
| Админ        | admin| (пусто)|
| Обычный      | любой | любой  |
```

## 🗄️ **Структура БД**

```bash
credentials(id, username, password, is_blocked)
user_profiles(id, first_name, last_name, favorite_club, avatar_path, background_path)
leagues(id, name, logo_path)
clubs(id, name, emblem_url, league_id)
players(id, first_name, last_name, birth_date, club_id, photo_url)
events(id, user_id, team1, team2, score1, score2, status, comment)
achievements(id, name, image_path, condition_description)
user_achievements(user_id, achievement_id, earned_at)
chat_messages(id, user_id, message, sent_at)
```

## 🔌 **Подключение к БД**

```bash
# database.py
self.db_params = {
    'host': 'ваш хост',
    'database': 'ваша БД',
    'user': 'ваше имя пользователя',
    'password': 'ваш пароль',
    'port': '5432'
}
```

## 📁 **Папки проекта**

```bash
| Папка           | Назначение                  |
|-----------------|-----------------------------|
| player_ratings/ | JSON с оценками игроков     |
| user_data/      | Аватары и фоны пользователей|
| image_cache/    | Кэш эмблем клубов           |
| Эмблемы/        | Логотипы лиг и клубов       |
```

# Основные функции

## Для всех пользователей

- 🔐 Авторизация: вход и регистрация с хешированием паролей
- ⚽ Добавление матчей: выбор команд, счёт, статус, комментарий
- ⭐ Оценка игроков: каждому игроку оценка от 1 до 10
- 📊 Статистика матче: просмотр всех добавленных событий
- 🏆 Достижения: автоматическая выдача за 1, 10, 50, 100 матчей
- 💬 Чат: общение с другими пользователями, правила чата
- 🖼️ Персонализация: смена аватара и фонового изображения

## Для администратора

- 👥 Управление пользователями: блокировка/разблокировка
- 🏟️ Управление клубами: добавление/удаление клубов по лигам
- 🧑‍🤝‍🧑 Управление игроками: добавление/удаление игроков с фото
- 📋 Просмотр всех событий: статистика по всем пользователям

# **Установка**

- Установить ZIP-файл program
- Извлечь все в любую свободную папку, созданную ранее
- Запустить файл program.exe
