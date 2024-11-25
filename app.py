from flask import Flask, request, jsonify, render_template, json
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
from config import Config
from analyzer import EnhancedCSVAnalyzer, CustomJSONEncoder

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.json_encoder = CustomJSONEncoder  # Set the custom encoder for the entire app

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

analyzer = EnhancedCSVAnalyzer(app.config['GEMINI_API_KEY'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_csv():
    print(f"Received request at /api/analyze")
    print(f"Request method: {request.method}")
    print(f"Request files: {request.files}")
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = None
    filepath = None
    
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze the file
            try:
                analysis_results = analyzer.analyze_csv(filepath)
                return jsonify(analysis_results)  # Remove cls parameter, using app.json_encoder instead
            except ValueError as ve:
                return jsonify({'error': str(ve)}), 400
            except Exception as e:
                logger.error(f"Analysis error: {str(e)}")
                return jsonify({'error': 'Error analyzing file: ' + str(e)}), 500
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        error_msg = str(e)
        if "Unsupported file format" in error_msg:
            return jsonify({'error': 'Please upload either CSV or Excel files (.csv, .xlsx, .xls)'}), 400
        return jsonify({'error': error_msg}), 500
        
    finally:
        # Clean up uploaded file
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logger.error(f"Error cleaning up file: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5040, debug=False)