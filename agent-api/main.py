from dotenv import load_dotenv

load_dotenv()

from functools import lru_cache  # noqa: E402
from typing import Annotated, Any  # noqa: E402

from agent.agent import construct_agent_graph, run_agent  # noqa: E402
from fastapi import Depends, FastAPI, Request  # noqa: E402
from pydantic import BaseModel  # noqa: E402


async def lifespan(app: FastAPI):
    app.state.agent = construct_agent_graph()

    yield
    # cleanup on application close, if any required


@lru_cache
def get_agent(request: Request):
    return request.app.state.agent


app = FastAPI(lifespan=lifespan)


class InputOutputMessage(BaseModel):
    msg: str


@app.post("/invoke")
async def invoke_agent(
    message: InputOutputMessage, agent: Annotated[Any, Depends(get_agent)]
) -> InputOutputMessage:
    return {"msg": run_agent(agent, message.msg)}
