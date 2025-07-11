# Примеры использования OPDS Browser

## Базовое использование

### Запуск с GUI
```bash
python opds_browser_gui.py
```

### Запуск с указанием каталога
```bash
python opds_browser_gui.py --catalog "https://flibusta.is/opds"
```

## Управление логированием

### Использование .env файла

Создайте файл `.env` на основе `env.example`:

```bash
cp env.example .env
```

Отредактируйте `.env` файл:

```env
# Отключить логи
OPDS_DISABLE_LOGS=true

# Или установить уровень логирования
OPDS_LOG_LEVEL=WARNING

# Настроить каталог по умолчанию
OPDS_DEFAULT_CATALOG=https://flibusta.is/opds

# Настроить прокси (опционально)
OPDS_PROXY_URL=http://proxy.example.com:8080
OPDS_PROXY_USERNAME=username
OPDS_PROXY_PASSWORD=password
```

### Отключение логов через переменную окружения
```bash
# Windows PowerShell
$env:OPDS_DISABLE_LOGS="true"
python opds_browser_gui.py

# Windows CMD
set OPDS_DISABLE_LOGS=true
python opds_browser_gui.py

# Linux/macOS
export OPDS_DISABLE_LOGS=true
python opds_browser_gui.py
```

### Установка уровня логирования
```bash
# Только ошибки
$env:OPDS_LOG_LEVEL="ERROR"
python opds_browser_gui.py

# Предупреждения и выше
$env:OPDS_LOG_LEVEL="WARNING"
python opds_browser_gui.py

# Информационные сообщения
$env:OPDS_LOG_LEVEL="INFO"
python opds_browser_gui.py

# Подробные отладочные сообщения
$env:OPDS_LOG_LEVEL="DEBUG"
python opds_browser_gui.py
```

### Управление логами через конфигурацию

Отредактируйте `config.json`:

```json
{
  "catalogs": [...],
  "logging": {
    "enabled": false,
    "level": "ERROR"
  }
}
```

## Навигация

### Поиск книг
1. Введите поисковый запрос в поле поиска
2. Нажмите Enter или кнопку "Search"
3. Результаты отобразятся в списке

### Навигация по папкам
1. Кликните на папку для перехода в неё
2. Используйте кнопку "Up" для возврата к родительской папке
3. Используйте кнопку "Back" для возврата по истории
4. Используйте кнопку "Home" для возврата к корню каталога

### Просмотр деталей книги
1. Кликните на книгу в списке
2. Детали отобразятся в нижней панели:
   - Название и автор
   - Описание
   - Обложка (если доступна)
   - Ссылки на скачивание

## Управление каталогами

### Добавление нового каталога
1. Нажмите кнопку "+" рядом с выпадающим списком каталогов
2. Введите название каталога
3. Введите URL каталога
4. Нажмите "Add"

### Переключение между каталогами
1. Выберите каталог из выпадающего списка
2. Приложение автоматически загрузит новый каталог

## Сохранение состояния

Приложение автоматически сохраняет:
- Список каталогов
- Текущий выбранный каталог
- Последнюю позицию в каталоге
- Настройки логирования

Данные сохраняются в файл `config.json`.

## Примеры конфигураций

### Минимальная конфигурация
```json
{
  "catalogs": [
    {
      "name": "Flibusta",
      "url": "https://flibusta.is/opds"
    }
  ],
  "logging": {
    "enabled": true,
    "level": "INFO"
  }
}
```

### Конфигурация с отключенными логами
```json
{
  "catalogs": [
    {
      "name": "Flibusta",
      "url": "https://flibusta.is/opds"
    }
  ],
  "logging": {
    "enabled": false,
    "level": "ERROR"
  }
}
```

### Конфигурация с прокси
```env
# .env файл
OPDS_PROXY_URL=http://proxy.example.com:8080
OPDS_PROXY_USERNAME=username
OPDS_PROXY_PASSWORD=password
OPDS_TIMEOUT=60
OPDS_USER_AGENT=MyOPDSBrowser/1.0
```

### Конфигурация с несколькими каталогами
```json
{
  "catalogs": [
    {
      "name": "Flibusta",
      "url": "https://flibusta.is/opds"
    },
    {
      "name": "Feedbooks",
      "url": "https://www.feedbooks.com/catalog.atom"
    }
  ],
  "logging": {
    "enabled": true,
    "level": "DEBUG"
  }
}
```

## Отладка

### Включение подробных логов
```bash
$env:OPDS_LOG_LEVEL="DEBUG"
python opds_browser_gui.py
```

### Проверка конфигурации
```bash
# Просмотр текущей конфигурации
Get-Content config.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Сброс конфигурации
```bash
# Удаление файла конфигурации (будет создан новый)
Remove-Item config.json
python opds_browser_gui.py
``` 