# RivalScope

RivalScope — AI-анализатор рынка конкурентов для NeiroBridge. Приложение помогает анализировать сайты, тексты и визуальные материалы конкурентов, строить scorecard и получать практический план улучшений.

## Возможности

- Анализ текста конкурента: сильные стороны, слабые стороны, УТП, рекомендации.
- Анализ изображений: маркетинговые инсайты, визуальный стиль и потенциал анимации.
- Анализ сайтов через Selenium: загрузка страницы, извлечение текста, скриншот, AI-вывод.
- Выбор ниши анализа: готовые варианты или пользовательская ниша.
- Динамический список конкурентов: пользователь может добавить свой бренд и несколько конкурентов.
- Режим сравнения: карточки конкурентов, сравнительная таблица и рекомендации по усилению своего бренда.
- Прогресс-бар для долгих AI-задач и блокировка кнопок на время анализа.
- История запросов в `history.json`.
- Desktop-приложение в `desktop/`.
- Задел под PDF-анализ и GigaChat fallback.

## Технологии

- Backend: Python, FastAPI, Uvicorn, Pydantic.
- AI: ProxyAPI с OpenAI-совместимым SDK, модели `gpt-4o-mini` и `gpt-4o`.
- Парсинг: Selenium, webdriver-manager, BeautifulSoup4, httpx.
- Frontend: HTML, CSS, Vanilla JS.
- Desktop: PyQt6.
- Сборка: PyInstaller.

## Быстрый старт

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy env.example.txt .env
```

Откройте `.env` и добавьте ключ:

```env
PROXY_API_KEY=ваш_ключ_proxyapi
```

Запуск:

```powershell
python run.py
```

Веб-интерфейс: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

## Desktop

```powershell
cd desktop
pip install -r requirements.txt
python main.py
```

Сборка `.exe`:

```powershell
cd desktop
python build.py
```

После сборки файл будет доступен по пути `desktop/dist/RivalScope.exe`.

## Структура

```text
RivalScope/
├── backend/
├── frontend/
├── desktop/
├── data/
├── reports/
├── requirements.txt
├── run.py
├── README.md
├── docs.md
└── env.example.txt
```

## Важно

Не загружайте `.env` в публичный репозиторий. Файл уже добавлен в `.gitignore`.
