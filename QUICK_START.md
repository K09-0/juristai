# JuristAI Quick Start Guide

## Что исправлено

1. Восстановлен поврежденный `groq_service.py`
2. Обновлен `database.py` для работы с Supabase
3. Добавлена функция `get_settings()` в config
4. Реализован `redlining_service.py`
5. Обновлены зависимости в requirements.txt
6. Создан `.env` с правильными переменными

## Быстрый старт с Docker

```bash
cd juristai

# 1. Добавьте свои API ключи в .env
nano .env
# Замените:
# - GROQ_API_KEY
# - GOOGLE_GENAI_API_KEY
# - HF_API_TOKEN (Hugging Face)

# 2. Запустите через Docker Compose
docker-compose up --build
```

Backend будет на http://localhost:8000
Frontend на http://localhost:3000

## Деплой на Railway (juristai.site)

### 1. Подготовка

В Railway Dashboard добавьте переменные окружения:

```bash
ENV=production
DEBUG=false
PORT=8000

# Supabase
SUPABASE_URL=https://0ec90b57d6e95fcbda19832f.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Keys (ваши ключи)
GROQ_API_KEY=gsk_...
GOOGLE_GENAI_API_KEY=AI...
HF_API_TOKEN=hf_...

# Security
SECRET_KEY=your-random-secret-key-min-32-chars

# CORS
CORS_ORIGINS=https://juristai.site,https://www.juristai.site,https://api.juristai.site

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-admin-password
```

### 2. Railway Deploy

1. Подключите GitHub репозиторий
2. Railway автоматически обнаружит `railway.json`
3. Dockerfile соберет backend
4. Получите URL: `your-app.railway.app`

### 3. Custom Domain (api.juristai.site)

В Railway → Settings → Networking:

1. Добавьте Custom Domain: `api.juristai.site`
2. Railway покажет CNAME:
   ```
   Type: CNAME
   Name: api
   Value: your-app.up.railway.app
   ```

3. Добавьте в DNS провайдере (Cloudflare/etc):
   - Name: `api`
   - Type: `CNAME`
   - Target: `your-app.up.railway.app`
   - Proxy: Off (или On если используете Cloudflare)

### 4. Frontend на Vercel

```bash
cd frontend

# Environment Variables в Vercel:
NEXT_PUBLIC_API_URL=https://api.juristai.site
NEXT_PUBLIC_SUPABASE_URL=https://0ec90b57d6e95fcbda19832f.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJI...

# Deploy
vercel --prod
```

В Vercel → Domains:
- Добавьте `juristai.site` и `www.juristai.site`
- Следуйте инструкциям DNS

## API Endpoints

После деплоя проверьте:

```bash
# Health check
curl https://api.juristai.site/health

# Swagger docs
open https://api.juristai.site/docs

# Test auth
curl -X POST https://api.juristai.site/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "username": "testuser",
    "full_name": "Test User"
  }'
```

## База данных Supabase

Ваша база уже настроена:
- URL: `https://0ec90b57d6e95fcbda19832f.supabase.co`
- Ключ в `.env`

Необходимо создать таблицы:

```sql
-- users
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE,
  username text UNIQUE,
  is_premium boolean DEFAULT false,
  premium_until timestamptz,
  daily_requests_count int DEFAULT 0,
  last_request_date date,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- legal_documents
CREATE TABLE IF NOT EXISTS legal_documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  doc_type text,
  doc_number text,
  issue_date date,
  content text,
  source_url text,
  created_at timestamptz DEFAULT now()
);

-- document_chunks (для RAG)
CREATE TABLE IF NOT EXISTS document_chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid REFERENCES legal_documents(id),
  chunk_text text NOT NULL,
  embedding vector(384),
  chunk_index int,
  metadata jsonb,
  created_at timestamptz DEFAULT now()
);

-- query_logs
CREATE TABLE IF NOT EXISTS query_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  session_id uuid,
  query_text text,
  response_text text,
  sources_used jsonb,
  processing_time_ms int,
  created_at timestamptz DEFAULT now()
);

-- generated_documents
CREATE TABLE IF NOT EXISTS generated_documents (
  id serial PRIMARY KEY,
  user_id uuid,
  doc_type text,
  tone text,
  input_data jsonb,
  content text,
  created_at timestamptz DEFAULT now()
);

-- payments
CREATE TABLE IF NOT EXISTS payments (
  id serial PRIMARY KEY,
  user_id uuid,
  amount_kzt int,
  months int,
  status text,
  created_at timestamptz DEFAULT now()
);
```

## Структура проекта

```
juristai/
├── backend/
│   ├── app/
│   │   ├── api/          # API роуты
│   │   ├── services/     # Бизнес-логика
│   │   ├── config.py     # Конфигурация
│   │   ├── database.py   # Supabase клиент
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── package.json
│   └── next.config.js
├── .env                  # Переменные окружения
├── docker-compose.yml
└── railway.json
```

## Проверка работоспособности

1. Backend health: `curl https://api.juristai.site/health`
2. Frontend: `https://juristai.site`
3. Swagger: `https://api.juristai.site/docs`

## Особенности

- Premium: 5000 тг/мес на Kaspi +77017891857
- Бесплатно: 10 запросов/день
- Admin доступ: безлимит (логин/пароль из .env)
- RAG система: поиск по законодательству РК
- Генерация документов: иски, договоры, претензии
- Анализ договоров (redlining): выявление рисков

## Поддержка

- Email: support@juristai.site
- Kaspi: +77017891857
- GitHub: https://github.com/K09-0/juristai

## Что нужно добавить (опционально)

1. Заполнить Supabase таблицы законодательством РК
2. Настроить CI/CD в GitHub Actions
3. Добавить мониторинг (Sentry)
4. Настроить rate limiting
5. Добавить фронтенд страницы (login, dashboard)
