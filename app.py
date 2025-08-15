from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import subprocess
import uuid

app = Flask(__name__)

# Ruta del ejecutable ffmpeg (Render ya lo instalará con el build script)
FFMPEG_BINARY = "ffmpeg"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    output_id = str(uuid.uuid4())
    video_path = f"{output_id}.mp4"
    audio_path = f"{output_id}.mp3"

    try:
        # Descargar el video de YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': video_path
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Convertir a MP3 usando ffmpeg
        subprocess.run([FFMPEG_BINARY, "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True)

        # Borrar el video original
        if os.path.exists(video_path):
            os.remove(video_path)

        # Enviar el MP3 al navegador
        return send_file(audio_path, as_attachment=True)

    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

    finally:
        # Limpiar archivos residuales
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

