from flask import Flask, request, jsonify, send_from_directory
import os
from image_processing import process_image
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Pastas de upload e saída
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/models'

# Garante que as pastas existam
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'app.html')

# Rota principal para upload da imagem PNG
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400

    if not file.filename.lower().endswith('.png'):
        return jsonify({'error': 'Apenas arquivos PNG são permitidos'}), 400

    # Salva a imagem enviada
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Define nome do arquivo de saída .glb
    output_filename = "output.glb"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        # Chama a função de processamento (gera o GLB)
        process_image(input_path, output_path)
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return jsonify({'error': f'Erro ao processar a imagem: {str(e)}'}), 500

    # Retorna a URL relativa do .glb para o front carregar
    return jsonify({'model_url': f'/static/models/{output_filename}'})

# Permite acessar arquivos estáticos da pasta /static (já é o padrão, mas só para reforçar)
@app.route('/static/models/<filename>')
def serve_glb(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
