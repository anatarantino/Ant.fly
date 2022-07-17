from typing import Optional, Union

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from connectdb import Connection


connectionDB = Connection()
connectionDB.connect()
connectionDB.create_tables()


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
]

status_codes = {
    'ok': 200,
    'unauthorized': 401,
    'error': 404,
    'conflict': 409,

}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    id_user: int = -1
    email: str
    password: str
    username: str

class Settings(BaseModel):
    authjwt_secret_key: str = "my_jwt_secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/")
def read_root():
    return {"Hello": "World Rasyue"}

@app.post('/register')
def register(user: User, Authorize: AuthJWT = Depends()):
    if connectionDB.register(user) == -1:
        raise HTTPException(status_code=status_codes['conflict'], detail=f"Email {user.email} already exists.")
    print(user)
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"detail": "user registered successfully","status_code":200}
    )

@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    result = connectionDB.login(user)
    if result == -1:
        raise HTTPException(status_code=status_codes['unauthorized'], detail=f"Email {user.email} is not registered.")
    if result == -2:
        raise HTTPException(status_code=status_codes['unauthorized'], detail=f"Password does not match.")

    access_token = Authorize.create_access_token(subject=user.id_user)
    return {"access_token": access_token}

@app.get('/home')
def home(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    links = connectionDB.get_user_links(current_user)
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"links": links, "status_code": 200}
    )

@app.post('/{short_link}')
def create_link(long_link, user: User, short_link, title: Optional[str] = None):

    if connectionDB.create_link(long_link, short_link, user, title) == -1:
        raise HTTPException(status_code=status_codes['conflict'], detail=f"Link {short_link} already exists.")
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"detail": "Link created successfully"}
    )


@app.delete('/{short_link}')
def delete_link(short_link):
    if connectionDB.delete_link(short_link) == -1:
        raise HTTPException(status_code=status_codes['error'], detail=f"Link {short_link} doesn't exist.")
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"detail": "Link deleted successfully"}
    )

@app.put("/{short_link}")
def change_link(old_link, short_link, title: Optional[str] = None):
    if connectionDB.change_link(old_link, short_link) == -1:
        raise HTTPException(status_code=status_codes['error'], detail=f"Link {old_link} doesn't exist.")
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"detail": "Link changed successfully"}
    )


@app.get('/test-jwt')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"user": 123124124, 'data': 'jwt test works'}
    # current_user = Authorize.get_jwt_subject()
    # return {"user": current_user, 'data': 'jwt test works'}

