from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
from ws_client import test_file, invia_file, scarica_ricevuta, anonimizza_dati

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploaded_files')
RICEVUTE_FOLDER = os.path.join(BASE_DIR, 'ricevute')
SCHEDINE_FOLDER = os.path.join(BASE_DIR, 'schedine')
ALLOWED_EXTENSIONS = {'xml', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RICEVUTE_FOLDER'] = RICEVUTE_FOLDER
app.config['SCHEDINE_FOLDER'] = SCHEDINE_FOLDER
app.secret_key = 'supersegretosemplice'  # Per i messaggi flash

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RICEVUTE_FOLDER, exist_ok=True)
os.makedirs(SCHEDINE_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        print('file: ', file)
        print(f"Ricevuto file: {file.filename}")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"xxxxSaving to: {path}")
            file.save(path)
            flash('File caricato correttamente.', 'success')
        else:
            flash('Formato file non valido.', 'danger')
        return redirect('/')

    filesUploaded = os.listdir(app.config['UPLOAD_FOLDER'])
    filesSchedine = os.listdir(app.config['SCHEDINE_FOLDER'])
    filesRicevute = os.listdir(app.config['RICEVUTE_FOLDER'])
    return render_template('index.html', filesUploaded=filesUploaded, filesSchedine=filesSchedine, filesRicevute=filesRicevute)

@app.route('/test/<filename>')
def test(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    esito, messaggio = test_file(filepath)
    flash(f'Test: {messaggio}', 'info' if esito else 'danger')
    return redirect('/')

@app.route('/invia/<filename>')
def invia(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    success, messaggio = invia_file(filepath)
    flash(f'Invio: {messaggio}', 'success' if success else 'danger')
    return redirect('/')

@app.route('/ricevuta/<filename>')
def ricevuta(filename):
    #controllo che la data corrente sia maggiore a quella della schedina
    data = filename.replace('.txt', '')
    data = data.replace('quest-', '')
    #controllo che la data corrente sia maggiore a quella della schedina
    today = datetime.today()
    if data < today.strftime('%Y-%m-%d'):
        flash('Non è possibile scaricare la ricevuta per una data futura.', 'warning')
        return redirect('/')
    nome_ricevuta = filename.replace('.txt', '_ricevuta.pdf')
    ricevuta_path = os.path.join(app.config['RICEVUTE_FOLDER'], nome_ricevuta)
    scarica_ricevuta(app.config['SCHEDINE_FOLDER'], filename, ricevuta_path)
    return send_from_directory(app.config['RICEVUTE_FOLDER'], nome_ricevuta, as_attachment=True)

@app.route('/anonimizza/<filename>')
def anonimizza(filename):
    content = anonimizza_dati(app.config['SCHEDINE_FOLDER'], filename)
    return redirect('/')
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RICEVUTE_FOLDER, exist_ok=True)
    app.run(debug=True)
