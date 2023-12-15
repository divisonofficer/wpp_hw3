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
manager = LoginManager(
    SECRET, "/login", use_cookie=True, custom_exception=NotAuthenticatedException
)

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
    return RedirectResponse(url="/login")


@app.websocket("/message-ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await socket_manager.broadcast(data)
    except:
        await socket_manager.disconnect(websocket)


@app.post("/login")
def login(
    response: Response,
    db: Session = Depends(get_db),
    data: OAuth2PasswordRequestForm = Depends(),
):
    username = data.username
    password = data.password

    user = read_user(db, username, password)
    if user is None:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data={"sub": username})
    manager.set_cookie(response, access_token)
    return {"access_token": access_token}


"""

Frontend Routing

"""


@app.get("/")
def get_root(user=Depends(manager)):
    """if no user, throw NotAuthenticatedException"""
    if user is None:
        raise NotAuthenticatedException

    return FileResponse("index.html")


@app.get("/login")
def get_login():
    return FileResponse("login.html")


@app.get("/register")
def get_register_html():
    return FileResponse("register.html")


@app.get("/recommendfriend")
def get_recommendfriend_html(user=Depends(manager)):
    return FileResponse("recommendfriend.html")


@app.get("/profile/{id}")
def get_profile_html(id: int, user=Depends(manager)):
    return FileResponse("profile.html")


@app.get("/chatlobby")
def get_chatlobby_html(user=Depends(manager)):
    return FileResponse("chatlobby.html")


"""
Account API
"""


@app.post("/register")
def register_user(
    response: Response,
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    username = data.username
    password = data.password

    user = db_register_user(db, username, password)
    if user:
        access_token = manager.create_access_token(data={"sub": username})
        manager.set_cookie(response, access_token)
        return Response(status_code=200, content="success")
    else:
        return Response(status_code=400)


@app.get("/logout")
def lotout(response: Response):
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(key="access-token")
    return response


"""
Friend API

"""


@app.get("/friend")
def get_friends(user=Depends(manager), db: Session = Depends(get_db)):
    return read_friends(db, user.id)


@app.get("/friend/recommend")
def get_recommend_friend(user=Depends(manager), db: Session = Depends(get_db)):
    return read_candidate_friends(db, user.id)


@app.post("/friend/make")
def post_make_friend(
    request: MakeFriendRequest, user=Depends(manager), db: Session = Depends(get_db)
):
    return make_friend(db, user.id, request.friend_id)


@app.get("/user/me")
def get_current_user(user=Depends(manager), db: Session = Depends(get_db)):
    return read_user_by_id(db, user.id)


@app.get("/user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return read_user_by_id(db, user_id)


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


"""
CHATROOM API
"""


@app.get("/chatroom/p2p/{friend_id}")
def get_p2p_chatroom(
    friend_id: str, db: Session = Depends(get_db), user=Depends(manager)
):
    return getP2PChatRoomInfo(db, user.id, friend_id)


@app.delete("/chatroom/{chatroom_id}")
def delete_chatroom(chatroom_id: int, db: Session = Depends(get_db)):
    return removeChatroom(db, chatroom_id)


@app.get("/chatroom/list")
def get_user_chatroom_all(db: Session = Depends(get_db), user=Depends(manager)):
    return read_user_chatroom_all(db, user.id)


@app.delete("/chatroom/{chatroom_id}")
def delete_chatroom(chatroom_id: int, db: Session = Depends(get_db)):
    return removeChatroom(db, chatroom_id)


"""

MESSAGE API

"""


@app.get("/chatroom/{chatroom_id}")
def get_chatroom(chatroom_id: int, db: Session = Depends(get_db)):
    return FileResponse("chatroom.html")


@app.get("/chatroom/{chatroom_id}/message")
def get_chatroom_message(chatroom_id: int, db: Session = Depends(get_db)):
    return read_chatroom_message(db, chatroom_id)


@app.get("/message")
def get_all_messages(db: Session = Depends(get_db)):
    return read_all_messages(db)


@app.post("/chatroom/{chatroom_id}/message")
async def post_message(
    message: MessageSchemaBase, chatroom_id: int, db: Session = Depends(get_db)
):
    message_item = insert_message(message, chatroom_id, db)
    await socket_manager.broadcast(message_item)
    return message_item
