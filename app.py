from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import subprocess
from pathlib import Path
import os

app = Flask(__name__)

# Ruta para guardar descargas
DOWNLOAD_FOLDER = Path("downloads")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Nombre de ffmpeg (debe estar instalado en tu sistema)
FFMPEG_BINARY = "ffmpeg"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("url")

        if not video_url:
            return "No se proporcionó un enlace", 400

        try:
            # Configuración de yt-dlp para descargar solo el audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(DOWNLOAD_FOLDER / "%(title)s.%(ext)s"),
                'noplaylist': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_path = Path(ydl.prepare_filename(info))

            # Convertir a MP3
            mp3_filename = downloaded_path.with_suffix(".mp3")
            cmd = [
                FFMPEG_BINARY, "-i", str(downloaded_path),
                "-vn", "-ab", "320k", "-ar", "44100", "-y",
                str(mp3_filename)
            ]
            subprocess.run(cmd, check=True)

            # Borrar archivo original (opcional)
            if downloaded_path.exists():
                downloaded_path.unlink()

            # Enviar archivo al navegador para descarga
            return send_from_directory(
                directory=str(mp3_filename.parent),
                path=mp3_filename.name,
                as_attachment=True
            )

        except Exception as e:
            return f"Ocurrió un error: {str(e)}", 500

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
