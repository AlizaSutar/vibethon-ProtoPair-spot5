from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

from passlib.context import CryptContext

# -------------------- FASTAPI SETUP --------------------
app = FastAPI()

# Templates & Static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------- DATABASE SETUP --------------------
DATABASE_URL = "postgresql://admin1:admin123@localhost:5432/aiml_db"
# 👉 Replace username, password, db name

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -------------------- USER MODEL --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Create table
Base.metadata.create_all(bind=engine)

# -------------------- PASSWORD HASHING --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# -------------------- HOME (LOGIN + REGISTER PAGE) --------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------- REGISTER --------------------
@app.post("/register")
def register(
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        return {"error": "Passwords do not match"}

    db = SessionLocal()

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        db.close()
        return {"error": "Email already registered"}

    hashed_password = hash_password(password)

    new_user = User(
        fullname=fullname,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.close()

    return RedirectResponse("/", status_code=303)

# -------------------- LOGIN --------------------
@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        db.close()
        return {"error": "Invalid email or password"}

    db.close()
    return RedirectResponse("/dashboard", status_code=303)

# -------------------- DASHBOARD --------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/learn", response_class=HTMLResponse)
def learn(request: Request):
    return templates.TemplateResponse("learn.html", {"request": request})

@app.get("/game", response_class=HTMLResponse)
def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})

@app.get("/build", response_class=HTMLResponse)
def build(request: Request):
    return templates.TemplateResponse("build.html", {"request": request})

@app.get("/quiz", response_class=HTMLResponse)
def quiz(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})