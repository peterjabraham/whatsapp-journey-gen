"""
Tests for the prompt builder functionality.
"""
import unittest
from prompt_builder import generate_prompt_markdown


class TestPromptBuilder(unittest.TestCase):
    """Tests for prompt builder functions."""

    def test_generate_prompt_markdown_basic(self):
        """Test basic prompt generation."""
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
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('WATI', result)
        self.assertIn('Test Brand', result)
        self.assertIn('Test Offer', result)
        self.assertIn('TEST123', result)
        self.assertIn('2', result)  # num_journeys
        self.assertIn('PROMPT: WhatsApp Journey Generator', result)

    def test_generate_prompt_markdown_with_lists(self):
        """Test prompt generation with list fields."""
        form_data = {
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
            'unique_selling_points': ['Point 1', 'Point 2', 'Point 3'],
            'products': ['Product A', 'Product B'],
            'brand_attributes': ['trustworthy', 'expert'],
            'url_product_pages': ['https://example.com/product1', 'https://example.com/product2'],
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
        
        result = generate_prompt_markdown(form_data)
        
        self.assertIn('Point 1', result)
        self.assertIn('Product A', result)
        self.assertIn('trustworthy', result)
        self.assertIn('example.com/product1', result)

    def test_generate_prompt_markdown_empty_optional_fields(self):
        """Test prompt generation with empty optional fields."""
        form_data = {
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
        
        result = generate_prompt_markdown(form_data)
        
        # Should still generate valid prompt even with empty optional fields
        self.assertIn('PROMPT: WhatsApp Journey Generator', result)
        self.assertIn('Test Brand', result)


if __name__ == '__main__':
    unittest.main()

