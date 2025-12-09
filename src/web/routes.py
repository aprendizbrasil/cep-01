from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import sys
import random
import tempfile
import shutil

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from api.getCepInfoV2 import get_cep_info
from terminal.addLatLong import process_csv

app = Flask(__name__, static_folder='static', template_folder='templates')
# Caminho absoluto para a pasta de uploads (relativo ao diretório raiz do projeto)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'sources')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Garante que a pasta de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Página inicial com menu."""
    return render_template('index.html')

@app.route('/consulta-cep-v2', methods=['GET', 'POST'])
def consulta_cep_v2():
    """Página de consulta de CEP individual."""
    result = None
    error = None
    if request.method == 'POST':
        cep = request.form.get('cep', '').strip()
        if not cep:
            error = 'Por favor, informe um CEP.'
        else:
            try:
                result = get_cep_info(cep)
            except Exception as e:
                error = str(e)
    return render_template('consultaCepV2.html', result=result, error=error)

@app.route('/add-lat-long', methods=['GET', 'POST'])
def add_lat_long():
    """Página para processar CSV em massa."""
    if request.method == 'GET':
        return render_template('addLatLong.html')
    
    # POST: processar upload
    if 'csv_file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Apenas arquivos CSV são permitidos.'}), 400
    
    # Gera um nome único para o arquivo original
    random_suffix = str(random.randint(10000000, 99999999))
    original_filename = file.filename.rsplit('.', 1)[0]
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename}_{random_suffix}.csv')
    file.save(original_path)
    
    # Processa o CSV
    output_filename = f'{original_filename}_{random_suffix}_com_coordenadas.csv'
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    success = process_csv(original_path, output_path)
    
    # Remove o arquivo original após processamento (opcional)
    try:
        os.remove(original_path)
    except:
        pass
    
    if not success:
        return jsonify({'error': 'Falha ao processar o arquivo.'}), 500
    
    # Retorna informações para download
    return jsonify({
        'success': True,
        'download_filename': output_filename,
        'original_filename': file.filename
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Endpoint para download do arquivo processado."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return 'Arquivo não encontrado.', 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
