"""
Markdown merger tool - merges intermediate .md sections into combined brief.

Combines brand profile, audience segments, and offer/timeline into a single
document for user review before journey generation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class MergedBrief:
    """Complete merged brief ready for user review."""
    brand_section: str = ""
    audience_section: str = ""
    offer_section: str = ""
    combined_markdown: str = ""
    generated_at: str = ""
    source_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def merge_to_brief(
    brand_md: str,
    audience_md: str,
    offer_md: str,
    platform_config: Optional[Dict[str, Any]] = None,
    additional_notes: str = ""
) -> MergedBrief:
    """
    Merge all intermediate sections into a combined brief.
    
    Args:
        brand_md: Brand profile markdown
        audience_md: Audience segments markdown
        offer_md: Offer and timeline markdown
        platform_config: Platform constraints (WATI limits, etc.)
        additional_notes: Any additional context from user
        
    Returns:
        MergedBrief with combined markdown
    """
    brief = MergedBrief(
        brand_section=brand_md,
        audience_section=audience_md,
        offer_section=offer_md,
        generated_at=datetime.now().isoformat(),
    )
    
    # Count sources
    source_count = sum(1 for s in [brand_md, audience_md, offer_md] if s)
    brief.source_count = source_count
    
    # Build platform constraints section
    platform_md = _build_platform_section(platform_config) if platform_config else _default_platform_section()
    
    # Combine all sections
    combined = f"""# WhatsApp Journey Brief

> **Auto-generated:** {brief.generated_at}
> 
> Review and edit this document before proceeding to journey generation.
> All sections can be modified to better match your requirements.

---

{brand_md}

---

{audience_md}

---

{offer_md}

---

{platform_md}

"""
    
    if additional_notes:
        combined += f"""---

## Additional Context

{additional_notes}

"""
    
    combined += """---

## Pre-Generation Checklist

Before proceeding to journey generation, confirm:

- [ ] Brand information is accurate
- [ ] Audience segments reflect your target customers  
- [ ] Offer details and timeline are correct
- [ ] Platform constraints match your WATI setup
- [ ] URLs and assets are valid and accessible

---

*Click "Approve & Generate" when ready to create your WhatsApp journey.*
"""
    
    brief.combined_markdown = combined
    
    return brief


def _build_platform_section(config: Dict[str, Any]) -> str:
    """Build platform constraints section from config."""
    
    platform = config.get('platform', 'WATI')
    body_max = config.get('body_text_max', '200')
    header_max = config.get('header_max', '60')
    footer_max = config.get('footer_max', '60')
    button_max = config.get('interactive_button_max', '20')
    quick_reply_max = config.get('quick_reply_button_max', '25')
    
    return f"""## Platform Constraints

### Platform: {platform}

### Character Limits

| Element | Max Characters |
|---------|---------------|
| Body Text | {body_max} |
| Header | {header_max} |
| Footer | {footer_max} |
| Interactive Button | {button_max} |
| Quick Reply Button | {quick_reply_max} |

### Message Type Rules

- **First message:** BROADCAST/TEMPLATE (required)
- **Within 24 hours:** CONVERSATIONAL
- **After 24+ hours:** BROADCAST/TEMPLATE

### Compliance Requirements

- Opt-out text in first message: "Type STOP to opt-out"
- Minimum delay between messages: 3 seconds
- Maximum interactive buttons per message: 3
"""


def _default_platform_section() -> str:
    """Default WATI platform constraints."""
    return _build_platform_section({
        'platform': 'WATI',
        'body_text_max': '200',
        'header_max': '60',
        'footer_max': '60',
        'interactive_button_max': '20',
        'quick_reply_button_max': '25',
    })


def generate_offer_markdown(
    offer_headline: str = "",
    discount_code: str = "",
    valid_until: str = "",
    terms: str = "",
    campaign_start: str = "",
    campaign_end: str = "",
    journey_duration: str = "3",
    timing_strategy: str = "balanced",
    timing_config: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate the offer and timeline markdown section.
    
    Args:
        offer_headline: Main offer text
        discount_code: Promo/discount code if any
        valid_until: Offer expiration date
        terms: Terms and conditions
        campaign_start: Campaign start date
        campaign_end: Campaign end date
        journey_duration: Number of days for journey
        timing_strategy: fast, balanced, or spaced
        timing_config: Specific timing delays
        
    Returns:
        Markdown string for offer section
    """
    
    # Default timing based on strategy
    if not timing_config:
        timing_config = _get_timing_for_strategy(timing_strategy)
    
    md = f"""# Campaign Offer & Timeline

## Offer Details

| Field | Value |
|-------|-------|
| Offer Headline | {offer_headline or '(Not specified)'} |
| Discount/Promo Code | {discount_code or '(None)'} |
| Valid Until | {valid_until or '(Not specified)'} |

### Terms & Conditions

{terms or '(Not specified)'}

---

## Campaign Timeline

| Field | Value |
|-------|-------|
| Campaign Start | {campaign_start or '(Not specified)'} |
| Campaign End | {campaign_end or '(Not specified)'} |
| Journey Duration | {journey_duration} days |
| Timing Strategy | {timing_strategy.title()} |

---

## Message Timing Configuration

### Day 0 (Welcome Sequence)

| Step | Delay |
|------|-------|
| Step 1 (Welcome) | Immediate |
| Step 1 → Step 2 | {timing_config.get('step1_to_2', '30 seconds')} |
| Step 2 → Step 3 | {timing_config.get('step2_to_3', '5 minutes')} |
| Step 3 → Auto-replies | {timing_config.get('step3_to_auto', 'Immediate')} |

### Day 1+ (Follow-up Sequence)

| Step | Delay |
|------|-------|
| Day 0 → Day 1 | {timing_config.get('day1_start', '24 hours')} |
| Day 1 → Day 2 | {timing_config.get('day2_start', '24 hours')} |
| Day 2 → Day 3 | {timing_config.get('day3_start', '24 hours')} |

### Message Pacing

- **Morning messages:** 9:00 AM - 10:00 AM
- **Afternoon follow-ups:** 2:00 PM - 3:00 PM
- **Evening reminders:** 6:00 PM - 7:00 PM (if applicable)

---

## Journey Structure

### Day 0: Welcome & Segmentation
- Welcome message with instant value
- Benefits overview
- Personalization question (segment users)
- Auto-replies with tailored content

### Day 1: Education
- Educational content based on segment
- Product/service deep-dive
- Address common questions

### Day 2: Social Proof
- Testimonials and success stories
- Trust-building content
- Soft CTA

### Day 3: Conversion
- Offer reveal/reminder
- Urgency messaging
- Final CTA push
"""
    
    return md


def _get_timing_for_strategy(strategy: str) -> Dict[str, str]:
    """Get timing configuration based on strategy."""
    
    strategies = {
        'fast': {
            'step1_to_2': '10 seconds',
            'step2_to_3': '5 seconds',
            'step3_to_auto': 'Immediate',
            'day1_start': '12 hours',
            'day2_start': '12 hours',
            'day3_start': '12 hours',
        },
        'balanced': {
            'step1_to_2': '30 minutes',
            'step2_to_3': '1 hour',
            'step3_to_auto': 'Immediate',
            'day1_start': '24 hours',
            'day2_start': '24 hours',
            'day3_start': '24 hours',
        },
        'spaced': {
            'step1_to_2': '2 hours',
            'step2_to_3': '4 hours',
            'step3_to_auto': 'Immediate',
            'day1_start': '48 hours',
            'day2_start': '48 hours',
            'day3_start': '48 hours',
        },
    }
    
    return strategies.get(strategy, strategies['balanced'])


def parse_merged_brief(markdown: str) -> Dict[str, str]:
    """
    Parse a merged brief back into sections.
    
    Useful for extracting edited sections after user review.
    
    Args:
        markdown: The combined markdown document
        
    Returns:
        Dictionary with extracted sections
    """
    sections = {}
    
    # Simple section extraction based on headers
    current_section = None
    current_content = []
    
    for line in markdown.split('\n'):
        if line.startswith('# Brand Profile'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'brand'
            current_content = [line]
        elif line.startswith('# Audience Segments'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'audience'
            current_content = [line]
        elif line.startswith('# Campaign Offer'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'offer'
            current_content = [line]
        elif line.startswith('## Platform Constraints'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'platform'
            current_content = [line]
        elif line.startswith('## Pre-Generation Checklist'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = None
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

