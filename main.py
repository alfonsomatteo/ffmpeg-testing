from fastapi import FastAPI, UploadFile, File
import subprocess
import os
import tempfile

app = FastAPI()

@app.post("/process-podcast/")
async def process_podcast(stacchetto: UploadFile = File(...), background_music: UploadFile = File(...), files: list[UploadFile] = File(...)):
    # Percorsi temporanei per i file caricati
    input_files = []
    
    # Crea un file temporaneo per il podcast finale
    with tempfile.NamedTemporaryFile(delete=False) as temp_podcast:
        temp_podcast_path = temp_podcast.name

    # Salviamo i file audio (intervistatore, intervistato, ecc.)
    for idx, file in enumerate(files):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            file_path = temp_file.name
            with open(file_path, "wb") as f:
                f.write(await file.read())
            input_files.append(file_path)

    # Salviamo lo stacchetto iniziale
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as stacchetto_temp:
        stacchetto_path = stacchetto_temp.name
        with open(stacchetto_path, "wb") as f:
            f.write(await stacchetto.read())
    
    # Salviamo la musica di sottofondo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as background_temp:
        background_music_path = background_temp.name
        with open(background_music_path, "wb") as f:
            f.write(await background_music.read())

    # Combinare la musica di sottofondo e lo stacchetto all'inizio
    podcast_with_music = temp_podcast_path
    try:
        subprocess.run(f"ffmpeg -i {stacchetto_path} -i {background_music_path} -filter_complex \"[0] [1] amerge=inputs=2[a]\" -map [a] {podcast_with_music}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": "Errore durante la combinazione dello stacchetto con la musica", "details": str(e)}

    # Unire il resto dei file audio con la musica di sottofondo
    podcast_final = tempfile.mktemp(suffix=".mp3")
    file_paths_str = " ".join(input_files)  # Percorsi dei file audio

    try:
        subprocess.run(f"ffmpeg -i {podcast_with_music} -i {file_paths_str} -filter_complex \"[0][1]concat=n={len(input_files)+1}:v=0:a=1[a]\" -map [a] {podcast_final}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": "Errore durante la combinazione delle voci", "details": str(e)}

    # Risultato
    return {"message": "Podcast creato con successo!", "file": podcast_final}

