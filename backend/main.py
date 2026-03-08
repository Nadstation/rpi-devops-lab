from http.server import BaseHTTPRequestHandler, HTTPServer
import pymysql
import json
import os
import requests

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "mariadb"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "devuser"),
        password=os.getenv("DB_PASSWORD", "devpassword"),
        database=os.getenv("DB_NAME", "devlab")
    )

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            response = {"message": "DevLab API is running! V2.0"}
        elif self.path == "/health":
            try:
                conn = get_db()
                conn.close()
                response = {"status": "ok", "database": "connected"}
            except Exception as e:
                response = {"status": "error", "database": str(e)}
        else:
            response = {"error": "not found"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(content_length))
            user_message = body.get("message", "")

            try:
                ollama_response = requests.post(
                    "http://ollama:11434/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": user_message,
                        "stream": False
                    }
                )
                reply = ollama_response.json().get("response", "No response")
                response = {"reply": reply}
            except Exception as e:
                response = {"error": str(e)}
        else:
            response = {"error": "not found"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Server running on port 8000...")
    server.serve_forever()
