"""
Tests for the WhatsApp Journey Generator web application.
"""
import os
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
import zipfile
from flask import Flask
from app import app
from app import AVAILABLE_MODELS
from journey_generator import (
    extract_prompt_body,
    slugify_model,
    slugify_scenario,
    parse_files_from_content,
    generate_journeys
)


class TestJourneyGenerator(unittest.TestCase):
    """Tests for core journey generator functions."""

    def test_extract_prompt_body_with_fenced_block(self):
        """Test extracting prompt from fenced code block."""
        content = """# Some markdown
```python
This is the actual prompt content
With multiple lines
```
More markdown after"""
        result = extract_prompt_body(content)
        self.assertEqual(result, "python\nThis is the actual prompt content\nWith multiple lines")

    def test_extract_prompt_body_without_fenced_block(self):
        """Test extracting prompt when no fenced block exists."""
        content = "This is the prompt content directly"
        result = extract_prompt_body(content)
        self.assertEqual(result, "This is the prompt content directly")

    def test_slugify_model(self):
        """Test model ID slugification."""
        self.assertEqual(slugify_model("openai/gpt-4.1-mini"), "openai_gpt_4_1_mini")
        self.assertEqual(slugify_model("anthropic/claude-3.5-sonnet"), "anthropic_claude_3_5_sonnet")
        self.assertEqual(slugify_model("meta-llama/llama-3.1-70b-instruct"), "meta_llama_llama_3_1_70b_instruct")

    def test_slugify_scenario(self):
        """Test scenario slugification."""
        self.assertEqual(slugify_scenario("Lifetime ISA for UK Police"), "lifetime_isa_for_uk_police")
        self.assertEqual(slugify_scenario("Test Scenario 123!"), "test_scenario_123")
        self.assertEqual(slugify_scenario(""), "scenario")

    def test_parse_files_from_content(self):
        """Test parsing file blocks from model response."""
        content = """```file:journey.md
# Journey content
Here is the journey
```

```file:summary_workflow.html
<!DOCTYPE html>
<html>Content</html>
```

```file:full_detail_workflow.html
<!DOCTYPE html>
<html>Overview</html>
```"""
        result = parse_files_from_content(content)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], "journey.md")
        self.assertEqual(result[1][0], "summary_workflow.html")
        self.assertEqual(result[2][0], "full_detail_workflow.html")
        self.assertIn("Journey content", result[0][1])
        self.assertIn("Content", result[1][1])

    def test_parse_files_from_content_no_files(self):
        """Test parsing when no file blocks exist."""
        content = "Just regular text without file blocks"
        with self.assertRaises(ValueError) as context:
            parse_files_from_content(content)
        self.assertIn("No ```file:...``` blocks found", str(context.exception))

    @patch('journey_generator.call_model')
    def test_generate_journeys(self, mock_call_model):
        """Test full journey generation."""
        # Mock API response
        mock_response = """```file:journey.md
# Journey
Content here
```

```file:summary_workflow.html
<html>Detailed</html>
```

```file:full_detail_workflow.html
<html>Overview</html>
```"""
        mock_call_model.return_value = mock_response

        prompt = "Test prompt content"
        scenario = "Test Scenario"
        models = ["openai/gpt-4.1-mini"]
        api_key = "test-key"

        result = generate_journeys(prompt, scenario, models, api_key)

        self.assertIn("test_scenario", result)
        self.assertIn("openai_gpt_4_1_mini", result["test_scenario"])
        self.assertIn("journey.md", result["test_scenario"]["openai_gpt_4_1_mini"])
        self.assertIn("summary_workflow.html", result["test_scenario"]["openai_gpt_4_1_mini"])
        self.assertIn("full_detail_workflow.html", result["test_scenario"]["openai_gpt_4_1_mini"])

        # Verify API was called correctly
        mock_call_model.assert_called_once()
        call_args = mock_call_model.call_args
        self.assertEqual(call_args[0][0], "openai/gpt-4.1-mini")
        self.assertEqual(call_args[0][2], scenario)
        self.assertEqual(call_args[0][3], api_key)


class TestFlaskApp(unittest.TestCase):
    """Tests for Flask application routes."""

    def setUp(self):
        """Set up test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test main page loads."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WhatsApp Journey Generator', response.data)

    def test_prompt_builder_route(self):
        """Test prompt builder page loads."""
        response = self.app.get('/prompt-builder')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Prompt Builder', response.data)

    def test_generate_prompt_route(self):
        """Test prompt generation endpoint."""
        data = {
            'platform': 'WATI',
            'format': 'B2C',
            'duration_overall': '3 days',
            'brand_name': 'Test Brand',
            'industry': 'Test Industry',
            'audience': 'Test Audience',
            'offer_text': 'Test Offer',
            'quote_code': 'TEST123',
            'num_journeys': '1',
            'deliverables': 'Journeys: 1. Deliverables: 1',
            'day0_duration': '0-3 hours',
            'day0_step1_timing': 'Immediate',
            'day0_step2_timing': '+30 minutes',
            'day0_step3_timing': '+2 hours',
            'day1_start': '+24 hours',
            'day2_start': '+24 hours',
            'day3_start': '+24 hours',
            'final_push_timing': '+3 hours',
            'urgency_level': 'medium',
            'sophistication_level': '7',
            'tone': 'professional',
            'emoji_usage': 'minimal'
        }
        response = self.app.post('/api/generate-prompt', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/markdown')
        self.assertIn(b'PROMPT: WhatsApp Journey Generator', response.data)
        self.assertIn(b'Test Brand', response.data)

    def test_get_models_route(self):
        """Test models API endpoint."""
        response = self.app.get('/api/models')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('provider', data[0])

    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'})
    @patch('app.generate_journeys')
    def test_generate_route_success(self, mock_generate):
        """Test successful journey generation."""
        # Mock generation result
        mock_generate.return_value = {
            "test_scenario": {
                "test_model": {
                    "journey.md": "# Journey content",
                    "summary_workflow.html": "<html>Summary</html>",
                    "full_detail_workflow.html": "<html>Full Detail</html>"
                }
            }
        }

        # Create test file - need to reset BytesIO position
        file_content = BytesIO(b'# Test prompt\n```\nPrompt content\n```')
        file_content.seek(0)
        
        # Use a model ID that exists in models.json
        valid_model = AVAILABLE_MODELS[0]['id'] if AVAILABLE_MODELS else 'openai/gpt-4.1-mini'
        
        data = {
            'prompt_file': (file_content, 'test.md'),
            'scenario': 'Test Scenario',
            'models[]': [valid_model]
        }

        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/zip')

        # Verify zip file can be read
        zip_data = BytesIO(response.data)
        with zipfile.ZipFile(zip_data, 'r') as zip_file:
            files = zip_file.namelist()
            self.assertIn('outputs/test_scenario/test_model/journey.md', files)
            self.assertIn('outputs/test_scenario/test_model/summary_workflow.html', files)
            self.assertIn('outputs/test_scenario/test_model/full_detail_workflow.html', files)

    def test_generate_route_no_file(self):
        """Test generation without file."""
        data = {
            'scenario': 'Test Scenario',
            'models[]': ['openai/gpt-4.1-mini']
        }
        response = self.app.post('/api/generate', data=data)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_route_no_scenario(self):
        """Test generation without scenario."""
        data = {
            'prompt_file': (BytesIO(b'Test content'), 'test.md'),
            'models[]': ['openai/gpt-4.1-mini']
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_route_no_models(self):
        """Test generation without models."""
        data = {
            'prompt_file': (BytesIO(b'Test content'), 'test.md'),
            'scenario': 'Test Scenario'
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_route_too_many_models(self):
        """Test generation with more than 3 models."""
        data = {
            'prompt_file': (BytesIO(b'Test content'), 'test.md'),
            'scenario': 'Test Scenario',
            'models[]': ['model1', 'model2', 'model3', 'model4']
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_route_invalid_file_type(self):
        """Test generation with non-md file."""
        data = {
            'prompt_file': (BytesIO(b'Test content'), 'test.txt'),
            'scenario': 'Test Scenario',
            'models[]': ['openai/gpt-4.1-mini']
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_generate_route_invalid_model(self):
        """Test generation with invalid model ID."""
        data = {
            'prompt_file': (BytesIO(b'Test content'), 'test.md'),
            'scenario': 'Test Scenario',
            'models[]': ['invalid-model-id']
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_route_no_api_key(self):
        """Test generation without API key configured."""
        file_content = BytesIO(b'Test content')
        file_content.seek(0)
        # Use a valid model ID
        valid_model = AVAILABLE_MODELS[0]['id'] if AVAILABLE_MODELS else 'x-ai/grok-4.1-fast'
        data = {
            'prompt_file': (file_content, 'test.md'),
            'scenario': 'Test Scenario',
            'models[]': [valid_model]
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'})
    @patch('app.generate_journeys')
    def test_generate_route_api_error(self, mock_generate):
        """Test handling of API errors."""
        mock_generate.side_effect = RuntimeError("API error occurred")

        file_content = BytesIO(b'Test content')
        file_content.seek(0)
        # Use a valid model ID
        valid_model = AVAILABLE_MODELS[0]['id'] if AVAILABLE_MODELS else 'x-ai/grok-4.1-fast'
        data = {
            'prompt_file': (file_content, 'test.md'),
            'scenario': 'Test Scenario',
            'models[]': [valid_model]
        }
        response = self.app.post('/api/generate', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()

