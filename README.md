# JurystAi - LegalTech SaaS для Казахстана

## 🎯 Что это?

LegalTech платформа с RAG системой для поиска по Нормативно-Правовым Актам (НПА) Республики Казахстан.

**Функциональность:**
- 🔍 RAG-поиск по 9 основным кодексам РК
- 📄 Загрузка и анализ документов
- 🎙️ Обработка аудио (транскрипция)
- ⚖️ Помощник по контрактам (Contract Redlining)
- 💰 Интеграция платежей (Kaspi Pay, LiqPay)

## 🚀 Быстрый старт

### Локальное разработка (Docker Compose)

```bash
git clone https://github.com/K09-0/juristai.git
cd juristai

cp backend/.env.example backend/.env

docker-compose up --build

# Проверяешь API
curl http://localhost:8000/health
curl http://localhost:3000
```

### Production деплой на Railway + Vercel

**Backend:**
1. https://railway.app → New Project → Deploy from GitHub
2. Выбери K09-0/juristai
3. Добавь Environment Variables (см. README в репо)

**Frontend:**
1. https://vercel.com → New Project → Import Git Repository
2. Выбери K09-0/juristai
3. Environment: `NEXT_PUBLIC_API_URL=https://api.juristai.site`

**DNS:**
1. https://cp.domainnameapi.com/login
2. Добавь CNAME: api → railway-domain
3. Добавь CNAME: www → vercel-domain

## 📡 API Endpoints

### Authentication
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход (access & refresh tokens)
- `POST /auth/refresh` - Обновление токена

### Health & Docs
- `GET /health` - Проверка статуса
- `GET /docs` - Swagger документация
- `GET /redoc` - ReDoc документация

## 🔐 Безопасность

- ✅ JWT с refresh tokens (access 30 мин, refresh 7 дней)
- ✅ Bcrypt для паролей
- ✅ CORS настроена
- ✅ SQL-injection защита
- ✅ HTTPS ready

## 🛠️ Tech Stack

**Backend:** FastAPI 0.109.0, SQLAlchemy 2.0, Alembic, Supabase, Groq, Google GenAI, Sentence Transformers

**Frontend:** Next.js 14, React 18, TailwindCSS 3.4, Lucide Icons, Supabase Client, Axios

## 📋 Статус

| Component | Статус | URL |
|-----------|--------|-----|
| Backend | ✅ Railway | https://api.juristai.site |
| Frontend | 🔄 Vercel | https://juristai.site |
| Database | ✅ Supabase | aatifhldykfrsozjxigl.supabase.co |

---

**Создано для JurystAi SaaS | Казахстан** 🇰🇿