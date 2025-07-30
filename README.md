# OPDS Catalog Browser

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/kzayko/opds-browser)

Современный графический браузер для просмотра OPDS (Open Publication Distribution System) каталогов с поддержкой навигации, поиска и отображения деталей книг.

**🌐 GitHub**: https://github.com/kzayko/opds-browser

## ✨ Возможности

- 🌐 **Навигация по каталогам** - просмотр папок и книг с иконками
- 🔍 **Поиск** - поиск книг по названию и автору
- 📚 **Детали книг** - отображение обложек, авторов, описаний
- 💾 **Сохранение состояния** - автоматическое сохранение последней позиции
- ⚙️ **Управление каталогами** - добавление и выбор каталогов через GUI
- 🔄 **Навигация назад/вперед** - кнопки для перемещения по истории
- 📁 **Кнопка "Up"** - возврат к родительской папке
- 🎨 **Современный интерфейс** - Treeview с иконками для папок и книг
- 🔧 **Гибкая конфигурация** - поддержка переменных окружения и .env файлов
- 🌍 **Прокси поддержка** - настройка прокси через переменные окружения
- 📝 **Логирование** - настраиваемые уровни логирования
- ⚡ **CLI поддержка** - запуск с аргументами командной строки

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск приложения

```bash
# Базовый запуск
python opds_browser_gui.py

# С указанием каталога
python opds_browser_gui.py --catalog "https://flibusta.is/opds"
```

## 📋 Требования

- **Python** 3.7+
- **tkinter** (обычно включен в Python)
- **requests** - для HTTP запросов
- **Pillow** - для работы с изображениями
- **python-dotenv** - для загрузки переменных окружения

## ⚙️ Конфигурация

### Переменные окружения

Скопируйте файл `env.example` в `.env` и настройте переменные:

```bash
cp env.example .env
```

#### Основные настройки

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OPDS_DISABLE_LOGS` | Отключить все логи | `false` |
| `OPDS_LOG_LEVEL` | Уровень логирования | `INFO` |
| `OPDS_DEFAULT_CATALOG` | URL каталога по умолчанию | - |
| `OPDS_TIMEOUT` | Таймаут запросов (секунды) | `30` |
| `OPDS_USER_AGENT` | User-Agent для HTTP запросов | `OPDS-Browser/1.0` |

#### Настройки прокси

| Переменная | Описание |
|------------|----------|
| `OPDS_PROXY_URL` | URL прокси сервера |
| `OPDS_PROXY_USERNAME` | Имя пользователя для прокси |
| `OPDS_PROXY_PASSWORD` | Пароль для прокси |

### Файл конфигурации

Приложение использует файл `config.json` для сохранения настроек:

```json
{
  "catalogs": [
    {
      "name": "Flibusta",
      "url": "https://flibusta.is/opds"
    }
  ],
  "current_catalog": "https://flibusta.is/opds",
  "last_entry_id": "tag:root:authors",
  "last_entry_path": ["tag:root:authors", "tag:authors:Л"],
  "logging": {
    "enabled": true,
    "level": "INFO"
  }
}
```

## 🎯 Использование

### Управление каталогами

1. **Добавление каталога**: Нажмите кнопку "Add Catalog" в интерфейсе
2. **Выбор каталога**: Используйте выпадающий список для выбора активного каталога
3. **Сохранение**: Каталоги автоматически сохраняются в `config.json`

### Навигация

- **Клик по папке** - переход в папку
- **Клик по книге** - просмотр деталей книги
- **Кнопка Up** - возврат к родительской папке
- **Кнопка Back** - возврат по истории навигации
- **Кнопка Home** - возврат к корню каталога

### Поиск

1. Введите поисковый запрос в поле поиска
2. Нажмите Enter или кнопку "Search"
3. Результаты отобразятся в списке

## 🔧 Управление логированием

### Через переменные окружения

```bash
# Отключить логи
export OPDS_DISABLE_LOGS=true
python opds_browser_gui.py

# Установить уровень логирования
export OPDS_LOG_LEVEL=INFO
python opds_browser_gui.py

# Использовать .env файл
cp env.example .env
# Отредактируйте .env файл
python opds_browser_gui.py
```

### Через конфигурацию

Добавьте в `config.json`:

```json
{
  "logging": {
    "enabled": true,
    "level": "INFO"
  }
}
```

## 📁 Структура проекта

```
opds/
├── opds_browser_gui.py    # Основной GUI модуль
├── opds_browser.py        # Бэкенд для работы с OPDS
├── config.json            # Конфигурация и сохраненные данные
├── requirements.txt       # Зависимости Python
├── env.example           # Пример файла переменных окружения
├── CHANGELOG.md          # История изменений
├── ENV_SUPPORT.md        # Документация по переменным окружения
├── EXAMPLES.md           # Примеры использования
└── README.md             # Документация
```

## 🌐 Поддерживаемые OPDS каталоги

Приложение протестировано с:
- **Flibusta** (https://flibusta.is/opds)
- Другие каталоги, поддерживающие стандарт OPDS 1.1+

## 🛠️ Разработка

### Добавление новых функций

1. **Новые типы записей**: Расширьте логику в `get_entries()` в `opds_browser.py`
2. **Новые элементы интерфейса**: Добавьте виджеты в `setup_widgets()` в `opds_browser_gui.py`
3. **Новые настройки**: Добавьте поля в `config.json` и методы в GUI

### Отладка

Включите подробные логи:

```bash
export OPDS_LOG_LEVEL=DEBUG
python opds_browser_gui.py
```

## 📚 Документация

- **[EXAMPLES.md](EXAMPLES.md)** - Подробные примеры использования
- **[ENV_SUPPORT.md](ENV_SUPPORT.md)** - Документация по переменным окружения
- **[CHANGELOG.md](CHANGELOG.md)** - История изменений

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте подключение к интернету
2. Убедитесь, что OPDS каталог доступен
3. Включите DEBUG логи для диагностики
4. Проверьте формат `config.json`

## 🤝 Участие в разработке

Мы приветствуем вклад в развитие проекта! 

### Как внести свой вклад

1. **Fork репозитория**: https://github.com/kzayko/opds-browser
2. **Создайте ветку** для новой функции: `git checkout -b feature/amazing-feature`
3. **Внесите изменения** и зафиксируйте их: `git commit -m 'Add amazing feature'`
4. **Отправьте изменения** в ваш fork: `git push origin feature/amazing-feature`
5. **Создайте Pull Request**

### Отчеты об ошибках

Если вы нашли ошибку, создайте issue в репозитории:
https://github.com/kzayko/opds-browser/issues

### Предложения новых функций

Для предложения новых функций используйте GitHub Discussions:
https://github.com/kzayko/opds-browser/discussions

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для подробностей.

---

**⭐ Если проект вам понравился, поставьте звездочку на GitHub!** 