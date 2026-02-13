from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import jwt
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User
from app.routers import auth, chat, projects, admin, services, stats
from app.dependencies import get_current_user

app = FastAPI(title="AI Developer Portal", version="1.0")

# ========== CORS для WebSocket ==========
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
# ========================================

SECRET_KEY = "your-super-secret-jwt-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ========== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ==========
app.include_router(auth.router)      # /api/auth/*
app.include_router(chat.router)       # /api/chat/*
app.include_router(projects.router)   # /api/projects/*
app.include_router(admin.router)      # /api/admin/*
app.include_router(services.router)   # /api/services/*
app.include_router(stats.router)      # /api/stats/*
# ==========================================

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    services_list = [
        {
            "icon": "🤖",
            "title": "AI-разработка",
            "items": [
                "Интеграция с языковыми моделями для чатов, ассистентов, ботов, игр",
                "Создание умных агентов для веб-приложений",
                "Взаимодействие с ChatGPT, Claude, Gemini, YandexGPT и др."
            ]
        },
        {
            "icon": "💻",
            "title": "Разработка веб-приложений",
            "items": [
                "Веб-приложения с ИИ-функциями",
                "Полный цикл разработки: от идеи до внедрения",
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
            "description": "Chrome-расширение для генерации иллюстраций через DALL-E 3",
            "metrics": "15+ тысяч пользователей, 99% uptime",
            "link": "https://illustraitor-ai-v2.onrender.com"
        },
        {
            "title": "SMM-эксперт с ИИ",
            "description": "Автоматизация создания контента (тестирование)",
            "metrics": "Ускорение работы в 4 раза: с 15 часов до 1 часа в день",
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
        # ========== ИСПРАВЛЕНИЕ: Проверяем cookie ==========
        token = request.cookies.get("access_token")
        if not token:
            # Если нет cookie, пробуем заголовок Authorization
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
        
        if not token:
            # Нет токена - редирект на логин
            return RedirectResponse(url="/login")
        
        # Декодируем токен вручную
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                return RedirectResponse(url="/login")
            
            # Получаем пользователя из БД
            db = next(get_db())
            user = db.query(User).filter(User.id == int(user_id)).first()
            db.close()
            
            if not user:
                return RedirectResponse(url="/login")
            
            # Всё хорошо - показываем личный кабинет
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_admin": user.is_admin
                }
            })
            
        except jwt.InvalidTokenError:
            return RedirectResponse(url="/login")
        except Exception as e:
            print(f"Ошибка в dashboard: {e}")
            return RedirectResponse(url="/login")
            
    except Exception as e:
        print(f"Критическая ошибка в dashboard: {e}")
        return RedirectResponse(url="/login")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    try:
        # ========== ИСПРАВЛЕНИЕ: Проверяем cookie ==========
        token = request.cookies.get("access_token")
        if not token:
            # Если нет cookie, пробуем получить из заголовка Authorization
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
        
        if not token:
            # Нет токена - редирект на логин
            return RedirectResponse(url="/login")
        
        # Декодируем токен вручную
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                return RedirectResponse(url="/login")
            
            # Получаем пользователя из БД
            db = next(get_db())
            user = db.query(User).filter(User.id == int(user_id)).first()
            db.close()
            
            if not user:
                return RedirectResponse(url="/login")
            
            if not user.is_admin:
                return RedirectResponse(url="/dashboard")
            
            # Всё хорошо - показываем админку
            return templates.TemplateResponse("admin.html", {
                "request": request,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_admin": user.is_admin
                }
            })
        except jwt.InvalidTokenError:
            return RedirectResponse(url="/login")
        except Exception as e:
            print(f"Ошибка в admin_page: {e}")
            return RedirectResponse(url="/login")
            
    except Exception as e:
        print(f"Критическая ошибка в admin_page: {e}")
        return RedirectResponse(url="/login")

@app.get("/test-api")
async def test_api():
    return {"message": "API работает", "status": "ok"}

# Дополнительные страницы
@app.get("/services", response_class=HTMLResponse)
async def services_page(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})

# ========== WebSocket для тестирования ==========
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

@app.websocket("/test-ws")
async def test_websocket(websocket: WebSocket):
    """
    Простой тестовый WebSocket endpoint
    """
    await websocket.accept()
    try:
        # Отправляем приветственное сообщение
        await websocket.send_json({
            "status": "connected",
            "message": "WebSocket работает!",
            "timestamp": datetime.now().isoformat()
        })
        # Ожидаем сообщения от клиента
        while True:
            data = await websocket.receive_text()
            # Возвращаем эхо
            await websocket.send_json({
                "echo": data,
                "timestamp": datetime.now().isoformat(),
                "received": True
            })
    except WebSocketDisconnect:
        print("Клиент отключился от тестового WebSocket")

@app.get("/ws-test")
async def websocket_test_page(request: Request):
    """
    Страница для тестирования WebSocket
    """
    return templates.TemplateResponse("websocket_test.html", {"request": request})
# =================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)