"""
Brand analyzer tool - analyzes brand voice, tone, and positioning.

Takes extracted content and determines brand characteristics that
influence message style in the WhatsApp journey.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class BrandAnalysis:
    """Complete brand analysis result."""
    company_name: str = ""
    industry: str = ""
    
    # Voice characteristics
    tone: List[str] = field(default_factory=list)  # Professional, Friendly, etc.
    formality_level: str = "professional"  # casual, professional, formal
    personality_traits: List[str] = field(default_factory=list)
    
    # Visual identity
    primary_color: str = "#1e3a5f"
    accent_color: str = "#e67e22"
    background_color: str = "#f5f7fa"
    
    # Messaging guidance
    key_phrases: List[str] = field(default_factory=list)
    words_to_avoid: List[str] = field(default_factory=list)
    emoji_recommendation: str = "minimal"  # none, minimal, moderate, frequent
    
    # Positioning
    value_statement: str = ""
    differentiators: List[str] = field(default_factory=list)
    target_emotion: str = ""  # trust, excitement, security, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def analyze_brand(
    extracted_content: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None
) -> BrandAnalysis:
    """
    Analyze brand characteristics from extracted content.
    
    Args:
        extracted_content: Output from content_extractor
        user_preferences: Optional user-provided brand preferences
        
    Returns:
        BrandAnalysis with brand characteristics
    """
    analysis = BrandAnalysis()
    
    # Get brand basics from extracted content
    brand_data = extracted_content.get('brand', {})
    value_prop = extracted_content.get('value_proposition', {})
    product = extracted_content.get('product', {})
    
    analysis.company_name = brand_data.get('name', '')
    analysis.industry = brand_data.get('industry', 'general business')
    
    # Determine tone from extracted keywords
    tone_keywords = brand_data.get('tone_keywords', [])
    analysis.tone = tone_keywords if tone_keywords else ['professional']
    
    # Map tone to formality
    casual_indicators = ['friendly', 'fun', 'casual', 'playful']
    formal_indicators = ['premium', 'luxury', 'established', 'traditional']
    
    if any(t in analysis.tone for t in casual_indicators):
        analysis.formality_level = 'casual'
    elif any(t in analysis.tone for t in formal_indicators):
        analysis.formality_level = 'formal'
    else:
        analysis.formality_level = 'professional'
    
    # Personality traits based on industry and tone
    analysis.personality_traits = _determine_personality(
        analysis.industry, 
        analysis.tone
    )
    
    # Colors from extraction or defaults
    colors = brand_data.get('colors', [])
    if colors:
        analysis.primary_color = colors[0]
        if len(colors) > 1:
            analysis.accent_color = colors[1]
        if len(colors) > 2:
            analysis.background_color = colors[2]
    
    # Key phrases from value proposition
    headline = value_prop.get('headline', '')
    benefits = value_prop.get('key_benefits', [])
    
    if headline:
        analysis.key_phrases.append(headline)
    analysis.key_phrases.extend(benefits[:3])
    
    # Words to avoid based on industry
    analysis.words_to_avoid = _get_words_to_avoid(analysis.industry)
    
    # Emoji recommendation based on formality and industry
    analysis.emoji_recommendation = _recommend_emoji_usage(
        analysis.formality_level,
        analysis.industry
    )
    
    # Value statement
    if headline:
        analysis.value_statement = headline
    elif product.get('description'):
        analysis.value_statement = product['description'][:200]
    
    # Target emotion based on industry
    analysis.target_emotion = _determine_target_emotion(analysis.industry)
    
    # Apply user preferences if provided
    if user_preferences:
        analysis = _apply_user_preferences(analysis, user_preferences)
    
    return analysis


def _determine_personality(industry: str, tone: List[str]) -> List[str]:
    """Determine brand personality traits."""
    traits = []
    
    # Industry-based traits
    industry_traits = {
        'financial services': ['trustworthy', 'reliable', 'expert'],
        'e-commerce': ['helpful', 'efficient', 'customer-focused'],
        'saas': ['innovative', 'smart', 'solution-oriented'],
        'healthcare': ['caring', 'professional', 'supportive'],
        'education': ['knowledgeable', 'encouraging', 'patient'],
        'real estate': ['local expert', 'trustworthy', 'responsive'],
        'grant management': ['innovative', 'caring', 'solution-oriented', 'impact-focused'],
        'marketing automation': ['innovative', 'smart', 'results-driven'],
    }
    
    traits.extend(industry_traits.get(industry, ['professional', 'helpful']))
    
    # Tone-based traits
    if 'friendly' in tone:
        traits.append('approachable')
    if 'innovative' in tone:
        traits.append('forward-thinking')
    if 'premium' in tone:
        traits.append('sophisticated')
    
    return list(set(traits))[:5]


def _get_words_to_avoid(industry: str) -> List[str]:
    """Get words to avoid based on industry regulations/norms."""
    general_avoid = ['spam', 'guaranteed', 'no risk', 'act now']
    
    industry_avoid = {
        'financial services': [
            'guaranteed returns', 
            'risk-free', 
            'get rich',
            'best rates',
            'no-brainer',
        ],
        'healthcare': [
            'cure',
            'miracle',
            'guaranteed results',
            'no side effects',
        ],
        'general business': [],
    }
    
    avoid_list = general_avoid + industry_avoid.get(industry, [])
    return avoid_list


def _recommend_emoji_usage(formality: str, industry: str) -> str:
    """Recommend emoji usage level."""
    # Formal industries should avoid emojis
    formal_industries = ['financial services', 'healthcare', 'legal']
    
    if industry in formal_industries or formality == 'formal':
        return 'none'
    elif formality == 'casual':
        return 'moderate'
    else:
        return 'minimal'


def _determine_target_emotion(industry: str) -> str:
    """Determine the primary emotion to evoke."""
    emotion_map = {
        'financial services': 'security',
        'e-commerce': 'excitement',
        'saas': 'confidence',
        'healthcare': 'reassurance',
        'education': 'aspiration',
        'real estate': 'trust',
        'grant management': 'empowerment',
        'marketing automation': 'confidence',
    }
    
    return emotion_map.get(industry, 'trust')


def _apply_user_preferences(
    analysis: BrandAnalysis, 
    preferences: Dict[str, Any]
) -> BrandAnalysis:
    """Override analysis with user preferences where provided."""
    
    if preferences.get('company_name'):
        analysis.company_name = preferences['company_name']
    
    if preferences.get('tone'):
        analysis.tone = preferences['tone'] if isinstance(preferences['tone'], list) else [preferences['tone']]
    
    if preferences.get('primary_color'):
        analysis.primary_color = preferences['primary_color']
    
    if preferences.get('accent_color'):
        analysis.accent_color = preferences['accent_color']
    
    if preferences.get('use_emojis') is False:
        analysis.emoji_recommendation = 'none'
    elif preferences.get('use_emojis') is True:
        analysis.emoji_recommendation = 'moderate'
    
    if preferences.get('brand_phrases'):
        analysis.key_phrases = preferences['brand_phrases']
    
    return analysis


def generate_brand_markdown(analysis: BrandAnalysis) -> str:
    """
    Generate markdown representation of brand analysis.
    
    Args:
        analysis: BrandAnalysis result
        
    Returns:
        Markdown string for the brand profile section
    """
    tone_str = ', '.join(analysis.tone) if analysis.tone else 'Professional'
    traits_str = ', '.join(analysis.personality_traits) if analysis.personality_traits else 'N/A'
    phrases_str = '\n'.join(f'- {p}' for p in analysis.key_phrases) if analysis.key_phrases else '- (Not specified)'
    avoid_str = '\n'.join(f'- {w}' for w in analysis.words_to_avoid[:5]) if analysis.words_to_avoid else '- (None specified)'
    
    md = f"""# Brand Profile

## Company Information

| Field | Value |
|-------|-------|
| Company Name | {analysis.company_name} |
| Industry | {analysis.industry} |
| Target Emotion | {analysis.target_emotion.title()} |

## Voice & Tone

| Field | Value |
|-------|-------|
| Tone | {tone_str} |
| Formality | {analysis.formality_level.title()} |
| Personality | {traits_str} |
| Emoji Usage | {analysis.emoji_recommendation.title()} |

## Visual Identity

| Field | Value |
|-------|-------|
| Primary Color | {analysis.primary_color} |
| Accent Color | {analysis.accent_color} |
| Background Color | {analysis.background_color} |

## Key Messaging

### Value Statement

{analysis.value_statement or '(Not specified)'}

### Key Phrases to Use

{phrases_str}

### Words/Phrases to Avoid

{avoid_str}

## Differentiators

{chr(10).join(f'- {d}' for d in analysis.differentiators) if analysis.differentiators else '- (Not specified)'}
"""
    
    return md

