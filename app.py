from flask import Flask, render_template, Response, jsonify, request
import subprocess
import os

app = Flask(__name__)

INSTALLER_SCRIPT = "gpc-installer.py"

def extract_oauth_url(text):
    """Твоя логика извлечения ссылки из текста"""
    for line in text.split('\n'):
        if "or visit:" in line.lower() and "user_code=" in line:
            start = line.find("https://")
            if start != -1:
                url = line[start:].strip()
                for char in [' ', '\r', '\n', '\t']:
                    if char in url: url = url[:url.index(char)]
                return url
    
    for line in text.split('\n'):
        if "https://" in line and "oauth.accounts.hytale.com" in line and "user_code=" in line:
            start = line.find("https://")
            if start != -1:
                url = line[start:].strip()
                for char in [' ', '\r', '\n', '\t']:
                    if char in url: url = url[:url.index(char)]
                if "user_code=" in url: return url
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream_install')
def stream_install():
    def generate():
        # Запуск с флагом -u для моментального вывода
        process = subprocess.Popen(['python3', '-u', INSTALLER_SCRIPT], 
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                # Пытаемся найти ссылку в текущей строке лога
                found_url = extract_oauth_url(line)
                if found_url:
                    yield f"data: BUTTON_LINK|{found_url}\n\n"
                
                yield f"data: {line}\n\n"
        
        process.wait()
        yield "data: --- ПРОЦЕСС ЗАВЕРШЕН ---\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('command')
    # Здесь будет отправка в screen игрового сервера
    print(f"DEBUG: Отправка команды в консоль: {cmd}")
    return jsonify(success=True)

if __name__ == '__main__':
    # Оставляем попытку открыть порт, но игнорируем ошибки прав
    subprocess.run("gcloud compute firewall-rules create hytale-web-panel --allow=tcp:5000 --source-ranges=0.0.0.0/0 --quiet", shell=True)
    app.run(host='0.0.0.0', port=5000, debug=False) # debug=False для стабильных логов