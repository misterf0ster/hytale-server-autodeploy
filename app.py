from flask import Flask, render_template, Response, jsonify
import subprocess
import os

app = Flask(__name__)

# Путь к твоему основному скрипту
INSTALLER_SCRIPT = "gpc-installer.py"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream_install')
def stream_install():
    def generate():
        # Запускаем твой скрипт и перехватываем вывод (stdout и stderr)
        process = subprocess.Popen(
            ['python3', INSTALLER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Читаем вывод построчно и отправляем в браузер
        for line in iter(process.stdout.readline, ''):
            if line:
                # Специальный формат SSE (Server-Sent Events)
                yield f"data: {line}\n\n"
        
        process.stdout.close()
        process.wait()
        yield "data: --- УСТАНОВКА ЗАВЕРШЕНА ---\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("[INFO] Opening port for Web Panel in GCP...")
    subprocess.run("gcloud compute firewall-rules create hytale-web-panel --allow=tcp:5000 --source-ranges=0.0.0.0/0 --quiet", shell=True)
    app.run(host='0.0.0.0', port=5000, debug=True)