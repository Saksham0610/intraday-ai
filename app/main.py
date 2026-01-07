from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine
from .models import User
from .auth import hash_password, verify_password, get_db, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def home():
    return RedirectResponse("/login")

@app.get("/login")
def login_page(request: Request):
    if request.cookies.get("user"):
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return RedirectResponse("/login", status_code=302)

    response = RedirectResponse("/dashboard", status_code=302)

    response.set_cookie(
        key="user",
        value=email,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    return response

@app.get("/register")
def register_page(request: Request):
    if request.cookies.get("user"):
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@app.get("/dashboard")
def dashboard(
    request: Request,
    user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )

@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(
        key="user",
        path="/"
    )
    return response
