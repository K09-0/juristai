# Список задач для завершения JurystAi

## Статус: ~60% готовности

---

## 🔴 КРИТИЧНО (Исправить немедленно)

### 1. Безопасность

- [ ] **Ротировать ключи Supabase**
  - Текущие ключи скомпрометированы (в Git)
  - Зайти в Supabase Dashboard → API → Reset keys
  - Обновить в Railway и Vercel

- [ ] **Добавить `.env` в `.gitignore`**
  - Файл: `/.gitignore`
  - Добавить строку: `.env`
  - Удалить `.env` из Git: `git rm --cached .env`

- [ ] **Проверить CORS (ИСПРАВЛЕНО ✅)**
  - ~~Было: `allow_origins=["*"]`~~
  - Теперь: Использует переменную `CORS_ORIGINS` для juristai.site

### 2. Код и архитектура

- [ ] **Удалить дублирующийся `main.py`**
  - Удалить: `/backend/main.py` (монолитный, устаревший)
  - Оставить: `/backend/app/main.py` (модульный, современный)
  - Обновить импорты в тестах если есть

- [ ] **Удалить дублирующиеся config.py**
  - Удалить: `/backend/config.py` (legacy)
  - Удалить: `/backend/app/core/config.py` (дубль)
  - Оставить: `/backend/app/config.py`
  - Обновить все импорты: `from app.config import settings`

- [ ] **Консолидировать модели БД**
  - Удалить модели из: `/backend/app/main.py`
  - Удалить: `/backend/app/models.py`
  - Оставить: `/backend/app/db/models.py` как единственный источник
  - Обновить alembic env.py: `from app.db.models import Base`

- [ ] **Исправить Alembic миграции**
  - Файл: `/backend/alembic/env.py`
  - Изменить: `from backend.app.main import Base`
  - На: `from app.db.models import Base`
  - Создать директорию: `/backend/alembic/versions/` если не существует
  - Запустить: `alembic upgrade head`

---

## ⚠️ ВАЖНО (Завершить до запуска)

### 3. Frontend - Страницы аутентификации

- [ ] **Создать `/app/auth/login/page.tsx`**
  - Форма входа (email, password)
  - Интеграция с API: `POST /auth/login`
  - Сохранение JWT токенов
  - Редирект на /dashboard после успешного входа

- [ ] **Создать `/app/auth/register/page.tsx`**
  - Форма регистрации (email, password, username, full_name)
  - Интеграция с API: `POST /auth/register`
  - Валидация полей
  - Редирект на /auth/login после регистрации

- [ ] **Создать `/app/auth/layout.tsx`**
  - Общий layout для auth страниц
  - Центрированная карточка
  - Logo и брендинг

### 4. Frontend - Dashboard

- [ ] **Создать `/app/dashboard/page.tsx`**
  - Protected route (проверка JWT)
  - Отображение лимитов (10/день или Premium)
  - Форма RAG запроса
  - История запросов
  - Кнопка Upgrade to Premium

- [ ] **Создать `/app/dashboard/layout.tsx`**
  - Header с навигацией
  - Sidebar с меню:
    - RAG поиск
    - Генерация документов
    - Анализ договоров
    - История
    - Настройки
  - Кнопка выхода

### 5. Frontend - API клиент

- [ ] **Создать `/lib/api.ts`**
  - Axios instance с baseURL
  - Request interceptor (добавление JWT токена)
  - Response interceptor (обработка 401, refresh token)
  - Типизированные методы:
    - `auth.register()`
    - `auth.login()`
    - `auth.refresh()`
    - `rag.query()`
    - `documents.generate()`
    - `payments.status()`

- [ ] **Создать `/lib/auth.ts`**
  - `getToken()` - получить access token из localStorage
  - `setTokens()` - сохранить access + refresh
  - `clearTokens()` - очистить при logout
  - `isAuthenticated()` - проверка наличия токена

- [ ] **Создать `/components/ProtectedRoute.tsx`**
  - HOC для защищенных страниц
  - Проверка JWT токена
  - Редирект на /auth/login если не авторизован

### 6. Backend - Завершить сервисы

- [ ] **Реализовать `/backend/app/services/redlining_service.py`**
  - Класс `RedliningService`
  - Метод `analyze_contract(docx_path, party_role, risk_level)`
  - Метод `create_redlined_document(input_path, output_path, risks, party_role)`
  - Интеграция с Groq LLM для анализа рисков
  - Использование python-docx для разметки

- [ ] **Завершить `/backend/app/services/vector_store.py`**
  - Проверить метод `add_document()`
  - Проверить метод `search_similar()`
  - Интеграция с Supabase pgvector
  - Тестирование поиска по законодательству РК

- [ ] **Проверить `/backend/app/services/groq_service.py`**
  - Файл урезан (последние 20 строк отсутствуют)
  - Восстановить полный код
  - Проверить все методы:
    - `generate_rag_response()`
    - `generate_document()`
    - `transcribe_audio()`
    - `analyze_audio_content()`

### 7. Интеграция роутеров

- [ ] **Подключить роутеры к main.py**
  - Файл: `/backend/app/main.py`
  - Добавить:
    ```python
    from app.api import rag, documents, audio, redlining, payments

    app.include_router(rag.router, prefix="/rag", tags=["RAG"])
    app.include_router(documents.router, prefix="/documents", tags=["Documents"])
    app.include_router(audio.router, prefix="/audio", tags=["Audio"])
    app.include_router(redlining.router, prefix="/redlining", tags=["Redlining"])
    app.include_router(payments.router, prefix="/payments", tags=["Payments"])
    ```

---

## 📝 ЖЕЛАТЕЛЬНО (Улучшение качества)

### 8. Тестирование

- [ ] **Создать `/backend/tests/`**
  - `test_auth.py` - тесты аутентификации
  - `test_rag.py` - тесты RAG системы
  - `test_documents.py` - тесты генерации документов
  - `conftest.py` - фикстуры pytest

- [ ] **Настроить pytest в CI/CD**
  - Файл: `.github/workflows/ci.yml`
  - Убрать `continue-on-error: true`
  - Сделать тесты блокирующими

- [ ] **Добавить integration тесты**
  - Тесты с реальной БД (test database)
  - Тесты API endpoints (TestClient)

### 9. Документация

- [ ] **Расширить README.md**
  - Добавить скриншоты
  - Примеры использования API
  - Troubleshooting секция

- [ ] **Создать API документацию**
  - Расширить docstrings в endpoints
  - Добавить примеры request/response
  - Swagger UI описания

- [ ] **Создать User Guide**
  - Как пользоваться RAG поиском
  - Как генерировать документы
  - Как оформить Premium подписку

### 10. Мониторинг и логирование

- [ ] **Настроить Sentry**
  - Регистрация на sentry.io
  - Установка: `pip install sentry-sdk`
  - Интеграция в main.py
  - Отслеживание ошибок в реальном времени

- [ ] **Structured logging**
  - Использовать `structlog` (уже в зависимостях)
  - Логирование всех запросов
  - Логирование ошибок с контекстом

- [ ] **Metrics и Analytics**
  - Prometheus metrics (опционально)
  - Google Analytics для фронтенда
  - Отслеживание использования API

### 11. Performance

- [ ] **Кеширование**
  - Redis для кеширования RAG результатов
  - Cache для популярных запросов
  - TTL: 1 час

- [ ] **Rate Limiting**
  - Middleware для ограничения запросов
  - Использовать Redis или slowapi
  - Разные лимиты для Free/Premium

- [ ] **Database Optimization**
  - Добавить индексы для частых запросов
  - Connection pooling (уже настроен)
  - Query optimization

---

## 🎨 ОПЦИОНАЛЬНО (Улучшения UX)

### 12. Frontend UI/UX

- [ ] **Улучшить дизайн**
  - Использовать UI библиотеку (shadcn/ui, Chakra UI)
  - Адаптивный дизайн для мобильных
  - Dark mode

- [ ] **Интерактивные элементы**
  - Loading states
  - Error boundaries
  - Toast notifications (react-hot-toast)

- [ ] **Анимации**
  - Framer Motion для плавных переходов
  - Skeleton loaders

### 13. Дополнительные фичи

- [ ] **Export документов**
  - Скачивание в DOCX
  - Скачивание в PDF
  - Копирование в буфер обмена

- [ ] **История запросов**
  - Сохранение всех RAG запросов
  - Возможность повторного выполнения
  - Поиск по истории

- [ ] **Шаринг**
  - Поделиться результатом RAG запроса
  - Сгенерировать публичную ссылку
  - Экспорт в социальные сети

---

## Приоритизация

**Неделя 1 (Критично):**
1. Ротация ключей Supabase
2. Удаление дубликатов кода
3. Исправление Alembic
4. Завершение сервисов (redlining, vector_store, groq)

**Неделя 2 (Frontend):**
5. Страницы auth (login, register)
6. Dashboard
7. API клиент
8. Protected routes

**Неделя 3 (Интеграция):**
9. Подключение роутеров
10. Тестирование интеграции
11. Деплой на staging

**Неделя 4 (Качество):**
12. Написание тестов
13. Документация
14. Мониторинг
15. Production деплой

---

## Чеклист перед Production

- [ ] Все критические задачи выполнены
- [ ] Все важные задачи выполнены
- [ ] Тесты проходят (coverage > 70%)
- [ ] CORS настроен правильно
- [ ] Секреты не в Git
- [ ] DNS настроен и работает
- [ ] SSL сертификаты активны
- [ ] Мониторинг настроен
- [ ] Backup БД настроен
- [ ] Rate limiting работает
- [ ] Документация обновлена
- [ ] Команда обучена

---

Когда все задачи из секций **КРИТИЧНО** и **ВАЖНО** будут выполнены, проект будет готов к production запуску на juristai.site!
