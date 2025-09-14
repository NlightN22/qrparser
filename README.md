# qrparser

Микросервис на Python для извлечения QR-кодов из PDF.  
Stateless, модульный, по канонам ООП и best practices. Без зависимостей от сторонних веб-сервисов.

## Структура
- `src/qrparser/` — код пакета (config, core, services, web)
- `tests/` — тесты (pytest)
- консистентные стили: `.editorconfig`, `.gitattributes`, `.gitignore`

## Требования
- Python 3.11+

## Быстрый старт (Windows, PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
# (опционально) установить pytest для тестов:
python -m pip install -U pip
python -m pip install pytest
pytest -q