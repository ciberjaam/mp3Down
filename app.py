from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import subprocess
import uuid

app = Flask(__name__)

FFMPEG_BINARY = "ffmpeg"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        # Si alguien entra directamente a /download, lo enviamos al índice
        return render_template('index.html')

    # POST: procesar la descarga
    url = request.form['url']
    output_id = str(uuid.uuid4())
    video_path = f"{output_id}.mp4"
    audio_path = f"{output_id}.mp3"

    try:
        # Descargar video
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': video_path
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Convertir a MP3
        subprocess.run([FFMPEG_BINARY, "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True)

        # Borrar video original
        if os.path.exists(video_path):
            os.remove(video_path)

        # Enviar MP3 al navegador
        return send_file(audio_path, as_attachment=True)

    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

