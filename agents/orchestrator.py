"""
Orchestrator Agent - coordinates the journey building pipeline.

Uses Claude's tool-use pattern to manage extraction, analysis, and
generation of WhatsApp marketing journeys.
"""

import os
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import anthropic

from .tools.content_extractor import extract_from_url, extract_from_text, ExtractedContent
from .tools.pdf_extractor import extract_pdf, extract_pdf_from_bytes
from .tools.brand_analyzer import analyze_brand, generate_brand_markdown, BrandAnalysis
from .tools.audience_suggester import suggest_audiences, generate_audience_markdown, AudienceSuggestion
from .tools.md_merger import merge_to_brief, generate_offer_markdown, MergedBrief


class OrchestrationStatus(Enum):
    """Status of orchestration pipeline."""
    PENDING = "pending"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    REVIEW = "review"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class OrchestrationStep:
    """Record of a single orchestration step."""
    name: str
    status: str  # pending, running, complete, error
    message: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class OrchestrationResult:
    """Complete result of orchestration pipeline."""
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    steps: List[OrchestrationStep] = field(default_factory=list)
    
    # Intermediate outputs
    extracted_content: Optional[Dict[str, Any]] = None
    brand_analysis: Optional[Dict[str, Any]] = None
    audience_suggestion: Optional[Dict[str, Any]] = None
    
    # Markdown outputs
    brand_markdown: str = ""
    audience_markdown: str = ""
    offer_markdown: str = ""
    combined_brief: str = ""
    
    # Error tracking
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'status': self.status.value,
            'steps': [asdict(s) for s in self.steps],
            'extracted_content': self.extracted_content,
            'brand_analysis': self.brand_analysis,
            'audience_suggestion': self.audience_suggestion,
            'brand_markdown': self.brand_markdown,
            'audience_markdown': self.audience_markdown,
            'offer_markdown': self.offer_markdown,
            'combined_brief': self.combined_brief,
            'error': self.error,
        }
        return result
    
    def add_step(self, name: str, status: str, message: str = "", result: Any = None, error: str = None):
        """Add a step record."""
        self.steps.append(OrchestrationStep(
            name=name,
            status=status,
            message=message,
            result=result if isinstance(result, dict) else None,
            error=error,
        ))


class Orchestrator:
    """
    Main orchestrator agent for journey building.
    
    Coordinates the pipeline:
    1. Extract content from URLs and/or PDFs
    2. Analyze brand characteristics
    3. Suggest/refine audience segments
    4. Structure offer and timeline
    5. Merge into combined brief for review
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize orchestrator.
        
        Args:
            api_key: Anthropic API key (falls back to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Progress callback for UI updates
        self.on_progress: Optional[Callable[[str, str], None]] = None
    
    def _emit_progress(self, step: str, message: str):
        """Emit progress update."""
        if self.on_progress:
            self.on_progress(step, message)
    
    def run(
        self,
        urls: Optional[List[str]] = None,
        pdf_files: Optional[List[tuple]] = None,  # [(filename, bytes), ...]
        journey_type: str = "B2C",
        user_inputs: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationResult:
        """
        Run the full orchestration pipeline.
        
        Args:
            urls: List of URLs to extract content from
            pdf_files: List of (filename, bytes) tuples for PDF uploads
            journey_type: "B2B" or "B2C"
            user_inputs: Optional user-provided data (audience, offer, etc.)
            
        Returns:
            OrchestrationResult with all outputs
        """
        result = OrchestrationResult()
        user_inputs = user_inputs or {}
        
        try:
            # Step 1: Extract content from sources
            result.status = OrchestrationStatus.EXTRACTING
            self._emit_progress("extract", "Extracting content from sources...")
            
            extracted = self._extract_content(urls, pdf_files, result)
            if not extracted:
                result.error = "No content could be extracted from provided sources"
                result.status = OrchestrationStatus.ERROR
                return result
            
            result.extracted_content = extracted.to_dict()
            result.add_step("extract", "complete", f"Extracted content from sources")
            
            # Step 2: Analyze brand
            result.status = OrchestrationStatus.ANALYZING
            self._emit_progress("brand", "Analyzing brand characteristics...")
            
            brand_prefs = user_inputs.get('brand', {})
            brand = analyze_brand(extracted.to_dict(), brand_prefs)
            
            # Apply any user overrides
            if user_inputs.get('company_name'):
                brand.company_name = user_inputs['company_name']
            if user_inputs.get('primary_color'):
                brand.primary_color = user_inputs['primary_color']
            if user_inputs.get('accent_color'):
                brand.accent_color = user_inputs['accent_color']
            
            result.brand_analysis = brand.to_dict()
            result.brand_markdown = generate_brand_markdown(brand)
            result.add_step("brand", "complete", f"Analyzed brand: {brand.company_name}")
            
            # Step 3: Suggest audiences
            self._emit_progress("audience", "Generating audience segments...")
            
            audience_input = user_inputs.get('audience', {})
            audiences = suggest_audiences(
                extracted.to_dict(),
                journey_type=journey_type,
                user_provided=audience_input if audience_input else None
            )
            
            result.audience_suggestion = audiences.to_dict()
            result.audience_markdown = generate_audience_markdown(audiences)
            result.add_step("audience", "complete", f"Suggested {len(audiences.segments)} audience segments")
            
            # Step 4: Generate offer/timeline section
            result.status = OrchestrationStatus.GENERATING
            self._emit_progress("offer", "Structuring offer and timeline...")
            
            offer_input = user_inputs.get('offer', {})
            timing_input = user_inputs.get('timing', {})
            
            result.offer_markdown = generate_offer_markdown(
                offer_headline=offer_input.get('headline', extracted.value_proposition.headline),
                discount_code=offer_input.get('discount_code', ''),
                valid_until=offer_input.get('valid_until', ''),
                terms=offer_input.get('terms', ''),
                campaign_start=offer_input.get('campaign_start', ''),
                campaign_end=offer_input.get('campaign_end', ''),
                journey_duration=timing_input.get('duration', '3'),
                timing_strategy=timing_input.get('strategy', 'balanced'),
                timing_config=timing_input.get('config'),
            )
            result.add_step("offer", "complete", "Generated offer and timeline structure")
            
            # Step 5: Merge into combined brief
            self._emit_progress("merge", "Merging into combined brief...")
            
            platform_config = user_inputs.get('platform', None)
            additional_notes = user_inputs.get('additional_notes', '')
            
            merged = merge_to_brief(
                brand_md=result.brand_markdown,
                audience_md=result.audience_markdown,
                offer_md=result.offer_markdown,
                platform_config=platform_config,
                additional_notes=additional_notes,
            )
            
            result.combined_brief = merged.combined_markdown
            result.add_step("merge", "complete", "Created combined brief for review")
            
            # Complete
            result.status = OrchestrationStatus.REVIEW
            self._emit_progress("complete", "Ready for review")
            
        except Exception as e:
            result.error = str(e)
            result.status = OrchestrationStatus.ERROR
            result.add_step("error", "error", str(e), error=str(e))
        
        return result
    
    def _extract_content(
        self,
        urls: Optional[List[str]],
        pdf_files: Optional[List[tuple]],
        result: OrchestrationResult
    ) -> Optional[ExtractedContent]:
        """
        Extract content from all provided sources and merge.
        
        Args:
            urls: List of URLs
            pdf_files: List of (filename, bytes) tuples
            result: OrchestrationResult to add steps to
            
        Returns:
            Merged ExtractedContent or None if no sources
        """
        all_extractions: List[ExtractedContent] = []
        
        # Extract from URLs
        if urls:
            for url in urls:
                self._emit_progress("extract", f"Scraping {url}...")
                try:
                    extracted = extract_from_url(url)
                    all_extractions.append(extracted)
                    result.add_step(
                        "extract_url", 
                        "complete", 
                        f"Extracted from {url}",
                        result={'source': url}
                    )
                except Exception as e:
                    result.add_step(
                        "extract_url",
                        "error",
                        f"Failed to extract from {url}",
                        error=str(e)
                    )
        
        # Extract from PDFs
        if pdf_files:
            for filename, file_bytes in pdf_files:
                self._emit_progress("extract", f"Extracting from {filename}...")
                try:
                    pdf_result = extract_pdf_from_bytes(file_bytes, filename)
                    if pdf_result.success:
                        # Convert PDF text to structured extraction
                        extracted = extract_from_text(pdf_result.content, filename)
                        all_extractions.append(extracted)
                        result.add_step(
                            "extract_pdf",
                            "complete",
                            f"Extracted from {filename} ({pdf_result.pages} pages)",
                            result={'source': filename, 'pages': pdf_result.pages}
                        )
                    else:
                        result.add_step(
                            "extract_pdf",
                            "error",
                            f"Failed to extract from {filename}",
                            error=pdf_result.error
                        )
                except Exception as e:
                    result.add_step(
                        "extract_pdf",
                        "error",
                        f"Failed to extract from {filename}",
                        error=str(e)
                    )
        
        if not all_extractions:
            return None
        
        # Merge extractions (primary source is first URL, supplement with others)
        merged = all_extractions[0]
        
        for extra in all_extractions[1:]:
            # Supplement missing fields
            if not merged.value_proposition.headline and extra.value_proposition.headline:
                merged.value_proposition.headline = extra.value_proposition.headline
            
            if not merged.value_proposition.subheadline and extra.value_proposition.subheadline:
                merged.value_proposition.subheadline = extra.value_proposition.subheadline
            
            # Extend lists
            merged.value_proposition.key_benefits.extend(
                b for b in extra.value_proposition.key_benefits 
                if b not in merged.value_proposition.key_benefits
            )
            
            merged.product.features.extend(
                f for f in extra.product.features
                if f not in merged.product.features
            )
            
            merged.social_proof.testimonials.extend(
                t for t in extra.social_proof.testimonials
                if t not in merged.social_proof.testimonials
            )
            
            merged.social_proof.stats.extend(
                s for s in extra.social_proof.stats
                if s not in merged.social_proof.stats
            )
            
            # Merge assets
            merged.assets.pdfs.extend(extra.assets.pdfs)
            merged.assets.videos.extend(extra.assets.videos)
        
        # Deduplicate and limit
        merged.value_proposition.key_benefits = merged.value_proposition.key_benefits[:5]
        merged.product.features = merged.product.features[:10]
        merged.social_proof.testimonials = merged.social_proof.testimonials[:3]
        merged.social_proof.stats = merged.social_proof.stats[:5]
        
        return merged
    
    def run_with_llm_reasoning(
        self,
        urls: Optional[List[str]] = None,
        pdf_files: Optional[List[tuple]] = None,
        journey_type: str = "B2C",
        user_inputs: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationResult:
        """
        Run orchestration with LLM-powered reasoning for better extraction.
        
        Uses Claude to analyze extracted content and make intelligent
        decisions about brand positioning, audience targeting, etc.
        
        Requires ANTHROPIC_API_KEY to be set.
        """
        if not self.client:
            # Fall back to non-LLM version
            return self.run(urls, pdf_files, journey_type, user_inputs)
        
        # First, run basic extraction
        result = self.run(urls, pdf_files, journey_type, user_inputs)
        
        if result.status == OrchestrationStatus.ERROR:
            return result
        
        # Use LLM to enhance the analysis
        try:
            self._emit_progress("enhance", "Enhancing analysis with AI...")
            
            # Create a prompt for LLM to review and enhance
            enhancement_prompt = f"""Review this extracted brand and audience analysis and suggest improvements:

## Extracted Content Summary
{json.dumps(result.extracted_content, indent=2)[:2000]}

## Current Brand Analysis  
{result.brand_markdown[:1500]}

## Current Audience Segments
{result.audience_markdown[:1500]}

Please provide:
1. Any missing key value propositions
2. Suggested improvements to audience targeting
3. Recommended messaging angles based on the brand

Keep your response concise and actionable."""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": enhancement_prompt}]
            )
            
            enhancement = response.content[0].text
            
            # Add enhancement to the brief
            if enhancement:
                result.combined_brief = result.combined_brief.replace(
                    "## Pre-Generation Checklist",
                    f"""## AI Enhancement Suggestions

{enhancement}

---

## Pre-Generation Checklist"""
                )
            
            result.add_step("enhance", "complete", "Added AI enhancement suggestions")
            
        except Exception as e:
            # Non-fatal - just skip enhancement
            result.add_step("enhance", "skipped", f"AI enhancement skipped: {str(e)}")
        
        return result


# Convenience function for simple usage
def orchestrate(
    urls: Optional[List[str]] = None,
    pdf_files: Optional[List[tuple]] = None,
    journey_type: str = "B2C",
    user_inputs: Optional[Dict[str, Any]] = None,
    use_llm: bool = False,
) -> OrchestrationResult:
    """
    Convenience function to run orchestration.
    
    Args:
        urls: List of URLs to extract from
        pdf_files: List of (filename, bytes) tuples
        journey_type: "B2B" or "B2C"
        user_inputs: User-provided data
        use_llm: Whether to use LLM enhancement
        
    Returns:
        OrchestrationResult
    """
    orchestrator = Orchestrator()
    
    if use_llm:
        return orchestrator.run_with_llm_reasoning(urls, pdf_files, journey_type, user_inputs)
    else:
        return orchestrator.run(urls, pdf_files, journey_type, user_inputs)

