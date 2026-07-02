from dotenv import load_dotenv

load_dotenv()

from functools import lru_cache  # noqa: E402
from typing import Annotated, Any  # noqa: E402

from agent.agent import construct_agent_graph, run_agent  # noqa: E402
from agent.models import InputOutputMessage  # noqa: E402
from fastapi import Depends, FastAPI, Request  # noqa: E402
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # noqa: E402


async def lifespan(app: FastAPI):
    async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as saver:
        app.state.agent = construct_agent_graph(saver)

        yield
    # cleanup on application close, if any required


@lru_cache
def get_agent(request: Request):
    return request.app.state.agent


app = FastAPI(lifespan=lifespan)


@app.post("/invoke")
async def invoke_agent(
    message: InputOutputMessage, agent: Annotated[Any, Depends(get_agent)]
) -> InputOutputMessage:
    return {"msg": await run_agent(agent, message)}
