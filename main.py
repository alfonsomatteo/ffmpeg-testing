from fastapi import FastAPI, UploadFile, File
import subprocess
import os
import tempfile

# Crea l'istanza FastAPI
app = FastAPI()

# Log di avvio per confermare che il server è attivo
print("Server FastAPI in fase di avvio...")

# Endpoint di test per verificare se il server è in esecuzione
@app.get("/")
async def root():
    return {"message": "Server is running"}

# Endpoint principale per il processamento del podcast
@app.post("/process-podcast/")
async def process_podcast(stacchetto: UploadFile = File(...), background_music: UploadFile = File(...), files: list[UploadFile] = File(...)):
    # Percorsi temporanei per i file caricati
    input_files = []
    
    # Salviamo i file audio (intervistatore, intervistato, ecc.)
    for idx, file in enumerate(files):
        file_path = f"/app/audio{idx}.mp3"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        input_files.append(file_path)

    # Salviamo lo stacchetto iniziale
    stacchetto_path = "/app/stacchetto.mp3"
    with open(stacchetto_path, "wb") as f:
        f.write(await stacchetto.read())
    
    # Salviamo la musica di sottofondo
    background_music_path = "/app/background_music.mp3"
    with open(background_music_path, "wb") as f:
        f.write(await background_music.read())

    # Combinare la musica di sottofondo e lo stacchetto all'inizio
    podcast_with_music = "/app/podcast_with_music.mp3"
    subprocess.run(f"ffmpeg -i {stacchetto_path} -i {background_music_path} -filter_complex \"[0] [1] amerge=inputs=2[a]\" -map [a] {podcast_with_music}", shell=True)

    # Unire il resto dei file audio con la musica di sottofondo
    podcast_final = "/app/final_podcast.mp3"
    file_paths_str = " ".join(input_files)  # Percorsi dei file audio
    subprocess.run(f"ffmpeg -i {podcast_with_music} -i {file_paths_str} -filter_complex \"[0][1]concat=n={len(input_files)+1}:v=0:a=1[a]\" -map [a] {podcast_final}", shell=True)

    return {"message": "Podcast creato con successo!", "file": podcast_final}

# Log per confermare che il server è avviato
print("Server FastAPI avviato e pronto per ricevere richieste")
