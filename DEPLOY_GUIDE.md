# Руководство по деплою JurystAi на juristai.site

## Текущий статус проекта

**Готовность:** ~60% (требуется доработка перед продакшн-запуском)

### Что работает ✅
- Backend API с JWT аутентификацией
- RAG-система для поиска по законодательству РК
- Генерация юридических документов
- Система подписки Premium (Kaspi: 5000 тг/мес)
- База данных PostgreSQL/Supabase
- Docker и Railway конфигурация

### Критические проблемы 🔴
- ❌ Утечка секретов Supabase в `.env` файле (ТРЕБУЕТСЯ РОТАЦИЯ)
- ⚠️ Дублирование кода (2 файла main.py, 3 config.py)
- ⚠️ Фронтенд не завершен (нет страниц auth/login, dashboard)
- ⚠️ Некоторые сервисы не реализованы (redlining_service.py пустой)

---

## Пошаговая инструкция по деплою

### Шаг 1: Подготовка переменных окружения

#### 1.1 Ротация ключей Supabase (ОБЯЗАТЕЛЬНО!)

Текущие ключи скомпрометированы (в Git). Выполните:

1. Зайдите в Supabase Dashboard: https://supabase.com/dashboard
2. Перейдите в Settings → API
3. Нажмите "Reset" для:
   - `anon` public key
   - `service_role` secret key
4. Обновите ключи в Railway и Vercel (см. ниже)

#### 1.2 Переменные для Railway (Backend)

В Railway Dashboard добавьте:

```bash
# Основные
ENV=production
DEBUG=false
PORT=8000

# База данных (Supabase или Railway Postgres)
DATABASE_URL=postgresql://user:password@host:5432/juristai

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_NEW_anon_key_after_rotation

# AI API Keys
GROQ_API_KEY=your_groq_api_key
GOOGLE_GENAI_API_KEY=your_google_genai_key

# JWT Security
SECRET_KEY=your-super-secret-random-string-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://juristai.site,https://www.juristai.site,https://api.juristai.site

# Logging
LOG_LEVEL=INFO

# Workers
WORKERS=4
```

#### 1.3 Переменные для Vercel (Frontend)

В Vercel Dashboard → Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://api.juristai.site
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_NEW_anon_key_after_rotation
```

---

### Шаг 2: Деплой Backend на Railway

#### 2.1 Подключение GitHub к Railway

1. Зайдите на https://railway.app
2. Создайте новый проект: **New Project** → **Deploy from GitHub repo**
3. Выберите репозиторий `juristai`
4. Railway автоматически обнаружит `railway.json`

#### 2.2 Настройка сервиса

1. В разделе **Settings**:
   - **Root Directory:** `backend`
   - **Build Command:** (автоматически из Dockerfile)
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. В разделе **Variables**:
   - Добавьте все переменные из Шага 1.2

3. В разделе **Networking**:
   - Получите URL вида: `your-app.railway.app`
   - Или настройте Custom Domain: `api.juristai.site`

#### 2.3 Настройка Custom Domain

1. В Railway → **Settings** → **Networking** → **Custom Domain**
2. Введите: `api.juristai.site`
3. Railway покажет CNAME запись:
   ```
   Type: CNAME
   Name: api
   Value: your-app.up.railway.app
   ```

4. Добавьте эту запись в DNS вашего домена (например, Cloudflare):
   - Войдите в панель DNS провайдера
   - Добавьте CNAME запись:
     - **Name:** `api`
     - **Target:** `your-app.up.railway.app`
     - **Proxy:** Отключить (или включить через Cloudflare)

5. Дождитесь propagation (5-60 минут)

#### 2.4 Проверка деплоя

```bash
curl https://api.juristai.site/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-22T10:00:00.000Z",
  "version": "1.0.0"
}
```

---

### Шаг 3: Деплой Frontend на Vercel

#### 3.1 Подключение GitHub к Vercel

1. Зайдите на https://vercel.com
2. **Add New Project** → **Import Git Repository**
3. Выберите `juristai`
4. Vercel автоматически обнаружит Next.js

#### 3.2 Настройка проекта

**Framework Preset:** Next.js
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `.next`
**Install Command:** `npm install`

#### 3.3 Environment Variables

В разделе **Environment Variables** добавьте:

```bash
NEXT_PUBLIC_API_URL=https://api.juristai.site
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_NEW_anon_key
```

#### 3.4 Custom Domain

1. В Vercel → **Settings** → **Domains**
2. Добавьте домены:
   - `juristai.site`
   - `www.juristai.site`

3. Vercel покажет DNS записи:
   ```
   Type: A
   Name: @
   Value: 76.76.21.21

   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

4. Добавьте их в DNS провайдера

5. Vercel автоматически выпустит SSL сертификат

#### 3.5 Проверка

Откройте https://juristai.site в браузере

---

### Шаг 4: Настройка базы данных

#### Вариант A: Использовать Supabase (Рекомендуется)

1. База уже настроена (из `.env`)
2. Выполните миграции:

```bash
# Локально или через Railway CLI
cd backend
alembic upgrade head
```

**ВАЖНО:** Исправьте ошибку в `/backend/alembic/env.py`:

Было:
```python
from backend.app.main import Base
```

Должно быть:
```python
from app.db.models import Base
```

#### Вариант B: Railway PostgreSQL

1. В Railway → **New** → **Database** → **PostgreSQL**
2. Railway создаст базу и выдаст `DATABASE_URL`
3. Скопируйте его в переменные окружения бэкенда
4. Выполните миграции

---

### Шаг 5: Настройка DNS (Полная схема)

В вашем DNS провайдере (Cloudflare, Reg.ru, etc.):

```dns
# Фронтенд (Vercel)
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com

# Backend (Railway)
Type: CNAME
Name: api
Value: your-app.up.railway.app
```

**Проверка DNS:**
```bash
nslookup juristai.site
nslookup www.juristai.site
nslookup api.juristai.site
```

---

## Проверка работоспособности

### 1. Backend Health Check
```bash
curl https://api.juristai.site/health
```

### 2. Swagger Docs
Откройте: https://api.juristai.site/docs

### 3. Регистрация пользователя
```bash
curl -X POST https://api.juristai.site/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "username": "testuser",
    "full_name": "Test User"
  }'
```

### 4. Frontend
Откройте: https://juristai.site

---

## Мониторинг и логи

### Railway (Backend)
1. Railway Dashboard → ваш проект
2. **Deployments** → выберите активный деплой
3. **View Logs** - реалтайм логи

### Vercel (Frontend)
1. Vercel Dashboard → ваш проект
2. **Deployments** → выберите продакшн деплой
3. **View Function Logs**

---

## Что нужно доработать перед полным запуском

### Критично 🔴

1. **Ротировать ключи Supabase** - текущие скомпрометированы
2. **Исправить миграции** - `/backend/alembic/env.py` имеет неверный импорт
3. **Реализовать фронтенд страницы:**
   - `/app/auth/login/page.tsx`
   - `/app/auth/register/page.tsx`
   - `/app/dashboard/page.tsx`
4. **Создать API клиент** - `lib/api.ts` для связи фронтенда с бэкендом
5. **Завершить сервисы:**
   - `/backend/app/services/redlining_service.py` (пустой)
   - `/backend/app/services/vector_store.py` (не завершен)

### Важно ⚠️

6. **Добавить `.env` в `.gitignore`** - предотвратить будущие утечки
7. **Удалить дубликаты:**
   - Выбрать 1 main.py (рекомендую `/backend/app/main.py`)
   - Выбрать 1 config.py (рекомендую `/backend/app/config.py`)
8. **Написать тесты** - pytest для API endpoints
9. **Настроить rate limiting** - защита от злоупотреблений
10. **Добавить мониторинг** - Sentry, LogTail или аналоги

---

## Архитектура деплоя

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────┐
│  juristai.site          │ ← Vercel (Next.js Frontend)
│  www.juristai.site      │
└────────┬────────────────┘
         │ API Calls
         │ HTTPS
         ▼
┌─────────────────────────┐
│  api.juristai.site      │ ← Railway (FastAPI Backend)
└────────┬────────────────┘
         │
         ├──► Supabase (PostgreSQL + Auth)
         ├──► Groq API (LLM)
         └──► Google GenAI (Gemini)
```

---

## Стоимость деплоя (примерно)

- **Railway:** $5-20/мес (в зависимости от трафика)
- **Vercel:** $0 (Hobby tier) или $20/мес (Pro)
- **Supabase:** $0 (Free tier) или $25/мес (Pro)
- **Домен juristai.site:** ~$10-15/год

**Итого:** $5-65/мес в зависимости от выбранных планов

---

## Поддержка и помощь

Если возникли проблемы:

1. Проверьте логи в Railway/Vercel
2. Проверьте переменные окружения
3. Убедитесь что DNS propagated: https://dnschecker.org
4. Проверьте CORS настройки если фронтенд не может подключиться к API

---

## Контакты

- **Kaspi для Premium:** +77017891857
- **Цена Premium:** 5000 тг/мес
- **Бесплатный тариф:** 10 запросов/день
