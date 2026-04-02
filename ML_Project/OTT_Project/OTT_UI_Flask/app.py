from flask import Flask, jsonify, render_template, request
from utils.code_meanings import CODE_MEANINGS
from utils.predictor import PredictionError, predict_from_manual_input, predict_from_user_seq

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/feature1")
def feature1():
    return render_template("feature1.html", code_meanings=CODE_MEANINGS)

@app.route("/api/predict/user-seq", methods=["POST"])
def api_predict_user_seq():
    try:
        payload = request.get_json(silent=True) or {}
        user_seq = int(str(payload.get("user_seq", "")).strip())
        result = predict_from_user_seq(user_seq)
        return jsonify({"success": True, "data": result})
    except ValueError:
        return jsonify({"success": False, "message": "사용자 번호를 숫자로 입력해주세요."}), 400
    except PredictionError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"예측 중 오류가 발생했습니다: {e}"}), 500

@app.route("/api/predict/manual", methods=["POST"])
def api_predict_manual():
    try:
        payload = request.get_json(silent=True) or {}
        result = predict_from_manual_input(payload)
        return jsonify({"success": True, "data": result})
    except PredictionError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"예측 중 오류가 발생했습니다: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
