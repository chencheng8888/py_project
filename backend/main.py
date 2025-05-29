from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import load_config
from chat import ChatService
from suggest import SuggestController,SuggestRequest
from evaluate import EvaluateController,EvaluateRequest

app = FastAPI()

# 加载配置和初始化服务
try:
    cf = load_config("configs/config.yaml")
    chat_svc = ChatService(cf)
    evaluate_ctrl = EvaluateController(chat_svc)
    suggest_ctrl = SuggestController(chat_svc)
except Exception as e:
    raise RuntimeError(f"Failed to initialize services: {e}")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_evaluate")
async def evaluate(request: EvaluateRequest):
    try:
        result = await evaluate_ctrl.evaluate(request)
        return {"result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/get_suggest")
async def suggest(request: SuggestRequest):
    try:
        result = await suggest_ctrl.suggest(request)
        return {"result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
