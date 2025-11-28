"""
Tests for the multi-agent orchestrator components.
"""
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

from agents.tools.content_extractor import (
    extract_from_url,
    extract_from_text,
    ExtractedContent,
    ValueProposition,
    ProductInfo,
    SocialProof,
    CTAs,
    BrandElements,
    Assets,
    EXTRACTION_SCHEMA,
)
from agents.tools.pdf_extractor import (
    extract_pdf,
    extract_pdf_from_bytes,
    get_pdf_metadata,
    PDFExtractionResult,
)
from agents.tools.brand_analyzer import (
    analyze_brand,
    generate_brand_markdown,
    BrandAnalysis,
)
from agents.tools.audience_suggester import (
    suggest_audiences,
    generate_audience_markdown,
    AudienceSegment,
    AudienceSuggestion,
)
from agents.tools.md_merger import (
    merge_to_brief,
    generate_offer_markdown,
    parse_merged_brief,
    MergedBrief,
)
from agents.orchestrator import (
    Orchestrator,
    OrchestrationResult,
    OrchestrationStatus,
    orchestrate,
)


class TestContentExtractor(unittest.TestCase):
    """Tests for content extraction from URLs and text."""
    
    def test_extraction_schema_structure(self):
        """Test that extraction schema has expected structure."""
        self.assertIn('value_proposition', EXTRACTION_SCHEMA)
        self.assertIn('product', EXTRACTION_SCHEMA)
        self.assertIn('social_proof', EXTRACTION_SCHEMA)
        self.assertIn('ctas', EXTRACTION_SCHEMA)
        self.assertIn('brand', EXTRACTION_SCHEMA)
        self.assertIn('assets', EXTRACTION_SCHEMA)
    
    def test_extracted_content_dataclass(self):
        """Test ExtractedContent dataclass creation."""
        content = ExtractedContent(
            source="https://example.com",
            source_type="url"
        )
        self.assertEqual(content.source, "https://example.com")
        self.assertEqual(content.source_type, "url")
        self.assertIsInstance(content.value_proposition, ValueProposition)
        self.assertIsInstance(content.product, ProductInfo)
    
    def test_extracted_content_to_dict(self):
        """Test ExtractedContent serialization."""
        content = ExtractedContent(source="test", source_type="text")
        content.value_proposition.headline = "Test Headline"
        
        result = content.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['source'], "test")
        self.assertEqual(result['value_proposition']['headline'], "Test Headline")
    
    def test_extract_from_text_basic(self):
        """Test basic text extraction."""
        text = """
        Welcome to Our Amazing Product
        
        - Save time with automation
        - Get better results faster
        - Enjoy easy integration
        
        Over 10,000 customers trust us.
        """
        
        result = extract_from_text(text, "test.pdf")
        
        self.assertIsInstance(result, ExtractedContent)
        self.assertEqual(result.source, "test.pdf")
        self.assertEqual(result.source_type, "text")
        # Should extract headline
        self.assertTrue(len(result.value_proposition.headline) > 0)
    
    def test_extract_from_text_benefits(self):
        """Test that benefits are extracted from bullet points."""
        text = """
        Product Overview
        
        - Get instant access to reports
        - Achieve 50% time savings
        - Save money on subscriptions
        """
        
        result = extract_from_text(text)
        
        # Benefits starting with "Get", "Achieve", "Save" should be extracted
        self.assertTrue(len(result.value_proposition.key_benefits) > 0)
    
    @patch('agents.tools.content_extractor.requests.get')
    def test_extract_from_url_success(self, mock_get):
        """Test URL extraction with mocked response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Product | Test Company</title>
            <meta name="description" content="The best product for your needs">
            <meta property="og:site_name" content="Test Company">
        </head>
        <body>
            <h1>Welcome to Test Product</h1>
            <p>This is an amazing product that helps you succeed.</p>
            <ul>
                <li>Feature one</li>
                <li>Feature two</li>
            </ul>
            <a href="/signup" class="btn">Sign Up Now</a>
            <blockquote>"This product changed my life!" - Happy Customer</blockquote>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        result = extract_from_url("https://example.com")
        
        self.assertIsInstance(result, ExtractedContent)
        self.assertEqual(result.source_type, "url")
        # Should extract value prop
        self.assertIn("Test Product", result.value_proposition.headline)
        # Should extract brand name
        self.assertEqual(result.brand.name, "Test Company")
    
    @patch('agents.tools.content_extractor.requests.get')
    def test_extract_from_url_error(self, mock_get):
        """Test URL extraction handles errors gracefully."""
        import requests as req
        mock_get.side_effect = req.RequestException("Connection failed")
        
        result = extract_from_url("https://invalid-url.com")
        
        self.assertIsInstance(result, ExtractedContent)
        self.assertIn("Error", result.raw_text)


class TestPDFExtractor(unittest.TestCase):
    """Tests for PDF extraction."""
    
    def test_extract_pdf_file_not_found(self):
        """Test handling of missing file."""
        result = extract_pdf("/nonexistent/file.pdf")
        
        self.assertIsInstance(result, PDFExtractionResult)
        self.assertFalse(result.success)
        self.assertIn("not found", result.error)
    
    def test_pdf_extraction_result_to_dict(self):
        """Test PDFExtractionResult serialization."""
        result = PDFExtractionResult(
            content="Test content",
            source="test.pdf",
            pages=5,
            success=True
        )
        
        d = result.to_dict()
        self.assertEqual(d['content'], "Test content")
        self.assertEqual(d['pages'], 5)
        self.assertTrue(d['success'])
    
    def test_extract_pdf_from_bytes(self):
        """Test extraction from bytes (simulating upload)."""
        # Create a minimal PDF-like content (will fail but should handle gracefully)
        fake_pdf = b"%PDF-1.4 fake content"
        
        result = extract_pdf_from_bytes(fake_pdf, "upload.pdf")
        
        self.assertIsInstance(result, PDFExtractionResult)
        self.assertEqual(result.source, "upload.pdf")


class TestBrandAnalyzer(unittest.TestCase):
    """Tests for brand analysis."""
    
    def test_analyze_brand_basic(self):
        """Test basic brand analysis."""
        extracted = {
            'brand': {
                'name': 'Test Company',
                'industry': 'financial services',
                'tone_keywords': ['professional', 'trustworthy'],
                'colors': ['#1e3a5f', '#e67e22'],
            },
            'value_proposition': {
                'headline': 'Save for your future',
                'key_benefits': ['Tax-free growth', 'Government bonus'],
            },
            'product': {
                'name': 'Test ISA',
                'description': 'A savings account with benefits',
            },
        }
        
        result = analyze_brand(extracted)
        
        self.assertIsInstance(result, BrandAnalysis)
        self.assertEqual(result.company_name, 'Test Company')
        self.assertEqual(result.industry, 'financial services')
        self.assertIn('professional', result.tone)
    
    def test_analyze_brand_with_user_preferences(self):
        """Test that user preferences override extracted values."""
        extracted = {
            'brand': {'name': 'Auto-Detected', 'industry': 'e-commerce'},
            'value_proposition': {},
            'product': {},
        }
        
        user_prefs = {
            'company_name': 'Override Company',
            'primary_color': '#ff0000',
        }
        
        result = analyze_brand(extracted, user_prefs)
        
        self.assertEqual(result.company_name, 'Override Company')
        self.assertEqual(result.primary_color, '#ff0000')
    
    def test_analyze_brand_emoji_recommendation(self):
        """Test emoji recommendation based on industry."""
        # Financial services should recommend no emojis
        financial = {'brand': {'industry': 'financial services'}, 'value_proposition': {}, 'product': {}}
        result = analyze_brand(financial)
        self.assertEqual(result.emoji_recommendation, 'none')
        
        # E-commerce can have moderate emojis
        ecommerce = {'brand': {'industry': 'e-commerce', 'tone_keywords': ['friendly']}, 'value_proposition': {}, 'product': {}}
        result = analyze_brand(ecommerce)
        self.assertIn(result.emoji_recommendation, ['minimal', 'moderate'])
    
    def test_generate_brand_markdown(self):
        """Test brand markdown generation."""
        analysis = BrandAnalysis(
            company_name="Test Co",
            industry="saas",
            tone=['professional', 'innovative'],
            primary_color="#1e3a5f",
        )
        
        md = generate_brand_markdown(analysis)
        
        self.assertIn("# Brand Profile", md)
        self.assertIn("Test Co", md)
        self.assertIn("saas", md)
        self.assertIn("#1e3a5f", md)


class TestAudienceSuggester(unittest.TestCase):
    """Tests for audience segment suggestions."""
    
    def test_suggest_audiences_b2c(self):
        """Test B2C audience suggestion."""
        extracted = {
            'brand': {'industry': 'financial services'},
            'product': {'name': 'Savings Account'},
            'value_proposition': {'key_benefits': ['Tax-free', 'Government bonus']},
        }
        
        result = suggest_audiences(extracted, journey_type="B2C")
        
        self.assertIsInstance(result, AudienceSuggestion)
        self.assertEqual(result.journey_type, "B2C")
        self.assertTrue(len(result.segments) > 0)
        self.assertTrue(all(s.type == "B2C" for s in result.segments))
    
    def test_suggest_audiences_b2b(self):
        """Test B2B audience suggestion."""
        extracted = {
            'brand': {'industry': 'saas'},
            'product': {'name': 'Business Software'},
            'value_proposition': {'key_benefits': ['Automate tasks']},
        }
        
        result = suggest_audiences(extracted, journey_type="B2B")
        
        self.assertIsInstance(result, AudienceSuggestion)
        self.assertEqual(result.journey_type, "B2B")
        self.assertTrue(len(result.segments) > 0)
    
    def test_suggest_audiences_with_user_input(self):
        """Test that user-provided audience is used."""
        extracted = {'brand': {}, 'product': {}, 'value_proposition': {}}
        
        user_audience = {
            'name': 'My Custom Audience',
            'description': 'Very specific segment',
            'age_range': '25-35',
        }
        
        result = suggest_audiences(extracted, journey_type="B2C", user_provided=user_audience)
        
        self.assertEqual(result.segments[0].name, 'My Custom Audience')
        self.assertEqual(result.segments[0].age_range, '25-35')
    
    def test_segmentation_question_generated(self):
        """Test that a segmentation question is generated."""
        extracted = {
            'brand': {'industry': 'e-commerce'},
            'product': {'name': 'Product'},
            'value_proposition': {},
        }
        
        result = suggest_audiences(extracted, journey_type="B2C")
        
        self.assertTrue(len(result.segmentation_question) > 0)
    
    def test_generate_audience_markdown(self):
        """Test audience markdown generation."""
        suggestion = AudienceSuggestion(
            journey_type="B2C",
            segments=[
                AudienceSegment(
                    name="Young Professionals",
                    type="B2C",
                    description="Career-focused individuals",
                    age_range="25-35",
                    pain_points=["Time constraints", "Budget limitations"],
                    goals=["Save money", "Grow career"],
                )
            ],
            segmentation_question="What's most important to you?",
        )
        
        md = generate_audience_markdown(suggestion)
        
        self.assertIn("# Audience Segments", md)
        self.assertIn("Young Professionals", md)
        self.assertIn("25-35", md)
        self.assertIn("Time constraints", md)


class TestMDMerger(unittest.TestCase):
    """Tests for markdown merging."""
    
    def test_merge_to_brief(self):
        """Test merging sections into combined brief."""
        brand_md = "# Brand Profile\n\nCompany: Test Co"
        audience_md = "# Audience Segments\n\nSegment 1: Users"
        offer_md = "# Campaign Offer\n\nOffer: 20% off"
        
        result = merge_to_brief(brand_md, audience_md, offer_md)
        
        self.assertIsInstance(result, MergedBrief)
        self.assertIn("# WhatsApp Journey Brief", result.combined_markdown)
        self.assertIn("Test Co", result.combined_markdown)
        self.assertIn("20% off", result.combined_markdown)
        self.assertIn("Pre-Generation Checklist", result.combined_markdown)
    
    def test_merge_with_platform_config(self):
        """Test merging with custom platform config."""
        result = merge_to_brief(
            "# Brand",
            "# Audience", 
            "# Offer",
            platform_config={
                'platform': 'Custom Platform',
                'body_text_max': '300',
            }
        )
        
        self.assertIn("Custom Platform", result.combined_markdown)
        self.assertIn("300", result.combined_markdown)
    
    def test_generate_offer_markdown(self):
        """Test offer markdown generation."""
        md = generate_offer_markdown(
            offer_headline="Get 20% off",
            discount_code="SAVE20",
            valid_until="2024-12-31",
            journey_duration="3",
            timing_strategy="balanced",
        )
        
        self.assertIn("# Campaign Offer", md)
        self.assertIn("Get 20% off", md)
        self.assertIn("SAVE20", md)
        self.assertIn("3 days", md)
    
    def test_timing_strategies(self):
        """Test different timing strategies."""
        fast = generate_offer_markdown(timing_strategy="fast")
        balanced = generate_offer_markdown(timing_strategy="balanced")
        spaced = generate_offer_markdown(timing_strategy="spaced")
        
        # Fast should have shorter delays
        self.assertIn("10 seconds", fast)
        # Balanced should have 30 minutes
        self.assertIn("30 minutes", balanced)
        # Spaced should have 2 hours
        self.assertIn("2 hours", spaced)
    
    def test_parse_merged_brief(self):
        """Test parsing merged brief back into sections."""
        combined = """# WhatsApp Journey Brief

# Brand Profile
Company info here

# Audience Segments
Segment info here

# Campaign Offer
Offer info here

## Platform Constraints
Platform info here

## Pre-Generation Checklist
"""
        
        sections = parse_merged_brief(combined)
        
        self.assertIn('brand', sections)
        self.assertIn('audience', sections)
        self.assertIn('offer', sections)


class TestOrchestrator(unittest.TestCase):
    """Tests for the main orchestrator."""
    
    def test_orchestration_result_structure(self):
        """Test OrchestrationResult dataclass."""
        result = OrchestrationResult()
        
        self.assertEqual(result.status, OrchestrationStatus.PENDING)
        self.assertEqual(result.steps, [])
        self.assertIsNone(result.extracted_content)
    
    def test_orchestration_result_add_step(self):
        """Test adding steps to result."""
        result = OrchestrationResult()
        result.add_step("extract", "complete", "Extracted from 1 source")
        
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.steps[0].name, "extract")
        self.assertEqual(result.steps[0].status, "complete")
    
    def test_orchestration_result_to_dict(self):
        """Test OrchestrationResult serialization."""
        result = OrchestrationResult(
            status=OrchestrationStatus.REVIEW,
            brand_markdown="# Brand",
            audience_markdown="# Audience",
        )
        result.add_step("test", "complete", "Done")
        
        d = result.to_dict()
        
        self.assertEqual(d['status'], 'review')
        self.assertEqual(d['brand_markdown'], "# Brand")
        self.assertEqual(len(d['steps']), 1)
    
    def test_orchestrator_init(self):
        """Test orchestrator initialization."""
        orch = Orchestrator()
        
        self.assertIsNone(orch.client)  # No API key set
    
    def test_orchestrator_init_with_api_key(self):
        """Test orchestrator with API key."""
        orch = Orchestrator(api_key="test-key")
        
        self.assertIsNotNone(orch.client)
    
    @patch('agents.tools.content_extractor.requests.get')
    def test_orchestrator_run_with_url(self, mock_get):
        """Test full orchestration with URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Product | Test Company</title>
            <meta name="description" content="Great product">
        </head>
        <body>
            <h1>Test Product</h1>
            <p>Description here</p>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        orch = Orchestrator()
        result = orch.run(urls=["https://example.com"], journey_type="B2C")
        
        self.assertIsInstance(result, OrchestrationResult)
        self.assertEqual(result.status, OrchestrationStatus.REVIEW)
        self.assertTrue(len(result.combined_brief) > 0)
        self.assertTrue(len(result.steps) > 0)
    
    def test_orchestrator_run_no_sources(self):
        """Test orchestration fails with no sources."""
        orch = Orchestrator()
        result = orch.run(urls=[], pdf_files=[])
        
        self.assertEqual(result.status, OrchestrationStatus.ERROR)
        # Error message should indicate no content was extracted
        self.assertIn("no content", result.error.lower())
    
    @patch('agents.tools.content_extractor.requests.get')
    def test_orchestrator_run_with_user_inputs(self, mock_get):
        """Test orchestration with user overrides."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Test</title></head><body>Test</body></html>"
        mock_get.return_value = mock_response
        
        orch = Orchestrator()
        result = orch.run(
            urls=["https://example.com"],
            journey_type="B2B",
            user_inputs={
                'company_name': 'Override Corp',
                'offer': {'headline': 'Special Deal'},
            }
        )
        
        self.assertEqual(result.status, OrchestrationStatus.REVIEW)
        # Check overrides are applied
        self.assertIn("Override Corp", result.brand_markdown)
        self.assertIn("Special Deal", result.offer_markdown)
    
    def test_orchestrate_convenience_function(self):
        """Test the orchestrate convenience function."""
        # Without any sources, should error
        result = orchestrate(urls=[], pdf_files=[])
        
        self.assertEqual(result.status, OrchestrationStatus.ERROR)


class TestOrchestratorIntegration(unittest.TestCase):
    """Integration tests for the orchestrator pipeline."""
    
    @patch('agents.tools.content_extractor.requests.get')
    def test_full_pipeline_b2c(self, mock_get):
        """Test complete B2C pipeline produces valid output."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Savings Account | MyBank</title>
            <meta name="description" content="Open a tax-free savings account today">
            <meta property="og:site_name" content="MyBank">
            <style>
                .header { background: #1e3a5f; }
                .btn { background: #e67e22; }
            </style>
        </head>
        <body>
            <h1>Tax-Free Savings Account</h1>
            <p>Start saving for your future with our market-leading ISA.</p>
            <ul>
                <li>Tax-free growth on your savings</li>
                <li>Government bonus of 25%</li>
                <li>Flexible withdrawals</li>
            </ul>
            <a href="/apply" class="btn">Apply Now</a>
            <blockquote>"Best savings account I've ever had!" - John D.</blockquote>
            <p>Over 50,000 customers trust us with their savings.</p>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        result = orchestrate(
            urls=["https://mybank.com/savings"],
            journey_type="B2C",
            user_inputs={
                'offer': {
                    'headline': 'Get £50 bonus when you open an account',
                    'discount_code': 'BONUS50',
                },
                'timing': {
                    'strategy': 'balanced',
                },
            }
        )
        
        # Verify all sections are populated
        self.assertEqual(result.status, OrchestrationStatus.REVIEW)
        self.assertTrue(len(result.brand_markdown) > 100)
        self.assertTrue(len(result.audience_markdown) > 100)
        self.assertTrue(len(result.offer_markdown) > 100)
        self.assertTrue(len(result.combined_brief) > 500)
        
        # Verify key content is present
        self.assertIn("MyBank", result.brand_markdown)
        self.assertIn("financial services", result.brand_markdown.lower())
        self.assertIn("B2C", result.audience_markdown)
        self.assertIn("BONUS50", result.offer_markdown)
        
        # Verify steps completed
        step_names = [s.name for s in result.steps]
        self.assertIn("extract_url", step_names)
        self.assertIn("brand", step_names)
        self.assertIn("audience", step_names)
        self.assertIn("offer", step_names)
        self.assertIn("merge", step_names)


if __name__ == '__main__':
    unittest.main()

