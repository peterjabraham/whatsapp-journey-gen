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
from prompt_builder import generate_prompt_markdown

# Monkey patch for gevent compatibility (if using gevent workers)
try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    pass  # gevent not installed, skip monkey patching

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Load available models
MODELS_FILE = Path(__file__).parent / "models.json"
try:
    with open(MODELS_FILE, 'r') as f:
        AVAILABLE_MODELS = json.load(f)
except FileNotFoundError:
    print(f"Warning: {MODELS_FILE} not found. Using empty models list.")
    AVAILABLE_MODELS = []
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {MODELS_FILE}: {e}")
    AVAILABLE_MODELS = []


@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')


@app.route('/prompt-builder')
def prompt_builder():
    """Serve the prompt builder form page."""
    return render_template('prompt_builder.html')


@app.route('/api/generate-prompt', methods=['POST'])
def generate_prompt():
    """Generate prompt.md file from form data."""
    try:
        form_data = request.form.to_dict()
        
        # Handle multi-value fields (lists)
        if 'unique_selling_points' in request.form:
            form_data['unique_selling_points'] = request.form.getlist('unique_selling_points[]')
        if 'url_product_pages' in request.form:
            form_data['url_product_pages'] = request.form.getlist('url_product_pages[]')
        if 'url_offer_pages' in request.form:
            form_data['url_offer_pages'] = request.form.getlist('url_offer_pages[]')
        if 'url_testimonials' in request.form:
            form_data['url_testimonials'] = request.form.getlist('url_testimonials[]')
        if 'products' in request.form:
            form_data['products'] = request.form.getlist('products[]')
        if 'brand_attributes' in request.form:
            form_data['brand_attributes'] = request.form.getlist('brand_attributes[]')
        
        # Generate prompt markdown
        prompt_content = generate_prompt_markdown(form_data)
        
        # Return as downloadable file
        return send_file(
            io.BytesIO(prompt_content.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name='PROMPT_4_WhatsApp_Journey_Generator.md'
        )
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate prompt: {str(e)}"}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    """Return list of available models."""
    try:
        return jsonify(AVAILABLE_MODELS)
    except Exception as e:
        return jsonify({"error": f"Failed to load models: {str(e)}"}), 500


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

