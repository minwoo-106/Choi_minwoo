from __future__ import annotations

from flask import Flask, jsonify, render_template, request

try:
    import oracledb
    try:
        oracledb.init_oracle_client(
            lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
        )
    except Exception:
        pass
except ImportError:
    oracledb = None

from utils.predictor import get_chart_data, predict_existing_member, predict_manual_input


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False

    @app.context_processor
    def inject_globals():
        return {"project_name": "OTT Retention AI"}

    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/existing")
    def existing_predict():
        return render_template("existing_predict.html")

    @app.get("/direct")
    def direct_predict():
        return render_template("direct_predict.html")

    @app.get("/api/charts/overview")
    def api_charts_overview():
        try:
            return jsonify({"ok": True, "charts": get_chart_data()})
        except Exception as exc:
            return jsonify({"ok": False, "message": str(exc)}), 500

    @app.post("/api/predict/existing")
    def api_predict_existing():
        payload = request.get_json(silent=True) or {}
        member_no = str(payload.get("member_no", "")).strip()
        if not member_no:
            return jsonify({"ok": False, "message": "회원 번호를 입력해 주시기 바랍니다."}), 400
        try:
            result = predict_existing_member(member_no)
            return jsonify({"ok": True, "result": result})
        except Exception as exc:
            return jsonify({"ok": False, "message": str(exc)}), 500

    @app.post("/api/predict/direct")
    def api_predict_direct():
        payload = request.get_json(silent=True) or {}
        try:
            result = predict_manual_input(payload)
            return jsonify({"ok": True, "result": result})
        except Exception as exc:
            return jsonify({"ok": False, "message": str(exc)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
