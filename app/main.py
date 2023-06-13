from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import user, post, fixture, auth, injuries, vote
from .config import settings



print(settings.database_name)

#create tables in DB defined in .models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#CORS middleware
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(fixture.router)
app.include_router(auth.router)
app.include_router(injuries.router)
app.include_router(vote.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to my API!!!!!"}

