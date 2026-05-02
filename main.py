from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

load_dotenv()

from brain import process_command
from brain import process_command
from voice import text_to_audio_base64

app = FastAPI(title="J.A.R.V.I.S.")
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
async def root():
    with open("public/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Conexão WebSocket estabelecida")

    try:
        welcome = "Sistemas online. Bem-vindo, Senhor. Todos os módulos operacionais."
        audio_b64 = text_to_audio_base64(welcome)
        await websocket.send_json({
            "type": "welcome",
            "text": welcome,
            "audio": audio_b64,
            "actions": []
        })
    except Exception as e:
        print(f"Erro no welcome: {e}")

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "text":
                await websocket.send_json({"type": "status", "message": "Pensando..."})
                result = process_command(data["text"])
                audio_b64 = text_to_audio_base64(result["text"])
                await websocket.send_json({
                    "type": "response",
                    "text": result["text"],
                    "audio": audio_b64,
                    "actions": result["actions"]
                })

    except WebSocketDisconnect:
        print("Cliente desconectado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)