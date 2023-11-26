from fastapi import FastAPI, Response, Depends, Request, Query, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, RedirectResponse

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from crud.database import SessionLocal, engine
from sqlalchemy.orm import Session
from crud.models import User, Message, Base
from crud.crud import *
from pydantic import BaseModel
from crud.schemas import *
from websocket.socket_manager import ConnectionManager

class NotAuthenticatedException(Exception):
    pass

app = FastAPI()
SECRET = "super-secret-key"
manager = LoginManager(SECRET, '/login', use_cookie=True, custom_exception=NotAuthenticatedException)

socket_manager = ConnectionManager()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url='/login')

@app.websocket("/message-ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await socket_manager.broadcast(data)
    except:
        await socket_manager.disconnect(websocket)

@app.post('/login')
def login(response: Response, db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = read_user(db, username, password)
    if user is None:
        raise InvalidCredentialsException
    
    return user

    access_token = manager.create_access_token(
        data={'sub': username}
    )
    manager.set_cookie(response, access_token)
    return {'access_token': access_token}



@app.get("/")
def get_root():
    return FileResponse("index.html")

@app.get("/login")
def get_login():
    return FileResponse("login.html")

@app.get("/style.css")
def get_style():
    return FileResponse("style.css")

@app.get("/function.js")
def get_function():
    return FileResponse("function.js")

@app.get("/login.js")
def get_login_function():
    return FileResponse("login.js")

@app.post('/register')
def register_user(response: Response, data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = data.username
    password = data.password

    user = db_register_user(db, username, password)
    if user:
        access_token = manager.create_access_token(
            data={'sub': username}
        )
        manager.set_cookie(response, access_token)
        return Response(status_code=200, content="success")
    else:
        return Response(status_code=400)


@app.get("/logout")
def lotout(response: Response):
    response = RedirectResponse("/login", status_code = 302)
    response.delete_cookie(key = "access-token")
    return response

@app.get("/message")
def get_all_messages(db: Session = Depends(get_db)):
    return read_all_messages(db)



@app.post("/message")
async def post_message(message: MessageSchemaBase,  db: Session = Depends(get_db)):
    message_item = insert_message(message, db)
    message_item_json = MessageSchema.from_orm(message_item).json()
    await socket_manager.broadcast(message_item_json)
    return message_item


@app.get("/user/me")
def get_current_user(userId: int, db: Session = Depends(get_db)):
    return read_user_by_id(db, userId)

@manager.user_loader
def get_user(username: str, db: Session = None):
    if not db:
        with SessionLocal() as db:
            return get_user(username, db)
    
    return db.query(User).filter(User.name == username).first()


@app.get("/resources/{filename}")
def get_resources(filename: str):
    filepath = "resources/" + filename
    return FileResponse(filepath)