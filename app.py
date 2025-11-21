"""
Flask web application for WhatsApp Journey Generator.
"""
import os
import json
import zipfile
import io
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from journey_generator import generate_journeys

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Load available models
MODELS_FILE = Path(__file__).parent / "models.json"
with open(MODELS_FILE, 'r') as f:
    AVAILABLE_MODELS = json.load(f)


@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')


@app.route('/api/models', methods=['GET'])
def get_models():
    """Return list of available models."""
    return jsonify(AVAILABLE_MODELS)


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate journeys from uploaded prompt file."""
    try:
        # Validate form data first (before API key check)
        if 'prompt_file' not in request.files:
            return jsonify({"error": "No prompt file uploaded"}), 400

        file = request.files['prompt_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate file extension
        if not file.filename.endswith('.md'):
            return jsonify({"error": "File must be a .md file"}), 400

        scenario = request.form.get('scenario', '').strip()
        if not scenario:
            return jsonify({"error": "Scenario is required"}), 400

        models = request.form.getlist('models[]')
        if not models:
            return jsonify({"error": "At least one model must be selected"}), 400

        if len(models) > 3:
            return jsonify({"error": "Maximum 3 models allowed"}), 400

        # Validate model IDs
        valid_model_ids = {m['id'] for m in AVAILABLE_MODELS}
        invalid_models = [m for m in models if m not in valid_model_ids]
        if invalid_models:
            return jsonify({"error": f"Invalid model IDs: {', '.join(invalid_models)}"}), 400

        # Validate API key (after form validation)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500

        # Read file content
        prompt_content = file.read().decode('utf-8')

        # Generate journeys
        results = generate_journeys(prompt_content, scenario, models, api_key)

        # Create zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for scenario_slug, models_dict in results.items():
                for model_slug, files_dict in models_dict.items():
                    for filename, content in files_dict.items():
                        # Create path: outputs/scenario_slug/model_slug/filename
                        zip_path = f"outputs/{scenario_slug}/{model_slug}/{filename}"
                        zip_file.writestr(zip_path, content)

        zip_buffer.seek(0)

        # Generate download filename
        scenario_slug = list(results.keys())[0]
        zip_filename = f"journeys_{scenario_slug}.zip"

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

