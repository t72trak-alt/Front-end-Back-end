from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import jwt
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User
from app.routers import auth, chat, projects, admin, services
from app.dependencies import get_current_user

app = FastAPI(title="AI Developer Portal", version="1.0")

SECRET_KEY = "your-super-secret-jwt-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(projects.router)
app.include_router(admin.router)
app.include_router(services.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    services_list = [
        {
            "icon": "🛠️",
            "title": "Промпт-инжиниринг",
            "items": [
                "Создание и оптимизация промптов для текста, изображений, аудио, видео",
                "Разработка контекстных систем для ИИ-ассистентов",
                "Интеграция с ChatGPT, Claude, Gemini, YandexGPT и др."
            ]
        },
        {
            "icon": "🤖",
            "title": "Разработка ИИ-решений",
            "items": [
                "ИИ-ассистенты и чат-боты",
                "Мультиагентные системы и автономные агенты",
                "MVP ИИ-продуктов 'под ключ'"
            ]
        },
        {
            "icon": "🏢",
            "title": "Интеграция ИИ в бизнес",
            "items": [
                "Внедрение ИИ в CRM (AmoCRM), мессенджеры, соцсети",
                "Автоматизация маркетинга, продаж и поддержки",
                "Создание систем аналитики на основе ИИ"
            ]
        },
        {
            "icon": "⚙️",
            "title": "Автоматизация бизнес-процессов",
            "items": [
                "Аудит и поиск точек для автоматизации",
                "Создание ИИ-инструментов для HR (прескрининг резюме)",
                "Анализ звонков, генерация контента"
            ]
        }
    ]
    portfolio = [
        {
            "title": "Illustraitor AI",
            "description": "Chrome-расширение для генерации изображений через DALL-E 3",
            "metrics": "15+ стилей генерации, 99% uptime",
            "link": "https://illustraitor-ai-v2.onrender.com"
        },
        {
            "title": "SMM-эксперт с ИИ",
            "description": "Автоматизация ведения соцсетей (ВКонтакте)",
            "metrics": "Снижение времени с 4 часов до 15 минут в день",
            "link": "#"
        }
    ]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "services": services_list,
        "portfolio": portfolio
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        user = await get_current_user(request)
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_admin": user.is_admin
            }
        })
    except HTTPException:
        return RedirectResponse(url="/login")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    try:
        user = await get_current_user(request)
        if not user.is_admin:
            return RedirectResponse(url="/dashboard")
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_admin": user.is_admin
            }
        })
    except HTTPException:
        return RedirectResponse(url="/login")

@app.get("/test-api")
async def test_api():
    return {"message": "API работает", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)