from typing import Optional, Union

import jwt
import store as store
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

class UrlData(BaseModel):
    short_link: str
    title: str
    long_link: str

class TagData(BaseModel):
    tag_name: str
    short_link: str

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
    username = connectionDB.get_username(current_user)
    userTags = connectionDB.get_user_tags(current_user)
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"links": links,"username":username,"userTags": userTags, "status_code": 200}
    )

auth_scheme = HTTPBearer()
@app.post('/url/{short_link}')
def create_link(url_data: UrlData, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    settings = Settings()
    decoded = jwt.decode(token.credentials, settings.authjwt_secret_key, algorithms=["HS256"])
    id_user = decoded['sub']
    if connectionDB.create_link(url_data.long_link, url_data.short_link, id_user, url_data.title) == -1:
        raise HTTPException(status_code=status_codes['conflict'], detail=f"Link {url_data.short_link} already exists.")
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"detail": "Link created successfully"}
    )

auth_scheme = HTTPBearer()
@app.delete('/{short_link}')
def delete_link(short_link, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    settings = Settings()
    decoded = jwt.decode(token.credentials, settings.authjwt_secret_key, algorithms=["HS256"])
    id_user = decoded['sub']
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

auth_scheme = HTTPBearer()
@app.post("/url/{short_link}/tags/{tag}")
def create_tag(tag_data: TagData, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    print("en create tag")
    print(tag_data)
    settings = Settings()
    decoded = jwt.decode(token.credentials, settings.authjwt_secret_key, algorithms=["HS256"])
    id_user = decoded['sub']
    print(id_user)
    result = connectionDB.create_tag(tag_data.short_link, tag_data.tag_name, id_user)
    if result == -1:
        raise HTTPException(status_code=status_codes['error'], detail=f"Link {tag_data.short_link} doesn't exist.")
    elif result == -2:
        raise HTTPException(status_code=status_codes['error'], detail=f"Link {tag_data.short_link} already has 5 tags")
    return JSONResponse(
        status_code=status_codes['ok'],
        content={"detail": "Tag created successfully"}
    )


@app.get('/test-jwt')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"user": 123124124, 'data': 'jwt test works'}
    # current_user = Authorize.get_jwt_subject()
    # return {"user": current_user, 'data': 'jwt test works'}

