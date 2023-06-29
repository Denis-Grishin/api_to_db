from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.chains import SQLDatabaseSequentialChain
from langchain.llms import OpenAI
from ..database import get_db
from ..config import settings
from fastapi import FastAPI, Query, Response, status, HTTPException, Depends, APIRouter
from pydantic import BaseModel



router = APIRouter(
    prefix="/chat", 
    tags=["chat"]
)

class Item(BaseModel):
    question: str

db = SQLDatabase.from_uri(get_db)
llm = OpenAI(openai_api_key=f"{settings.openai_api_key}", temperature=0, verbose=True)
chain = SQLDatabaseSequentialChain.from_llm(llm, db, verbose=True)

@router.post("/chat/")
async def query(item: Item):
    result = chain.run(item.question)  
    return {"result": result}


