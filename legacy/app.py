from flask import Flask, render_template, request, jsonify
from chatbot import FAQChatbot

app = Flask(__name__)
bot = FAQChatbot("dataset.json", threshold=0.25)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()

    if not question:
        return jsonify({"error": "Pertanyaan tidak boleh kosong"}), 400

    hasil = bot.ask(question)
    return jsonify(hasil)


@app.route("/api/reload", methods=["POST"])
def reload_faq():

    bot.reload()
    return jsonify({"status": "ok", "total_faq": len(bot.faqs)})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "total_faq": len(bot.faqs)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
