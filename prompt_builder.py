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
    
    # Handle colors - use defaults if URL provided but no colors specified
    primary_color = get_value('primary_color', '')
    accent_color = get_value('accent_color', '')
    background_color = get_value('background_color', '')
    colors_url = get_value('colors_from_url', '')
    
    # If URL provided but no colors, use professional defaults
    if colors_url and not primary_color:
        primary_color = '#1e3a5f'  # Dark blue
    if colors_url and not accent_color:
        accent_color = '#e67e22'   # Orange
    if colors_url and not background_color:
        background_color = '#f5f7fa'  # Light gray
    
    # Fallback defaults if still empty
    if not primary_color:
        primary_color = '#1e3a5f'
    if not accent_color:
        accent_color = '#e67e22'
    if not background_color:
        background_color = '#f5f7fa'
    
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
            'primary_color': primary_color,
            'accent_color': accent_color,
            'background_color': background_color,
            'colors_from_url': colors_url,
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
- Prospect acquisition journeys
- Multi-day promotional and educational flows

---

## ⚠️ CRITICAL: USE ONLY THE USER'S DATA - NO EXCEPTIONS ⚠️

**THE USER HAS PROVIDED SPECIFIC DATA. YOU MUST USE IT EXACTLY.**

| Data Field | User's Value (USE THIS EXACTLY) |
|------------|--------------------------------|
| Company Name | **{brief['company_name']}** |
| Product Name | **{brief['product_name']}** |
| Target Audience | **{brief['audience_description']}** |
| Campaign Offer | **{brief['campaign_offer']}** |
| Main URL | **{brief['main_product_url']}** |
| Application URL | **{brief['application_url']}** |
| Assets | **{brief['assets_list']}** |

### STRICTLY FORBIDDEN - DO NOT DO THESE:

❌ **DO NOT invent a company name** - Use "{brief['company_name']}" only
❌ **DO NOT invent a product name** - Use "{brief['product_name']}" only  
❌ **DO NOT invent an industry** - The industry is implied by the user's product
❌ **DO NOT invent URLs** - Use ONLY "{brief['main_product_url']}" and "{brief['application_url']}"
❌ **DO NOT invent assets** - Use ONLY what's in "{brief['assets_list']}"
❌ **DO NOT use emojis or icons anywhere**
❌ **DO NOT create fictional scenarios, case studies, or examples**

### YOU MAY BE CREATIVE WITH:

✅ Message copy/wording (following brand voice)
✅ Journey flow and timing
✅ How you describe benefits of the user's actual product

Your job:
1. Take the structured input fields below.
2. Build a normalised `CONFIG` object using ONLY the provided data.
3. Generate:
   - Journey Markdown specs (.md) for each journey.
   - HTML visualisations:
     - A) Summary Workflow HTML (structure overview)
     - B) Full Detail Workflow HTML (complete step-by-step journey with all copy)

All journeys must:
- Respect **{platform['platform']} message/character limits**.
- Follow the specified **timeline & structure**.
- Use **brand voice** and **offer** provided.
- Use ONLY the URLs and assets provided in the BRIEF section.

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
| Colors Source URL | {brand['colors_from_url'] or '(Not specified)'} |
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

## OUTPUT SPECIFICATIONS - CRITICAL: FOLLOW EXACTLY

### COLOR SCHEME (Use these exact colors)

```css
:root {{
  --primary: {brand['primary_color']};        /* Dark blue - header, day badges */
  --primary-light: {brand['primary_color']}20; /* 20% opacity - backgrounds */
  --accent: {brand['accent_color']};          /* Orange/yellow - highlights, badges */
  --accent-light: {brand['accent_color']}20;  /* 20% opacity - step backgrounds */
  --background: {brand['background_color']};  /* Light gray - page background */
  --white: #ffffff;                           /* Cards */
  --text-dark: #1a1a2e;                       /* Primary text */
  --text-light: #6b7280;                      /* Secondary text */
  --success: #10b981;                         /* Green for conversational */
  --broadcast: #3b82f6;                       /* Blue for broadcast */
}}
```

---

### SUMMARY WORKFLOW HTML - EXACT STRUCTURE

**ABSOLUTE REQUIREMENTS:**
- NO emojis anywhere (not in titles, not in content, nowhere)
- NO icons or icon fonts
- NO gradients (except header)
- NO pink, purple, or bright colors
- Professional business document style
- White cards on light gray background

**EXACT HTML STRUCTURE TO FOLLOW:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Journey Name] - Summary Workflow</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: {brand['background_color']};
      color: #1a1a2e;
      line-height: 1.6;
    }}
    
    /* HEADER - Dark blue gradient */
    .header {{
      background: linear-gradient(135deg, {brand['primary_color']} 0%, #0f2942 100%);
      color: white;
      padding: 40px 20px;
      text-align: center;
    }}
    .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
    .header .subtitle {{ opacity: 0.9; margin-bottom: 20px; }}
    
    /* METRICS ROW - Horizontal cards in header */
    .metrics-row {{
      display: flex;
      justify-content: center;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .metric {{
      background: rgba(255,255,255,0.15);
      padding: 15px 25px;
      border-radius: 8px;
      text-align: center;
    }}
    .metric-value {{ font-size: 24px; font-weight: 700; }}
    .metric-label {{ font-size: 12px; text-transform: uppercase; opacity: 0.8; }}
    
    .container {{ max-width: 1000px; margin: 0 auto; padding: 30px 20px; }}
    
    /* WHITE CARDS */
    .card {{
      background: white;
      border-radius: 12px;
      padding: 25px;
      margin-bottom: 25px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .card-title {{
      font-size: 18px;
      font-weight: 600;
      color: {brand['primary_color']};
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid {brand['primary_color']}20;
    }}
    
    /* JOURNEY OVERVIEW - 4 column grid */
    .overview-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
    }}
    .overview-item h4 {{
      font-size: 11px;
      text-transform: uppercase;
      color: #6b7280;
      margin-bottom: 5px;
    }}
    .overview-item p {{ font-size: 14px; color: #1a1a2e; }}
    
    /* DAY SECTION with orange badge */
    .day-section {{ margin-bottom: 30px; }}
    .day-header {{
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 15px;
    }}
    .day-badge {{
      width: 50px;
      height: 50px;
      background: {brand['accent_color']};
      color: white;
      border-radius: 50%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-weight: 700;
    }}
    .day-badge .code {{ font-size: 14px; }}
    .day-badge .label {{ font-size: 8px; text-transform: uppercase; }}
    .day-title {{ font-size: 20px; font-weight: 600; color: #1a1a2e; }}
    .day-meta {{ font-size: 13px; color: #6b7280; }}
    
    /* STEP CARDS - Grid layout */
    .steps-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 15px;
    }}
    .step-card {{
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 18px;
    }}
    .step-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }}
    .step-number {{
      width: 28px;
      height: 28px;
      background: {brand['primary_color']};
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 600;
    }}
    .step-badge {{
      font-size: 10px;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .step-badge.broadcast {{ background: #dbeafe; color: #1d4ed8; }}
    .step-badge.conversational {{ background: #d1fae5; color: #047857; }}
    .step-title {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; }}
    .step-timing {{ font-size: 12px; color: #6b7280; }}
    .step-type {{ font-size: 12px; color: #9ca3af; margin-top: 8px; }}
    
    /* PERSONALIZATION BOX */
    .personalization-box {{
      background: {brand['primary_color']}08;
      border: 2px dashed {brand['primary_color']}40;
      border-radius: 12px;
      padding: 25px;
      margin: 25px 0;
    }}
    .personalization-title {{
      font-size: 16px;
      font-weight: 600;
      color: {brand['primary_color']};
      margin-bottom: 10px;
    }}
    .paths-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
      margin-top: 15px;
    }}
    .path-card {{
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 15px;
      text-align: center;
    }}
    .path-card h4 {{ font-size: 14px; font-weight: 600; color: #1a1a2e; }}
    
    /* STATISTICS SECTION */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 15px;
      margin-top: 15px;
    }}
    .stat-card {{
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 20px;
      text-align: center;
    }}
    .stat-value {{ font-size: 28px; font-weight: 700; color: {brand['primary_color']}; }}
    .stat-label {{ font-size: 11px; color: #6b7280; text-transform: uppercase; margin-top: 5px; }}
    
    /* FOOTER */
    .footer {{
      text-align: center;
      padding: 30px;
      color: #9ca3af;
      font-size: 12px;
      border-top: 1px solid #e5e7eb;
      margin-top: 40px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{brief['company_name']} {brief['product_name']} Journey</h1>
    <p class="subtitle">{brief['campaign_name'] or brief['product_name']} - Summary Workflow</p>
  </div>
  
  <div class="container">
    <!-- Journey Overview Card - USE EXACT DATA FROM BRIEF -->
    <div class="card">
      <div class="card-title">Journey Overview</div>
      <div class="overview-grid">
        <div class="overview-item"><h4>Entry Point</h4><p>{brief['entry_point']}</p></div>
        <div class="overview-item"><h4>Target Audience</h4><p>{brief['audience_description']}</p></div>
        <div class="overview-item"><h4>Primary Goal</h4><p>Convert to {brief['product_name']}</p></div>
        <div class="overview-item"><h4>Offer</h4><p>{brief['campaign_offer']}</p></div>
      </div>
    </div>
    
    <!-- Day 0 Section -->
    <div class="day-section">
      <div class="day-header">
        <div class="day-badge"><span class="code">D0</span><span class="label">Day Zero</span></div>
        <div>
          <div class="day-title">Immediate Welcome & Personalisation</div>
          <div class="day-meta">Duration: 0-3 hours | Purpose: Establish trust, educate on benefits</div>
        </div>
      </div>
      <div class="steps-grid">
        <div class="step-card">
          <div class="step-header">
            <div class="step-number">1</div>
            <span class="step-badge broadcast">Broadcast</span>
          </div>
          <div class="step-title">Welcome & Instant Value</div>
          <div class="step-timing">Immediate</div>
          <div class="step-type">Standard</div>
        </div>
        <!-- More step cards... -->
      </div>
    </div>
    
    <!-- Personalization Branching -->
    <div class="personalization-box">
      <div class="personalization-title">Personalisation Branching</div>
      <p>Based on the user's selection, the journey splits into three tailored paths for Days 1-3</p>
      <div class="paths-grid">
        <div class="path-card"><h4>Path A: [Option 1]</h4></div>
        <div class="path-card"><h4>Path B: [Option 2]</h4></div>
        <div class="path-card"><h4>Path C: [Option 3]</h4></div>
      </div>
    </div>
    
    <!-- More day sections (D1, D2, D3)... -->
    
    <!-- Journey Statistics -->
    <div class="card">
      <div class="card-title">Journey Statistics</div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-value">11</div><div class="stat-label">Total Steps</div></div>
        <div class="stat-card"><div class="stat-value">1</div><div class="stat-label">Decision Points</div></div>
        <div class="stat-card"><div class="stat-value">4</div><div class="stat-label">Days Active</div></div>
        <div class="stat-card"><div class="stat-value">3</div><div class="stat-label">Personalisation Paths</div></div>
        <div class="stat-card"><div class="stat-value">4</div><div class="stat-label">Broadcast Messages</div></div>
        <div class="stat-card"><div class="stat-value">7</div><div class="stat-label">Conversational Messages</div></div>
      </div>
    </div>
    
    <!-- URL Links Used in Campaign - REQUIRED SECTION -->
    <div class="card">
      <div class="card-title">URL Links Used in Campaign</div>
      <table style="width:100%; border-collapse: collapse;">
        <thead>
          <tr style="background: {brand['primary_color']}10; text-align: left;">
            <th style="padding: 12px; border-bottom: 2px solid #e5e7eb;">URL</th>
            <th style="padding: 12px; border-bottom: 2px solid #e5e7eb;">Purpose</th>
            <th style="padding: 12px; border-bottom: 2px solid #e5e7eb;">Used In</th>
          </tr>
        </thead>
        <tbody>
          <!-- USE THESE EXACT URLs FROM USER INPUT -->
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: {brand['primary_color']}; word-break: break-all;">{brief['main_product_url']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">Main product/service page</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">[List all steps using this URL]</td>
          </tr>
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: {brand['primary_color']}; word-break: break-all;">{brief['application_url']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">Application/conversion form</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">[List all steps using this URL]</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Assets Required - USE ASSETS FROM USER INPUT: {brief['assets_list']} -->
    <div class="card">
      <div class="card-title">Assets Required for Campaign</div>
      <p style="color: #6b7280; margin-bottom: 15px; font-size: 14px;">Assets provided by user: {brief['assets_list']}</p>
      <table style="width:100%; border-collapse: collapse;">
        <thead>
          <tr style="background: {brand['primary_color']}10; text-align: left;">
            <th style="padding: 12px; border-bottom: 2px solid #e5e7eb;">Asset</th>
            <th style="padding: 12px; border-bottom: 2px solid #e5e7eb;">Type</th>
            <th style="padding: 12px; border-bottom: 2px solid #e5e7eb;">Used In</th>
          </tr>
        </thead>
        <tbody>
          <!-- Create a row for EACH asset from: {brief['assets_list']} -->
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">[Asset name from list above]</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">Image/PDF/Video</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">[List steps where used]</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  
  <div class="footer">
    {brief['company_name']} | {brief['product_name']} Journey | {platform['platform']} WhatsApp Automation
  </div>
</body>
</html>
```

---

### FULL DETAIL WORKFLOW HTML - EXACT STRUCTURE

**ABSOLUTE REQUIREMENTS:**
- Same color scheme as Summary Workflow
- NO emojis anywhere
- NO icons
- Full message copy displayed in each step
- URLs shown in full (not just as links)
- Character counts shown

**EXACT HTML STRUCTURE TO FOLLOW:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Journey Name] - Full Detailed Workflow</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: {brand['background_color']};
      color: #1a1a2e;
      line-height: 1.6;
    }}
    
    /* Same header as Summary */
    .header {{
      background: linear-gradient(135deg, {brand['primary_color']} 0%, #0f2942 100%);
      color: white;
      padding: 40px 20px;
      text-align: center;
    }}
    .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
    .header .subtitle {{ opacity: 0.9; margin-bottom: 20px; }}
    .metrics-row {{
      display: flex;
      justify-content: center;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .metric {{
      background: rgba(255,255,255,0.15);
      padding: 15px 25px;
      border-radius: 8px;
      text-align: center;
    }}
    .metric-value {{ font-size: 24px; font-weight: 700; }}
    .metric-label {{ font-size: 12px; text-transform: uppercase; opacity: 0.8; }}
    
    .container {{ max-width: 900px; margin: 0 auto; padding: 30px 20px; }}
    
    /* DAY HEADER - FULL WIDTH RECTANGLE */
    .day-header-bar {{
      background: {brand['primary_color']};
      color: white;
      padding: 20px 25px;
      border-radius: 12px;
      margin: 30px 0 20px 0;
      display: flex;
      align-items: center;
      gap: 20px;
    }}
    .day-badge-large {{
      width: 60px;
      height: 60px;
      background: {brand['accent_color']};
      border-radius: 50%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      flex-shrink: 0;
    }}
    .day-badge-large .code {{ font-size: 18px; }}
    .day-badge-large .label {{ font-size: 9px; text-transform: uppercase; }}
    .day-info h2 {{ font-size: 22px; margin-bottom: 5px; }}
    .day-info p {{ opacity: 0.9; font-size: 14px; }}
    
    /* STEP CARD - Full detail */
    .step-detail {{
      background: white;
      border-radius: 12px;
      margin-bottom: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      overflow: hidden;
    }}
    .step-detail-header {{
      background: {brand['primary_color']}10;
      padding: 18px 25px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #e5e7eb;
    }}
    .step-detail-number {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .step-num {{
      width: 32px;
      height: 32px;
      background: {brand['primary_color']};
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
    }}
    .step-detail-title {{ font-size: 17px; font-weight: 600; }}
    .step-timing-badge {{
      font-size: 13px;
      color: #6b7280;
    }}
    .step-type-badge {{
      font-size: 11px;
      padding: 5px 12px;
      border-radius: 15px;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .step-type-badge.broadcast {{ background: #dbeafe; color: #1d4ed8; }}
    .step-type-badge.conversational {{ background: #d1fae5; color: #047857; }}
    
    .step-detail-body {{ padding: 25px; }}
    
    /* MESSAGE CONTENT BOX */
    .message-box {{
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .message-label {{
      font-size: 11px;
      text-transform: uppercase;
      color: #6b7280;
      margin-bottom: 8px;
      font-weight: 600;
    }}
    .message-content {{
      font-size: 15px;
      color: #1a1a2e;
      white-space: pre-wrap;
    }}
    .char-count {{
      font-size: 11px;
      color: #9ca3af;
      margin-top: 10px;
      text-align: right;
    }}
    
    /* BUTTONS SECTION - Clickable links */
    .buttons-section {{
      margin-top: 20px;
    }}
    .button-item {{
      margin-bottom: 10px;
    }}
    .button-item a {{
      display: block;
      background: {brand['accent_color']};
      color: #ffffff;
      text-decoration: none;
      padding: 12px 20px;
      border-radius: 8px;
      font-weight: 600;
      text-align: center;
      transition: background 0.2s;
    }}
    .button-item a:hover {{
      background: {brand['primary_color']};
    }}
    .button-url {{
      font-size: 12px;
      color: {brand['primary_color']};
      word-break: break-all;
      margin-top: 5px;
      text-align: center;
    }}
    
    /* AUTO-REPLY BOX */
    .auto-reply {{
      background: #fef3c7;
      border: 1px solid #f59e0b40;
      border-radius: 10px;
      padding: 20px;
      margin-top: 20px;
    }}
    .auto-reply-title {{
      font-size: 13px;
      font-weight: 600;
      color: #92400e;
      margin-bottom: 10px;
    }}
    
    /* WAIT INDICATOR */
    .wait-indicator {{
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      color: #6b7280;
      font-size: 14px;
    }}
    .wait-line {{
      height: 40px;
      width: 2px;
      background: #d1d5db;
      margin: 0 15px;
    }}
    
    /* SUMMARY CARD */
    .summary-card {{
      background: white;
      border-radius: 12px;
      padding: 30px;
      margin-top: 40px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .summary-title {{
      font-size: 20px;
      font-weight: 600;
      color: {brand['primary_color']};
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 2px solid {brand['primary_color']}20;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 20px;
    }}
    .summary-stat {{
      text-align: center;
      padding: 15px;
      background: {brand['background_color']};
      border-radius: 10px;
    }}
    .summary-stat-value {{ font-size: 28px; font-weight: 700; color: {brand['primary_color']}; }}
    .summary-stat-label {{ font-size: 12px; color: #6b7280; margin-top: 5px; }}
    
    .assets-section, .urls-section {{
      margin-top: 30px;
    }}
    .section-subtitle {{
      font-size: 16px;
      font-weight: 600;
      color: #1a1a2e;
      margin-bottom: 15px;
    }}
    .asset-list, .url-list {{
      list-style: none;
    }}
    .asset-list li, .url-list li {{
      padding: 10px 0;
      border-bottom: 1px solid #e5e7eb;
      font-size: 14px;
    }}
    .url-list li a {{
      color: {brand['primary_color']};
      word-break: break-all;
    }}
    
    .footer {{
      text-align: center;
      padding: 30px;
      color: #9ca3af;
      font-size: 12px;
      border-top: 1px solid #e5e7eb;
      margin-top: 40px;
    }}
  </style>
</head>
<body>
  <!-- Header - USE EXACT DATA FROM BRIEF -->
  <div class="header">
    <h1>{brief['company_name']} {brief['product_name']} Journey</h1>
    <p class="subtitle">Full Detailed Workflow - Complete Message Content</p>
  </div>
  
  <div class="container">
    <!-- Journey Overview Card (same as summary) -->
    
    <!-- DAY 0 - Full Width Header Bar -->
    <div class="day-header-bar">
      <div class="day-badge-large"><span class="code">D0</span><span class="label">Day Zero</span></div>
      <div class="day-info">
        <h2>Immediate Welcome & Personalisation</h2>
        <p>Duration: 0-3 hours | Purpose: Establish trust, educate on benefits, segment by goal</p>
      </div>
    </div>
    
    <!-- DAY ASSETS BOX - Show assets needed for this day FROM USER'S ASSETS LIST ONLY -->
    <div style="background: {brand['accent_color']}10; border: 1px solid {brand['accent_color']}30; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
      <div style="font-weight: 600; color: {brand['primary_color']}; margin-bottom: 10px;">Assets Required for Day 0</div>
      <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
        <!-- LIST ONLY ASSETS FROM: {brief['assets_list']} - DO NOT INVENT NEW ASSETS -->
        <li>[First asset from user's assets_list]</li>
        <li>[Second asset from user's assets_list if applicable]</li>
      </ul>
    </div>
    
    <!-- Step 1 Detail Card -->
    <div class="step-detail">
      <div class="step-detail-header">
        <div class="step-detail-number">
          <div class="step-num">1</div>
          <div>
            <div class="step-detail-title">Welcome & Instant Value</div>
            <div class="step-timing-badge">SEND AT: Immediate</div>
          </div>
        </div>
        <span class="step-type-badge broadcast">Broadcast</span>
      </div>
      <div class="step-detail-body">
        <div class="message-box">
          <div class="message-label">Message Body</div>
          <div class="message-content">[Full message text goes here - exactly as it should appear in WhatsApp]</div>
          <div class="char-count">Characters: 156/200</div>
        </div>
        
        <div class="message-box">
          <div class="message-label">Footer</div>
          <div class="message-content">Type STOP to opt-out</div>
          <div class="char-count">Characters: 20/60</div>
        </div>
        
        <!-- CALL TO ACTION BUTTONS - Show button text AND the FULL URL -->
        <div class="buttons-section">
          <div class="message-label">Call to Action Buttons</div>
          <div class="button-item">
            <div class="button-text">Learn More</div>
            <div class="button-url">{brief['main_product_url']}</div>
          </div>
          <div class="button-item">
            <div class="button-text">Apply Now</div>
            <div class="button-url">{brief['application_url']}</div>
          </div>
        </div>
        
        <!-- ASSET USED IN THIS STEP - from user's assets list: {brief['assets_list']} -->
        <div style="margin-top: 15px; padding: 12px; background: #f3f4f6; border-radius: 8px;">
          <div class="message-label">Asset Used</div>
          <div style="color: #4b5563;">[Asset from: {brief['assets_list']}]</div>
        </div>
      </div>
    </div>
    
    <!-- Wait Indicator -->
    <div class="wait-indicator">
      <div class="wait-line"></div>
      Wait: +30 minutes
      <div class="wait-line"></div>
    </div>
    
    <!-- More steps for Day 0... -->
    
    <!-- REPEAT FOR EACH DAY (D1, D2, D3, etc.):
         1. Day Header Bar
         2. Day Assets Box (listing all assets needed for that day)
         3. Step Detail Cards with:
            - Full message content
            - CTA Buttons with FULL URLs displayed
            - Asset used in each step
         4. Wait Indicators between steps
    -->
    
    <!-- Complete Journey Summary - REQUIRED AT BOTTOM -->
    <div class="summary-card">
      <div class="summary-title">Complete Journey Summary</div>
      <div class="summary-grid">
        <div class="summary-stat"><div class="summary-stat-value">[X]</div><div class="summary-stat-label">Total Steps</div></div>
        <div class="summary-stat"><div class="summary-stat-value">[X]</div><div class="summary-stat-label">Decision Points</div></div>
        <div class="summary-stat"><div class="summary-stat-value">[X]</div><div class="summary-stat-label">Days Active</div></div>
        <div class="summary-stat"><div class="summary-stat-value">[X]</div><div class="summary-stat-label">Paths</div></div>
      </div>
      
      <!-- COMPLETE ASSETS LIST - List ALL assets from user input -->
      <div class="assets-section">
        <div class="section-subtitle">Complete Assets Required</div>
        <p style="color: #6b7280; margin-bottom: 10px;">Assets from user input: {brief['assets_list']}</p>
        <table style="width:100%; border-collapse: collapse;">
          <thead>
            <tr style="background: {brand['primary_color']}10;">
              <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">Asset</th>
              <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">Type</th>
              <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">Used In</th>
            </tr>
          </thead>
          <tbody>
            <!-- List each asset from {brief['assets_list']} -->
            <tr><td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">[Asset 1]</td><td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Image/PDF/Video</td><td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Day X Step Y</td></tr>
          </tbody>
        </table>
      </div>
      
      <!-- COMPLETE URL LIST - List ALL URLs from user input -->
      <div class="urls-section">
        <div class="section-subtitle">Complete URL List</div>
        <table style="width:100%; border-collapse: collapse;">
          <thead>
            <tr style="background: {brand['primary_color']}10;">
              <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">URL</th>
              <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">Purpose</th>
              <th style="padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb;">Used In</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; color: {brand['primary_color']}; word-break: break-all;">{brief['main_product_url']}</td>
              <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Main product page</td>
              <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">[List steps]</td>
            </tr>
            <tr>
              <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; color: {brand['primary_color']}; word-break: break-all;">{brief['application_url']}</td>
              <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Application form</td>
              <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">[List steps]</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
  <div class="footer">
    {brief['company_name']} | {brief['product_name']} Journey | {platform['platform']} WhatsApp Automation
  </div>
</body>
</html>
```

---

## CRITICAL: DO NOT DO THE FOLLOWING

1. **DO NOT INVENT OR MAKE UP ANY DATA** - Use ONLY the exact data from Section 1 BRIEF:
   - Company: {brief['company_name']}
   - Product: {brief['product_name']}
   - Audience: {brief['audience_description']}
   - URLs: {brief['main_product_url']} and {brief['application_url']}
   - Assets: {brief['assets_list']}
2. **NO EMOJIS** - Absolutely no emojis anywhere in the HTML output
3. **NO ICONS** - No FontAwesome, no icon fonts, no SVG icons, no decorative icons
4. **NO "Success Metrics & KPIs"** section
5. **NO "Implementation Notes"** section
6. **NO "WATI Technical Specifications"** section
7. **NO "Ready for Implementation"** checklist
8. **NO PINK/PURPLE colors** - Stick to the blue/orange/white color scheme only
9. **NO GRADIENTS** on cards (only on the main header)
10. **NO placeholder URLs** - Never use "example.com" - use the actual URLs provided
11. **NO invented use cases** - Use only what the user described in the BRIEF
12. **NO "Visual Identity" card** - Do not include a card showing colors (Primary, Accent, Background)
13. **NO metrics-section in header** - Do not show Duration/Steps/Paths metrics in header

## CRITICAL: YOU MUST INCLUDE IN BOTH HTML FILES

### In EVERY CTA Button:
- The button text as a CLICKABLE LINK using `<a href="URL" target="_blank">Button Text</a>`
- Use the actual URLs from user input: {brief['main_product_url']} or {brief['application_url']}
- Make buttons clickable so users can verify links work

### At the BOTTOM of BOTH HTML files, include these two sections:

**1. Complete URL List:**
| URL | Purpose | Used In Steps |
|-----|---------|---------------|
| {brief['main_product_url']} | Main product/service page | [list which steps] |
| {brief['application_url']} | Application/conversion | [list which steps] |

**2. Complete Assets List:**
| Asset | Type | Used In Steps |
|-------|------|---------------|
| [Each item from: {brief['assets_list']}] | Image/PDF/Video | [list which steps] |

### Within each Day section of Full Detail Workflow:
- Show which assets from the list above are used in that day's messages

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
(complete HTML document following the EXACT structure above)
```

=== HTML B – FULL DETAIL WORKFLOW ===
```file:full_detail_workflow.html
(complete HTML document following the EXACT structure above)
```
```

Ensure all messages respect platform limits and brand voice.
"""
    
    return prompt
