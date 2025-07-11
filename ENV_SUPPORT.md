# Поддержка переменных окружения

OPDS Browser теперь поддерживает загрузку настроек из файла `.env` и переменных окружения.

## Установка зависимостей

```bash
pip install python-dotenv
```

## Создание .env файла

Скопируйте пример файла:

```bash
cp env.example .env
```

## Поддерживаемые переменные

### Логирование

| Переменная | Описание | Значения по умолчанию |
|------------|----------|----------------------|
| `OPDS_DISABLE_LOGS` | Отключить все логи | `false` |
| `OPDS_LOG_LEVEL` | Уровень логирования | `INFO` |

### Сетевые настройки

| Переменная | Описание | Значения по умолчанию |
|------------|----------|----------------------|
| `OPDS_DEFAULT_CATALOG` | URL каталога по умолчанию | - |
| `OPDS_TIMEOUT` | Таймаут запросов (секунды) | `30` |
| `OPDS_USER_AGENT` | User-Agent для HTTP запросов | `OPDS-Browser/1.0` |
| `OPDS_PROXY_URL` | URL прокси сервера | - |
| `OPDS_PROXY_USERNAME` | Имя пользователя для прокси | - |
| `OPDS_PROXY_PASSWORD` | Пароль для прокси | - |

## Приоритет настроек

1. **Переменные окружения** (высший приоритет)
2. **Файл .env** (если существует)
3. **config.json** (низший приоритет)

## Примеры использования

### Базовый .env файл

```env
# Логирование
OPDS_LOG_LEVEL=INFO
OPDS_DISABLE_LOGS=false

# Каталог по умолчанию
OPDS_DEFAULT_CATALOG=https://flibusta.is/opds
```

### .env файл с прокси

```env
# Логирование
OPDS_LOG_LEVEL=WARNING

# Сетевые настройки
OPDS_TIMEOUT=60
OPDS_USER_AGENT=MyOPDSBrowser/1.0

# Прокси
OPDS_PROXY_URL=http://proxy.example.com:8080
OPDS_PROXY_USERNAME=username
OPDS_PROXY_PASSWORD=password
```

### .env файл для отладки

```env
# Подробные логи
OPDS_LOG_LEVEL=DEBUG

# Увеличенный таймаут
OPDS_TIMEOUT=120

# Кастомный User-Agent
OPDS_USER_AGENT=OPDS-Debug/1.0
```

## Переменные окружения в командной строке

```bash
# Windows PowerShell
$env:OPDS_LOG_LEVEL="DEBUG"
$env:OPDS_DISABLE_LOGS="false"
python opds_browser_gui.py

# Linux/macOS
export OPDS_LOG_LEVEL=DEBUG
export OPDS_DISABLE_LOGS=false
python opds_browser_gui.py
```

## Отладка загрузки переменных

Включите DEBUG логирование, чтобы увидеть процесс загрузки переменных:

```bash
$env:OPDS_LOG_LEVEL="DEBUG"
python opds_browser_gui.py
```

Вы увидите сообщения типа:
```
DEBUG:Loaded environment variables from .env file
DEBUG:Configured proxy: http://proxy.example.com:8080
```

## Безопасность

- Файл `.env` не должен попадать в систему контроля версий
- Добавьте `.env` в `.gitignore`
- Храните пароли в безопасном месте
- Используйте переменные окружения для чувствительных данных

## Совместимость

- Поддержка Windows, Linux, macOS
- Автоматическое определение кодировки файла
- Graceful fallback при отсутствии python-dotenv
- Обратная совместимость с существующими настройками 