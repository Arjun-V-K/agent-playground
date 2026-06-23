from agent.agent import run_agent
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

app = FastAPI()


class InputOutputMessage(BaseModel):
    msg: str


@app.post("/invoke")
async def invoke_agent(message: InputOutputMessage) -> InputOutputMessage:
    return {"msg": run_agent(message.msg)}
