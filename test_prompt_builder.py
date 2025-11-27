"""
Tests for the prompt builder functionality.
"""
import unittest
from prompt_builder import generate_prompt_markdown, build_config_from_form


class TestPromptBuilder(unittest.TestCase):
    """Tests for prompt builder functions."""

    def get_minimal_form_data(self):
        """Return minimal valid form data for testing."""
        return {
            'product_name': 'Test Product',
            'company_name': 'Test Company',
            'audience_description': 'Test audience description',
            'entry_point': 'Website form',
            'campaign_offer': 'Test offer',
            'feature_1': 'Feature One',
            'feature_2': 'Feature Two',
            'main_product_url': 'https://example.com/product',
            'application_url': 'https://example.com/apply',
            'assets_list': 'Hero image, Logo',
            'journey_duration': '2',
            'total_messages': '7',
            'include_personalization': 'yes',
            'step1_to_2_delay': '10 seconds',
            'step2_to_3_delay': '5 seconds',
            'step3_to_autoreplies': 'Immediate',
            'day1_start': '24 hours',
            'step5_to_6_delay': '2 hours',
            'step6_to_7_delay': '10 minutes',
            'tone_of_voice[]': ['Professional', 'Trustworthy'],
            'brand_positioning': 'We are the best',
            'primary_color': '#315891',
            'accent_color': '#D44437',
            'background_color': '#E9E9E9',
            'platform': 'WATI',
            'body_text_max': '200',
            'header_max': '60',
            'footer_max': '60',
            'interactive_button_max': '20',
            'quick_reply_button_max': '25',
            'target_open_rate': '70',
            'target_button_click': '40',
            'target_app_start': '40',
            'target_completion': '20',
            'optout_wording': 'Type STOP to opt-out',
            'include_disclaimers': 'yes',
            'include_terms': 'yes',
        }

    def test_build_config_from_form_basic(self):
        """Test building config from form data."""
        form_data = self.get_minimal_form_data()
        config = build_config_from_form(form_data)
        
        self.assertEqual(config['BRIEF']['product_name'], 'Test Product')
        self.assertEqual(config['BRIEF']['company_name'], 'Test Company')
        self.assertEqual(config['PLATFORM']['platform'], 'WATI')
        self.assertEqual(config['TARGETS']['open_rate'], '70')

    def test_build_config_from_form_with_features(self):
        """Test building config with features as JSON."""
        form_data = self.get_minimal_form_data()
        form_data['features'] = '["Feature A", "Feature B", "Feature C"]'
        
        config = build_config_from_form(form_data)
        
        self.assertEqual(len(config['BRIEF']['features']), 3)
        self.assertIn('Feature A', config['BRIEF']['features'])

    def test_build_config_from_form_with_tone_list(self):
        """Test building config with tone of voice list."""
        form_data = self.get_minimal_form_data()
        form_data['tone_of_voice[]'] = ['Professional', 'Trustworthy', 'Warm']
        
        config = build_config_from_form(form_data)
        
        self.assertEqual(len(config['BRAND']['tone_of_voice']), 3)
        self.assertIn('Professional', config['BRAND']['tone_of_voice'])

    def test_generate_prompt_markdown_basic(self):
        """Test basic prompt generation."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('PROMPT: WhatsApp Journey Generator', result)
        self.assertIn('Test Product', result)
        self.assertIn('Test Company', result)
        self.assertIn('WATI', result)

    def test_generate_prompt_markdown_includes_brief_section(self):
        """Test that generated prompt includes Brief section."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('1. BRIEF (Core Information)', result)
        self.assertIn('Product & Company Details', result)
        self.assertIn('Target Audience', result)
        self.assertIn('Campaign Details', result)

    def test_generate_prompt_markdown_includes_journey_section(self):
        """Test that generated prompt includes Journey Requirements section."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('2. JOURNEY REQUIREMENTS', result)
        self.assertIn('Journey Duration', result)
        self.assertIn('Timing Configuration', result)

    def test_generate_prompt_markdown_includes_brand_section(self):
        """Test that generated prompt includes Brand Guidelines section."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('3. BRAND GUIDELINES', result)
        self.assertIn('Voice & Tone', result)
        self.assertIn('Visual Identity', result)
        self.assertIn('#315891', result)  # primary color

    def test_generate_prompt_markdown_includes_platform_section(self):
        """Test that generated prompt includes Platform Constraints section."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('4. PLATFORM CONSTRAINTS', result)
        self.assertIn('Character Limits', result)
        self.assertIn('Message Type Rules', result)

    def test_generate_prompt_markdown_includes_targets_section(self):
        """Test that generated prompt includes Conversion Targets section."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('5. CONVERSION TARGETS', result)
        self.assertIn('70%', result)  # open rate
        self.assertIn('End-to-End Conversion', result)

    def test_generate_prompt_markdown_includes_compliance_section(self):
        """Test that generated prompt includes Compliance section."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('6. COMPLIANCE & SPECIAL REQUIREMENTS', result)
        self.assertIn('Must Include', result)
        self.assertIn('Type STOP to opt-out', result)

    def test_generate_prompt_markdown_includes_output_specs(self):
        """Test that generated prompt includes Output Specifications."""
        form_data = self.get_minimal_form_data()
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('SUMMARY WORKFLOW HTML - EXACT STRUCTURE', result)
        self.assertIn('FULL DETAIL WORKFLOW HTML - EXACT STRUCTURE', result)
        self.assertIn('NO emojis', result)
        self.assertIn('NO EMOJIS', result)

    def test_generate_prompt_markdown_with_segmentation(self):
        """Test prompt generation with segmentation options."""
        form_data = self.get_minimal_form_data()
        form_data['segmentation_question'] = 'What interests you most?'
        form_data['option_1_label'] = 'First Home'
        form_data['option_1_desc'] = 'For first-time buyers'
        form_data['option_2_label'] = 'Retirement'
        form_data['option_2_desc'] = 'For retirement savings'
        form_data['option_3_label'] = 'Both'
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('What interests you most?', result)
        self.assertIn('First Home', result)
        self.assertIn('Retirement', result)

    def test_generate_prompt_markdown_calculates_e2e_conversion(self):
        """Test that end-to-end conversion is calculated correctly."""
        form_data = self.get_minimal_form_data()
        # 70% * 40% * 40% * 20% = 2.24%
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('2.24%', result)

    def test_generate_prompt_markdown_with_requirements_list(self):
        """Test prompt generation with requirements list."""
        form_data = self.get_minimal_form_data()
        form_data['requirements[]'] = ['Ages 18-39', 'UK resident']
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('Ages 18-39', result)
        self.assertIn('UK resident', result)

    def test_generate_prompt_markdown_with_supporting_urls(self):
        """Test prompt generation with supporting URLs."""
        form_data = self.get_minimal_form_data()
        form_data['supporting_urls[]'] = ['https://example.com/page1', 'https://example.com/page2']
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('https://example.com/page1', result)
        self.assertIn('https://example.com/page2', result)


class TestPromptBuilderLegacy(unittest.TestCase):
    """Tests for backward compatibility with old form field names."""

    def test_generate_prompt_markdown_legacy_fields(self):
        """Test prompt generation with legacy field names still works."""
        # Old form field names for backward compatibility
        form_data = {
            'platform': 'WATI',
            'format': 'B2C',
            'duration_overall': '3 days',
            'brand_name': 'Test Brand',
            'industry': 'Test Industry',
            'audience': 'Test Audience',
            'offer_text': 'Test Offer',
            'quote_code': 'TEST123',
            'num_journeys': '2',
            'deliverables': 'Journeys: 2. Deliverables: 1, 2A, 2B',
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
        
        # Should not raise an error even with old field names
        result = generate_prompt_markdown(form_data)
        
        # Should still generate a valid prompt
        self.assertIn('PROMPT: WhatsApp Journey Generator', result)


if __name__ == '__main__':
    unittest.main()
