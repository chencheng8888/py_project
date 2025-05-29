from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from config import load_config
from chat import ChatService
from suggest import SuggestController
from evaluate import EvaluateController

app = Flask(__name__)

# CORS配置
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"]
    }
})

# 加载配置和初始化服务
try:
    cf = load_config("configs/config.yaml")
    chat_svc = ChatService(cf)
    evaluate_ctrl = EvaluateController(chat_svc)
    suggest_ctrl = SuggestController(chat_svc)
except Exception as e:
    raise RuntimeError(f"Failed to initialize services: {e}")

@app.route('/get_evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        result = evaluate_ctrl.evaluate(data)  # 调用同步方法
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_suggest', methods=['POST', 'OPTIONS'])
def suggest():
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "*")
        return response
    try:
        data = request.get_json()
        result = suggest_ctrl.suggest(data)  # 调用同步方法
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
