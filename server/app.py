# server/app.py
from __future__ import annotations
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from models import ReviewerAction, CodeReviewObservation
from server.environment import CodeReviewEnvironment

app = FastAPI(title="CodeReviewArena - OpenEnv Environment")


def env_factory() -> CodeReviewEnvironment:
    task_id = os.getenv("TASK_ID", "task1_easy")
    seed    = int(os.getenv("SEED", "42"))
    return CodeReviewEnvironment(task_id=task_id, seed=seed)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    return {
        "name":        "code_review_arena",
        "version":     "1.0.0",
        "description": "Adversarial Multi-Agent Code Review RL Environment",
        "tasks":       ["task1_easy", "task2_medium", "task3_hard"],
        "themes":      ["multi-agent", "self-improvement", "world-modeling"],
    }


@app.get("/schema")
def schema():
    return {
        "action":      ReviewerAction.model_json_schema(),
        "observation": CodeReviewObservation.model_json_schema(),
    }


@app.post("/reset")
async def reset(request: Request):
    try:
        body = {}
        try:
            body = await request.json()
        except Exception:
            pass
        task_id = body.get("task_id", os.getenv("TASK_ID", "task1_easy"))
        seed    = int(body.get("seed",    os.getenv("SEED",    "42")))
        env     = CodeReviewEnvironment(task_id=task_id, seed=seed)
        app.state.env = env
        obs = env.reset()
        return JSONResponse(content={
            "observation": obs.model_dump(),
            "info": {"task_id": task_id, "seed": seed},
        })
    except Exception as e:
        tb = traceback.format_exc()
        print(f"RESET ERROR:\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": tb},
        )


@app.post("/step")
async def step(request: Request):
    try:
        body   = await request.json()
        action_data = body.get("action", body)
        action = ReviewerAction(**action_data)
        env    = getattr(app.state, "env", None)
        if env is None:
            env = env_factory()
            env.reset()
            app.state.env = env
        obs, reward, done, info = env.step(action)
        return JSONResponse(content={
            "observation": obs.model_dump(),
            "reward":      reward,
            "done":        done,
            "info":        info,
        })
    except Exception as e:
        tb = traceback.format_exc()
        print(f"STEP ERROR:\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": tb},
        )


@app.get("/state")
def state():
    try:
        env = getattr(app.state, "env", None)
        if env is None:
            return JSONResponse(content={"state": "idle"})
        return JSONResponse(content=env.state)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})


def main():
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()