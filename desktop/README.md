# RivalScope Desktop

Desktop-клиент на PyQt6 для RivalScope.

## Запуск

Сначала запустите backend из корня проекта:

```powershell
python run.py
```

Затем в отдельном терминале:

```powershell
cd desktop
pip install -r requirements.txt
python main.py
```

## Сборка .exe

```powershell
cd desktop
python build.py
```

Готовый файл появится в `desktop/dist/RivalScope.exe`.
