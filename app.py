from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import subprocess
import uuid

app = Flask(__name__)

FFMPEG_BINARY = "ffmpeg"

@app.route('/')
def index():
    return render_template('index.html', mensaje=None)

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        return render_template('index.html', mensaje=None)

    url = request.form['url']
    output_id = str(uuid.uuid4())
    video_path = f"{output_id}.mp4"
    audio_path = f"{output_id}.mp3"

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': video_path,
            'noplaylist': True,
            'geo_bypass': True  # Ignora restricciones de país
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        subprocess.run([FFMPEG_BINARY, "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True)

        if os.path.exists(video_path):
            os.remove(video_path)

        return send_file(audio_path, as_attachment=True)

    except yt_dlp.utils.DownloadError:
        return render_template("index.html", mensaje="Video no disponible o restringido. Intenta con otro enlace.")

    except Exception as e:
        return render_template("index.html", mensaje=f"Ocurrió un error inesperado: {str(e)}")

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


