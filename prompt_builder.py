"""
Prompt builder - generates prompt.md file from form inputs.
Updated for comprehensive form structure.
"""
import json
from typing import Dict, Any, List


def build_config_from_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build normalized CONFIG object from form data."""
    
    def get_value(key: str, default: str = "") -> str:
        val = form_data.get(key, "")
        if isinstance(val, str):
            return val.strip() or default
        return str(val) if val else default
    
    def get_list(key: str) -> List[str]:
        value = form_data.get(key, "")
        if isinstance(value, list):
            return [v.strip() for v in value if v and str(v).strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split('\n') if v.strip()]
        return []
    
    def get_bool(key: str, default: bool = False) -> bool:
        val = form_data.get(key, "")
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ('yes', 'true', '1', 'on')
        return default
    
    # Extract features from form
    features = []
    if form_data.get('features'):
        try:
            features = json.loads(form_data.get('features', '[]'))
        except (json.JSONDecodeError, TypeError):
            pass
    if not features:
        # Fallback to individual fields
        for i in range(1, 10):
            f = form_data.get(f'feature_{i}', '')
            if isinstance(f, str) and f.strip():
                features.append(f.strip())
    
    # Build tone list
    tone_of_voice = get_list('tone_of_voice[]') or get_list('tone_of_voice')
    
    # Build config
    config = {
        'BRIEF': {
            'product_name': get_value('product_name'),
            'company_name': get_value('company_name'),
            'campaign_name': get_value('campaign_name'),
            'audience_description': get_value('audience_description'),
            'age_range': get_value('age_range'),
            'geographic_location': get_value('geographic_location'),
            'entry_point': get_value('entry_point'),
            'campaign_offer': get_value('campaign_offer'),
            'offer_valid_until': get_value('offer_valid_until'),
            'features': features,
            'requirements': get_list('requirements[]') or get_list('requirements'),
            'main_product_url': get_value('main_product_url'),
            'application_url': get_value('application_url'),
            'supporting_urls': get_list('supporting_urls[]') or get_list('supporting_urls'),
            'file_references': get_list('file_references[]') or get_list('file_references'),
            'assets_list': get_value('assets_list'),
        },
        'JOURNEY': {
            'duration_days': get_value('journey_duration', '2'),
            'total_messages': get_value('total_messages', '7'),
            'include_personalization': get_bool('include_personalization', True),
            'decision_points': get_value('decision_points', '1'),
            'segmentation_question': get_value('segmentation_question'),
            'options': [
                {'label': get_value('option_1_label'), 'description': get_value('option_1_desc')},
                {'label': get_value('option_2_label'), 'description': get_value('option_2_desc')},
                {'label': get_value('option_3_label'), 'description': get_value('option_3_desc')},
            ],
            'timing': {
                'day0_strategy': get_value('day0_timing_strategy', 'fast'),
                'step1_to_2': get_value('step1_to_2_delay', '10 seconds'),
                'step2_to_3': get_value('step2_to_3_delay', '5 seconds'),
                'step3_to_auto': get_value('step3_to_autoreplies', 'Immediate'),
                'day1_start': get_value('day1_start', '24 hours'),
                'step5_to_6': get_value('step5_to_6_delay', '2 hours'),
                'step6_to_7': get_value('step6_to_7_delay', '10 minutes'),
            },
        },
        'BRAND': {
            'tone_of_voice': tone_of_voice,
            'brand_positioning': get_value('brand_positioning'),
            'use_emojis': get_bool('use_emojis', False),
            'emoji_style': get_value('emoji_style'),
            'primary_color': get_value('primary_color', '#315891'),
            'accent_color': get_value('accent_color', '#D44437'),
            'background_color': get_value('background_color', '#E9E9E9'),
            'logo_reference': get_value('logo_reference'),
            'brand_phrases': get_list('brand_phrases[]') or get_list('brand_phrases'),
        },
        'PLATFORM': {
            'platform': get_value('platform', 'WATI'),
            'body_text_max': get_value('body_text_max', '200'),
            'header_max': get_value('header_max', '60'),
            'footer_max': get_value('footer_max', '60'),
            'interactive_button_max': get_value('interactive_button_max', '20'),
            'quick_reply_button_max': get_value('quick_reply_button_max', '25'),
        },
        'TARGETS': {
            'open_rate': get_value('target_open_rate', '70'),
            'button_click': get_value('target_button_click', '40'),
            'app_start': get_value('target_app_start', '40'),
            'completion': get_value('target_completion', '20'),
        },
        'COMPLIANCE': {
            'optout_wording': get_value('optout_wording', 'Type STOP to opt-out'),
            'include_disclaimers': get_bool('include_disclaimers', True),
            'include_terms': get_bool('include_terms', True),
            'disclaimer_text': get_value('disclaimer_text'),
            'other_required': get_value('other_required'),
            'content_to_avoid': get_value('content_to_avoid'),
            'competitor_mentions': get_value('competitor_mentions'),
            'regulatory_restrictions': get_value('regulatory_restrictions'),
        },
        'OUTPUTS': {
            'deliverables': get_list('deliverables[]') or get_list('deliverables'),
            'format_prefs': get_list('format_prefs[]') or get_list('format_prefs'),
        },
        'ADDITIONAL': {
            'notes': get_value('additional_notes'),
        }
    }
    
    return config


def generate_prompt_markdown(form_data: Dict[str, Any]) -> str:
    """Generate the prompt.md file content from form data."""
    
    config = build_config_from_form(form_data)
    
    # Helper functions
    def bullet_list(items: List[str], indent: int = 0) -> str:
        prefix = "  " * indent
        return '\n'.join(f"{prefix}- {item}" for item in items if item) if items else f"{prefix}- (Not specified)"
    
    def format_options(options: List[Dict]) -> str:
        result = []
        for i, opt in enumerate(options, 1):
            if opt.get('label'):
                result.append(f"  - **Option {i}:** {opt['label']}")
                if opt.get('description'):
                    result.append(f"    - Focus: {opt['description']}")
        return '\n'.join(result) if result else "  - (Not specified)"
    
    brief = config['BRIEF']
    journey = config['JOURNEY']
    brand = config['BRAND']
    platform = config['PLATFORM']
    targets = config['TARGETS']
    compliance = config['COMPLIANCE']
    outputs = config['OUTPUTS']
    additional = config['ADDITIONAL']
    
    # Calculate end-to-end conversion
    try:
        e2e = (float(targets['open_rate'])/100 * float(targets['button_click'])/100 * 
               float(targets['app_start'])/100 * float(targets['completion'])/100 * 100)
        e2e_str = f"~{e2e:.2f}%"
    except (ValueError, ZeroDivisionError):
        e2e_str = "~2.2%"
    
    # Default values for outputs (can't use backslash in f-string expressions in Python 3.11)
    default_deliverables = """- Journey Documentation (Markdown)
- HTML - Full Detailed View
- HTML - Workflow Overview"""
    
    default_format_prefs = """- Include logo in HTML files
- Show character counts
- Show cumulative timing"""
    
    prompt = f"""# PROMPT: WhatsApp Journey Generator → Markdown + HTML Templates

You are an expert **WhatsApp journey + marketing automation architect** specialised in:
- {platform['platform']} (WhatsApp marketing automation)
- B2C consumer acquisition journeys
- Multi-day promotional and educational flows

Your job:
1. Take the structured input fields below.
2. Build a normalised `CONFIG` object.
3. Generate:
   - Journey Markdown specs (.md) for each journey.
   - HTML visualisations:
     - A) Summary Workflow HTML (structure overview with key metrics)
     - B) Full Detail Workflow HTML (complete step-by-step journey with all copy)

All journeys must:
- Respect **{platform['platform']} message/character limits**.
- Follow the specified **timeline & structure**.
- Use **brand voice** and **offer** provided.

---

## 1. BRIEF (Core Information)

### Product & Company Details

| Field | Value |
|-------|-------|
| Product/Service Name | {brief['product_name']} |
| Company Name | {brief['company_name']} |
| Campaign Name | {brief['campaign_name'] or '(Not specified)'} |

### Target Audience

| Field | Value |
|-------|-------|
| Audience Description | {brief['audience_description']} |
| Age Range | {brief['age_range'] or '(Not specified)'} |
| Geographic Location | {brief['geographic_location'] or '(Not specified)'} |

### Campaign Details

| Field | Value |
|-------|-------|
| Entry Point | {brief['entry_point']} |
| Campaign Offer | {brief['campaign_offer']} |
| Offer Valid Until | {brief['offer_valid_until'] or '(Not specified)'} |

### Product Features

{bullet_list(brief['features'])}

### Eligibility/Requirements

{bullet_list(brief['requirements'])}

### Links & Assets

| Field | Value |
|-------|-------|
| Main Product URL | {brief['main_product_url']} |
| Application/Form URL | {brief['application_url']} |

**Supporting URLs:**
{bullet_list(brief['supporting_urls'])}

**File References:**
{bullet_list(brief['file_references'])}

**Required Assets:**
{brief['assets_list']}

---

## 2. JOURNEY REQUIREMENTS

### Structure

| Field | Value |
|-------|-------|
| Journey Duration | {journey['duration_days']} days |
| Total Messages (approx) | {journey['total_messages']} |
| Include Personalization | {'Yes' if journey['include_personalization'] else 'No'} |
| Decision Points | {journey['decision_points']} |

### Segmentation Paths

**Segmentation Question:** {journey['segmentation_question'] or '(Not specified)'}

**Options:**
{format_options(journey['options'])}

### Timing Configuration

**Day 0 Timing:**
| Step | Delay |
|------|-------|
| Strategy | {journey['timing']['day0_strategy']} |
| Step 1 → Step 2 | {journey['timing']['step1_to_2']} |
| Step 2 → Step 3 | {journey['timing']['step2_to_3']} |
| Step 3 → Auto-replies | {journey['timing']['step3_to_auto']} |

**Day 1+ Timing:**
| Step | Delay |
|------|-------|
| Time until Day 1 starts | {journey['timing']['day1_start']} |
| Step 5 → Step 6 | {journey['timing']['step5_to_6']} |
| Step 6 → Step 7 | {journey['timing']['step6_to_7']} |

---

## 3. BRAND GUIDELINES

### Voice & Tone

| Field | Value |
|-------|-------|
| Tone of Voice | {', '.join(brand['tone_of_voice']) if brand['tone_of_voice'] else 'Professional, Trustworthy'} |
| Brand Positioning | {brand['brand_positioning']} |
| Use Emojis | {'Yes - ' + brand['emoji_style'] if brand['use_emojis'] and brand['emoji_style'] else 'Yes' if brand['use_emojis'] else 'No'} |

### Visual Identity

| Field | Value |
|-------|-------|
| Primary Color | {brand['primary_color']} |
| Accent Color | {brand['accent_color']} |
| Background Color | {brand['background_color']} |
| Logo Reference | {brand['logo_reference'] or '(Not specified)'} |

### Key Brand Phrases

{bullet_list(brand['brand_phrases'])}

---

## 4. PLATFORM CONSTRAINTS

### Platform: {platform['platform']}

### Character Limits

| Element | Max Characters |
|---------|---------------|
| Body Text | {platform['body_text_max']} |
| Header | {platform['header_max']} |
| Footer | {platform['footer_max']} |
| Interactive Button | {platform['interactive_button_max']} |
| Quick Reply Button | {platform['quick_reply_button_max']} |

### Message Type Rules

- **First message:** BROADCAST/TEMPLATE (required)
- **Within 24 hours:** CONVERSATIONAL
- **After 24+ hours:** BROADCAST/TEMPLATE

---

## 5. CONVERSION TARGETS

| Metric | Target |
|--------|--------|
| Open Rate | {targets['open_rate']}% |
| Button Click Rate | {targets['button_click']}% |
| Application/Purchase Start | {targets['app_start']}% |
| Completion Rate | {targets['completion']}% |
| **End-to-End Conversion** | **{e2e_str}** |

---

## 6. COMPLIANCE & SPECIAL REQUIREMENTS

### Must Include

| Requirement | Value |
|-------------|-------|
| Opt-out in first message | Yes (required) |
| Opt-out Wording | "{compliance['optout_wording']}" |
| Compliance Disclaimers | {'Yes' if compliance['include_disclaimers'] else 'No'} |
| "Terms and conditions apply" | {'Yes' if compliance['include_terms'] else 'No'} |

**Disclaimer Text:**
{compliance['disclaimer_text'] or '(Not specified)'}

**Other Required Content:**
{compliance['other_required'] or '(Not specified)'}

### Must Avoid

**Content to Avoid:**
{compliance['content_to_avoid'] or '(Not specified)'}

**Competitor Mentions to Avoid:**
{compliance['competitor_mentions'] or '(Not specified)'}

**Regulatory Restrictions:**
{compliance['regulatory_restrictions'] or '(Not specified)'}

---

## 7. OUTPUTS/DELIVERABLES

### Documents Required

{bullet_list(outputs['deliverables']) if outputs['deliverables'] else default_deliverables}

### Format Preferences

{bullet_list(outputs['format_prefs']) if outputs['format_prefs'] else default_format_prefs}

---

## 8. ADDITIONAL CONTEXT

{additional['notes'] or '(No additional notes)'}

---

## OUTPUT SPECIFICATIONS

### Summary Workflow HTML Requirements

**CRITICAL DESIGN REQUIREMENTS:**
- Use a **maximum of 3 colors** (primary: {brand['primary_color']}, accent: {brand['accent_color']}, background: {brand['background_color']}) with 20% tint variations
- **NO emojis or icons** anywhere in the HTML
- **NO implementation notes section**
- **NO WATI Technical Specifications section**

**REQUIRED SECTIONS (IN THIS EXACT ORDER):**

1. **Header with Key Metrics** - Journey title, subtitle, metrics row (Duration, Total Steps, Decision Points, etc.)

2. **Campaign Strategy Card** - Entry Point, Target Audience, Primary Goal, Offer Code

3. **Journey Timeline Section** - For each day:
   - Day header with duration and purpose
   - Step cards with timing, type (BROADCAST/CONVERSATIONAL), description
   - **Calls to Action cards** showing CTA text, full URL, and purpose

4. **Core Principles Cards** - 4-6 principle cards in a grid

5. **Assets Required Card** - Organized by day, with asset specifications

6. **Key Links Card** - All URLs used, which steps use them, purpose

7. **Discounts Used Card** - Discount codes, amounts, validity, which steps mention them

### Full Detail Workflow HTML Requirements

**CRITICAL DESIGN REQUIREMENTS:**
- Use a **maximum of 3 colors** with 20% tint variations
- **NO emojis or icons** anywhere
- **NO implementation notes section**
- Day headers (D0, D1, etc.) **MUST be full column width rectangles with rounded corners**

**REQUIRED SECTIONS:**

1. **Journey Header** - Title, subtitle, key metrics row

2. **Day-by-Day Breakdown** - For each day:
   - **Full-width Day Header Rectangle** with day name, duration, purpose
   - **Step Cards** with:
     - Step number and title
     - Send timing
     - Message type badge
     - **Full message copy** (header, body, footer with character counts)
     - **Buttons with full URLs displayed**
     - **Call-to-Actions with full URLs**
     - Media/Assets section
     - Auto-Reply sections (for interactive steps)
     - Wait time to next step

3. **Complete Journey Summary Card** - Full width card containing:
   - Summary metrics
   - **Required Assets List** (all assets needed)
   - **Key URLs Used** (all URLs with purposes)
   - **DO NOT include:** "Ready for Implementation" or "WATI Technical Specifications"

---

## OUTPUT FORMAT

Output your response in this order:

```text
=== CONFIG YAML ===
(normalized CONFIG object)

=== JOURNEY MARKDOWN ===
(journey specification in markdown)

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
    
    return prompt
