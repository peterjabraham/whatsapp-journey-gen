"""
Flask web application for WhatsApp Journey Generator.

NOTE: When running with gunicorn + gevent workers, the wsgi.py file handles
gevent monkey patching BEFORE imports. This app.py does NOT do monkey patching
to avoid RecursionError issues during development.
"""
import sys
# Increase recursion limit for complex HTML parsing
sys.setrecursionlimit(10000)

import os
import json
import zipfile
import io
import re
import time
import queue
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
from dotenv import load_dotenv
from journey_generator import generate_journeys
from prompt_builder import generate_prompt_markdown

# Load environment variables
load_dotenv()

# Import orchestrator (optional - may not be installed yet)
try:
    from agents import Orchestrator, OrchestrationResult
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

# NOTE: Gevent monkey patching removed from here - it was causing RecursionError
# when importing after ssl. For production, use wsgi.py which patches first.

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


@app.route('/health')
def health():
    """Health check endpoint for Railway."""
    return jsonify({"status": "ok", "service": "whatsapp-journey-generator"}), 200


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
        
        # Handle all multi-value fields (arrays)
        multi_value_fields = [
            'tone_of_voice[]',
            'requirements[]',
            'supporting_urls[]',
            'file_references[]',
            'brand_phrases[]',
            'deliverables[]',
            'format_prefs[]',
        ]
        
        for field in multi_value_fields:
            if field in request.form:
                # Remove the [] suffix for the dict key
                clean_key = field.rstrip('[]')
                form_data[clean_key] = request.form.getlist(field)
        
        # Legacy support for old form field names
        legacy_fields = [
            ('unique_selling_points[]', 'unique_selling_points'),
            ('url_product_pages[]', 'url_product_pages'),
            ('url_offer_pages[]', 'url_offer_pages'),
            ('url_testimonials[]', 'url_testimonials'),
            ('products[]', 'products'),
            ('brand_attributes[]', 'brand_attributes'),
        ]
        
        for form_key, dict_key in legacy_fields:
            if form_key in request.form:
                form_data[dict_key] = request.form.getlist(form_key)
        
        # Generate prompt markdown
        prompt_content = generate_prompt_markdown(form_data)
        
        # Generate filename based on campaign/product name
        campaign_name = form_data.get('campaign_name', '').strip()
        product_name = form_data.get('product_name', '').strip()
        
        if campaign_name:
            filename = f"PROMPT_{sanitize_filename(campaign_name)}.md"
        elif product_name:
            filename = f"PROMPT_{sanitize_filename(product_name)}.md"
        else:
            filename = 'PROMPT_4_WhatsApp_Journey_Generator.md'
        
        # Return as downloadable file
        return send_file(
            io.BytesIO(prompt_content.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate prompt: {str(e)}"}), 500


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use in a filename."""
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove or replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Limit length
    return name[:50]


@app.route('/api/extract-colors', methods=['POST'])
def extract_colors():
    """
    Extract colors from a URL by fetching the page and parsing CSS.
    This is a simple implementation that looks for common color patterns.
    """
    try:
        import requests as http_requests
        
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Fetch the page
        try:
            response = http_requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ColorExtractor/1.0)'
            })
            response.raise_for_status()
            html_content = response.text
        except http_requests.RequestException as e:
            return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 400
        
        # Extract colors using regex patterns
        colors = set()
        
        # Pattern for hex colors (#RGB, #RRGGBB)
        hex_pattern = r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![0-9A-Fa-f])'
        hex_matches = re.findall(hex_pattern, html_content)
        for match in hex_matches:
            color = f"#{match.upper()}"
            # Expand 3-digit hex to 6-digit
            if len(match) == 3:
                color = f"#{match[0]*2}{match[1]*2}{match[2]*2}".upper()
            colors.add(color)
        
        # Pattern for rgb/rgba colors
        rgb_pattern = r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
        rgba_pattern = r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)'
        
        for pattern in [rgb_pattern, rgba_pattern]:
            matches = re.findall(pattern, html_content)
            for match in matches:
                r, g, b = int(match[0]), int(match[1]), int(match[2])
                if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                    color = f"#{r:02X}{g:02X}{b:02X}"
                    colors.add(color)
        
        # Filter out common/boring colors (white, black, very light grays)
        filtered_colors = []
        for color in colors:
            # Skip very common colors
            if color.upper() in ['#FFFFFF', '#000000', '#FFF', '#000']:
                continue
            # Skip very light colors (likely backgrounds)
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                # Skip if all channels are very close to white or very close to black
                if (r > 240 and g > 240 and b > 240) or (r < 15 and g < 15 and b < 15):
                    continue
                # Skip grays (all channels nearly equal)
                if abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10:
                    if r > 200 or r < 50:
                        continue
                filtered_colors.append(color)
            except (ValueError, IndexError):
                continue
        
        # Sort by frequency (approximate by counting occurrences in original HTML)
        color_counts = []
        for color in filtered_colors:
            # Count how many times this color appears
            count = html_content.lower().count(color.lower())
            # Also count the short form if applicable
            if len(color) == 7:
                short = f"#{color[1]}{color[3]}{color[5]}"
                count += html_content.lower().count(short.lower())
            color_counts.append((color, count))
        
        # Sort by count (descending) and take top 6
        color_counts.sort(key=lambda x: x[1], reverse=True)
        top_colors = [c[0] for c in color_counts[:6]]
        
        return jsonify({"colors": top_colors})
        
    except Exception as e:
        return jsonify({"error": f"Failed to extract colors: {str(e)}"}), 500


# ============================================================================
# ORCHESTRATOR ROUTES (New multi-agent pipeline)
# ============================================================================

@app.route('/orchestrate')
def orchestrate_page():
    """Serve the new orchestrator input page."""
    return render_template('orchestrate.html')


@app.route('/review')
def review_page():
    """Serve the brief review/edit page."""
    return render_template('review.html')


@app.route('/api/orchestrate', methods=['POST'])
def run_orchestration():
    """
    Run the orchestration pipeline to extract and analyze content.
    
    Accepts:
    - urls[]: List of URLs to scrape
    - pdfs: PDF file uploads
    - journey_type: "B2B" or "B2C"
    - user_inputs: JSON string with user preferences
    """
    if not ORCHESTRATOR_AVAILABLE:
        return jsonify({
            "error": "Orchestrator not available. Install dependencies: pip install pymupdf pymupdf4llm anthropic"
        }), 500
    
    try:
        # Get URLs
        urls = request.form.getlist('urls[]')
        urls = [u.strip() for u in urls if u.strip()]
        
        # Get PDF files
        pdf_files = []
        if 'pdfs' in request.files:
            for pdf in request.files.getlist('pdfs'):
                if pdf.filename and pdf.filename.endswith('.pdf'):
                    pdf_files.append((pdf.filename, pdf.read()))
        
        # Validate we have at least one source
        if not urls and not pdf_files:
            return jsonify({"error": "Please provide at least one URL or PDF"}), 400
        
        # Get journey type
        journey_type = request.form.get('journey_type', 'B2C')
        if journey_type not in ['B2B', 'B2C']:
            journey_type = 'B2C'
        
        # Get user inputs (optional overrides)
        user_inputs = {}
        user_inputs_json = request.form.get('user_inputs', '{}')
        try:
            user_inputs = json.loads(user_inputs_json)
        except json.JSONDecodeError:
            pass
        
        # Add any direct form fields to user_inputs
        if request.form.get('company_name'):
            user_inputs['company_name'] = request.form.get('company_name')
        if request.form.get('offer_headline'):
            user_inputs.setdefault('offer', {})['headline'] = request.form.get('offer_headline')
        if request.form.get('discount_code'):
            user_inputs.setdefault('offer', {})['discount_code'] = request.form.get('discount_code')
        if request.form.get('timing_strategy'):
            user_inputs.setdefault('timing', {})['strategy'] = request.form.get('timing_strategy')
        
        # Run orchestration
        orchestrator = Orchestrator()
        
        # Check if LLM enhancement is requested
        use_llm = request.form.get('use_llm', 'false').lower() == 'true'
        
        if use_llm:
            result = orchestrator.run_with_llm_reasoning(
                urls=urls,
                pdf_files=pdf_files,
                journey_type=journey_type,
                user_inputs=user_inputs
            )
        else:
            result = orchestrator.run(
                urls=urls,
                pdf_files=pdf_files,
                journey_type=journey_type,
                user_inputs=user_inputs
            )
        
        return jsonify(result.to_dict())
        
    except Exception as e:
        return jsonify({"error": f"Orchestration failed: {str(e)}"}), 500


# Store for SSE progress (simple in-memory, keyed by session)
_progress_queues = {}


@app.route('/api/orchestrate/stream', methods=['POST'])
def run_orchestration_stream():
    """
    Run orchestration with Server-Sent Events (SSE) for real-time progress.
    
    Returns a stream of events:
    - progress: {step, message, percent}
    - complete: {result}
    - error: {message}
    """
    if not ORCHESTRATOR_AVAILABLE:
        return jsonify({
            "error": "Orchestrator not available"
        }), 500
    
    # Parse form data
    urls = request.form.getlist('urls[]')
    urls = [u.strip() for u in urls if u.strip()]
    
    pdf_files = []
    if 'pdfs' in request.files:
        for pdf in request.files.getlist('pdfs'):
            if pdf.filename and pdf.filename.endswith('.pdf'):
                pdf_files.append((pdf.filename, pdf.read()))
    
    if not urls and not pdf_files:
        return jsonify({"error": "Please provide at least one URL or PDF"}), 400
    
    journey_type = request.form.get('journey_type', 'B2C')
    if journey_type not in ['B2B', 'B2C']:
        journey_type = 'B2C'
    
    user_inputs = {}
    user_inputs_json = request.form.get('user_inputs', '{}')
    try:
        user_inputs = json.loads(user_inputs_json)
    except json.JSONDecodeError:
        pass
    
    if request.form.get('company_name'):
        user_inputs['company_name'] = request.form.get('company_name')
    if request.form.get('offer_headline'):
        user_inputs.setdefault('offer', {})['headline'] = request.form.get('offer_headline')
    if request.form.get('discount_code'):
        user_inputs.setdefault('offer', {})['discount_code'] = request.form.get('discount_code')
    if request.form.get('timing_strategy'):
        user_inputs.setdefault('timing', {})['strategy'] = request.form.get('timing_strategy')
    
    use_llm = request.form.get('use_llm', 'false').lower() == 'true'
    
    # Create a queue for progress updates
    progress_queue = queue.Queue()
    
    # Progress steps with percentages
    PROGRESS_STEPS = {
        'extract': 20,
        'brand': 40,
        'audience': 60,
        'offer': 80,
        'merge': 95,
        'complete': 100,
    }
    
    def progress_callback(step: str, message: str):
        """Callback that the orchestrator calls for each step."""
        percent = PROGRESS_STEPS.get(step, 50)
        progress_queue.put({
            'type': 'progress',
            'step': step,
            'message': message,
            'percent': percent
        })
    
    def run_orchestrator():
        """Run orchestrator in a thread."""
        try:
            orchestrator = Orchestrator()
            orchestrator.on_progress = progress_callback
            
            if use_llm:
                result = orchestrator.run_with_llm_reasoning(
                    urls=urls,
                    pdf_files=pdf_files,
                    journey_type=journey_type,
                    user_inputs=user_inputs
                )
            else:
                result = orchestrator.run(
                    urls=urls,
                    pdf_files=pdf_files,
                    journey_type=journey_type,
                    user_inputs=user_inputs
                )
            
            progress_queue.put({
                'type': 'complete',
                'result': result.to_dict()
            })
        except Exception as e:
            progress_queue.put({
                'type': 'error',
                'message': str(e)
            })
    
    # Start orchestrator in background thread
    thread = threading.Thread(target=run_orchestrator)
    thread.start()
    
    def generate_events():
        """Generator for SSE events."""
        while True:
            try:
                # Wait for progress update (timeout to keep connection alive)
                event = progress_queue.get(timeout=30)
                
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"
                
                # If complete or error, stop
                if event['type'] in ['complete', 'error']:
                    break
                    
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    
    return Response(
        stream_with_context(generate_events()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
        }
    )


@app.route('/api/save-brief', methods=['POST'])
def save_brief():
    """
    Save the edited brief and prepare for journey generation.
    
    Accepts:
    - brief: The edited markdown content
    - filename: Optional filename
    """
    try:
        data = request.get_json()
        if not data or 'brief' not in data:
            return jsonify({"error": "Brief content is required"}), 400
        
        brief_content = data['brief']
        filename = data.get('filename', 'journey_brief.md')
        
        # Sanitize filename
        filename = sanitize_filename(filename)
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Return as downloadable file
        return send_file(
            io.BytesIO(brief_content.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": f"Failed to save brief: {str(e)}"}), 500


@app.route('/api/brief-to-prompt', methods=['POST'])
def brief_to_prompt():
    """
    Convert an orchestrated brief to a journey generator prompt.
    
    Takes the combined brief markdown and formats it for the
    existing journey generator pipeline.
    """
    try:
        data = request.get_json()
        if not data or 'brief' not in data:
            return jsonify({"error": "Brief content is required"}), 400
        
        brief_content = data['brief']
        
        # The brief is already in the format needed for journey generation
        # Just wrap it with the journey generator header
        prompt_content = f"""# PROMPT: WhatsApp Journey Generator

{brief_content}

---

## OUTPUT FORMAT

Output your response in this exact order with these exact delimiters:

```text
=== CONFIG YAML ===
(normalized CONFIG object in YAML format)

=== JOURNEY MARKDOWN ===
(complete journey specification in markdown)

=== HTML A – SUMMARY WORKFLOW ===
```file:summary_workflow.html
(complete HTML document)
```

=== HTML B – FULL DETAIL WORKFLOW ===
```file:full_detail_workflow.html
(complete HTML document)
```
```

Ensure all messages respect platform limits and brand voice.
"""
        
        filename = data.get('filename', 'PROMPT_orchestrated.md')
        filename = sanitize_filename(filename)
        if not filename.endswith('.md'):
            filename += '.md'
        
        return send_file(
            io.BytesIO(prompt_content.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": f"Failed to convert brief: {str(e)}"}), 500


# ============================================================================
# EXISTING ROUTES
# ============================================================================

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
