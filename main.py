# main.py
from fastapi import FastAPI, UploadFile
import subprocess

app = FastAPI()

@app.post("/process-audio/")
async def process_audio(file: UploadFile):
    # Salva il file caricato
    with open("input.mp3", "wb") as f:
        f.write(await file.read())

    # Esegui FFmpeg per elaborare l'audio (esempio di comando)
    subprocess.run(["ffmpeg", "-i", "input.mp3", "output.mp3"])

    # Restituisci una risposta semplice
    return {"message": "File audio elaborato con successo!"}
