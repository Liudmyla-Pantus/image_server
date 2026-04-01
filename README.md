# Image Server

Невеликий веб-сервіс для завантаження, перегляду та видалення зображень.

## Функціонал

- Завантаження зображень (jpg, jpeg, png, gif)
- Генерація унікального імені файлу
- Отримання URL для кожного зображення
- Копіювання посилання
- Відображення галереї зображень
- Видалення зображень з сервера

## Технології

- Python (http.server)
- JavaScript (fetch API)
- HTML / CSS
- Pillow (перевірка зображень)
- Docker / Docker Compose
- Nginx

## Як запустити

1. Встановити залежності:
pip install -r requirements.txt

2. Запустити сервер:
python app.py

3. Відкрити у браузері:
http://localhost:8000

## Структура проекту

```
image_server/
├── app.py
├── images/
├── logs/
├── static/
│   ├── index.html
│   ├── form/
│   │   ├── upload.html
│   │   └── images.html
│   └── image-uploader/
│       ├── js/
│       │   ├── upload.js
│       │   └── images.js
│       ├── css/
│       └── img/
├── Dockerfile
├── compose.yaml
├── nginx.conf
├── requirements.txt
└── README.md
```

## Що було реалізовано

- Обробка HTTP-запитів (GET, POST, DELETE)
- Робота з файлами на сервері
- Валідація зображень
- REST API для отримання списку зображень
- Динамічне оновлення сторінки через JavaScript

## Рефакторинг

- прибрано дублювання коду при визначенні типів файлів
- винесено логіку визначення content type в окрему функцію

## Автор

Проект виконаний в рамках навчання.