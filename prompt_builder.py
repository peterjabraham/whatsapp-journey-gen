"""
Prompt builder - generates prompt.md file from form inputs.
"""
from typing import Dict, Any


def build_config_from_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build normalized CONFIG object from form data."""
    
    # Helper to get form value or default
    def get_value(key: str, default: str = "") -> str:
        return form_data.get(key, "").strip() or default
    
    def get_list(key: str) -> list:
        value = form_data.get(key, "")
        if isinstance(value, list):
            return [v.strip() for v in value if v.strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split('\n') if v.strip()]
        return []
    
    # Extract brand colors
    brand_colors_input = get_value('brand_colours', '')
    # Try to extract HEX codes or use defaults
    primary = '#667eea'
    secondary = '#764ba2'
    accent = '#f59e0b'
    conversion = '#10b981'
    
    # Simple extraction of HEX codes from input
    import re
    hex_codes = re.findall(r'#([0-9A-Fa-f]{6})', brand_colors_input)
    if len(hex_codes) >= 1:
        primary = f"#{hex_codes[0]}"
    if len(hex_codes) >= 2:
        secondary = f"#{hex_codes[1]}"
    if len(hex_codes) >= 3:
        accent = f"#{hex_codes[2]}"
    if len(hex_codes) >= 4:
        conversion = f"#{hex_codes[3]}"
    
    config = {
        'GLOBAL': {
            'platform': get_value('platform', 'WATI (WhatsApp marketing automation)'),
            'format': get_value('format', 'B2C consumer acquisition journeys'),
            'duration_label': get_value('duration_overall', '3 days + initial Day 0 (0-3 hours)'),
            'brand_name': get_value('brand_name', ''),
            'industry': get_value('industry', ''),
            'audience': get_value('audience', ''),
            'discount_text': get_value('offer_text', ''),
            'discount_code': get_value('quote_code', ''),
            'brand_tone': get_value('brand_tone', ''),
            'brand_attributes': get_list('brand_attributes'),
            'brand_emoji_usage': get_value('emoji_usage', 'minimal'),
            'compliance_notes': get_value('compliance', ''),
            'brand_colours': {
                'primary': primary,
                'secondary': secondary,
                'accent': accent,
                'conversion': conversion,
                'background_start': primary,
                'background_end': secondary,
                'text_dark': '#2c3e50',
                'text_light': '#5a6c7d'
            },
            'urls': {
                'homepage': get_value('url_homepage', ''),
                'product_pages': get_list('url_product_pages'),
                'offer_pages': get_list('url_offer_pages'),
                'testimonials': get_list('url_testimonials')
            },
            'products': get_list('products'),
            'urgency_level': get_value('urgency_level', 'medium'),
            'unique_selling_points': get_list('unique_selling_points')
        },
        'TIMELINE_DEFAULTS': {
            'day0_duration': get_value('day0_duration', '0-3 hours'),
            'day0_step1_timing': get_value('day0_step1_timing', 'Immediate'),
            'day0_step2_timing': get_value('day0_step2_timing', '+30 minutes'),
            'day0_step3_timing': get_value('day0_step3_timing', '+2 hours'),
            'day1_start': get_value('day1_start', '+24 hours'),
            'day2_start': get_value('day2_start', '+24 hours'),
            'day3_start': get_value('day3_start', '+24 hours'),
            'final_push_timing': get_value('final_push_timing', '+3 hours')
        },
        'WATI_LIMITS': {
            'message_body_max': 200,
            'button_text_max': 20,
            'header_text_max': 60,
            'footer_text_max': 60,
            'buttons_per_msg': 3,
            'min_delay_seconds': 3,
            'message_type_rules': [
                'Step is BROADCAST if first message or ≥24h gap',
                'Step is CONVERSATIONAL if <24h gap'
            ]
        },
        'JOURNEYS': []  # Will be populated by the AI model
    }
    
    return config


def generate_prompt_markdown(form_data: Dict[str, Any]) -> str:
    """Generate the prompt.md file content from form data."""
    
    def get_value(key: str, default: str = "") -> str:
        return form_data.get(key, "").strip() or default
    
    def get_list(key: str) -> list:
        value = form_data.get(key, "")
        if isinstance(value, list):
            return [v.strip() for v in value if v.strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split('\n') if v.strip()]
        return []
    
    # Build the prompt markdown
    prompt = """# PROMPT: WhatsApp Journey Generator → Markdown + HTML Templates

You are an expert **WhatsApp journey + marketing automation architect** specialised in:
- WATI (WhatsApp marketing automation)
- B2C consumer acquisition journeys
- Multi-day promotional and educational flows

Your job:
1. Take the structured input fields below (CONTEXT, TIMELINE, etc.).
2. Build a normalised `CONFIG` object.
3. Generate:
   - Journey Markdown specs (.md) for each journey.
   - HTML visualisations:
     - A) Full detailed HTML with copy.
     - B) Workflow Overview HTML (structure only – **no long copy**).
     - C) Comparison Summary HTML.

All journeys must:
- Respect **WATI message/character limits**.
- Follow the specified **timeline & structure**.
- Use **brand voice** and **offer** provided by the user.

---

## 0. USER INPUT FIELDS (TO BE FILLED IN BY USER)

The user fills in EVERYTHING inside `Your answer:` sections.
Examples are just hints.

### 0.1 CONTEXT

Platform:  
- Example: WATI (WhatsApp marketing automation)  
- Your answer: {platform}

Format:  
- Example: B2C consumer acquisition journeys  
- Your answer: {format}

Duration (overall journey):  
- Example: 3 days + initial Day 0 (0–3 hours)  
- Your answer: {duration_overall}

Discount (describe clearly):  
- Example: 15% OFF your first order / Free shipping / Tiered discount  
- Your answer: {discount}

Brand Name:  
- Example: Nike  
- Your answer: {brand_name}

Industry:  
- Example: Sportswear / Financial Services / Beauty / [Your industry]  
- Your answer: {industry}

Unique Selling Points (3–5 bullets):  
- Example: [What makes you different]  
- Your answer:
{unique_selling_points}

Brand Tone of Voice:  
- Example: "Warm, direct, plain English, minimal emojis", or URL to guidelines  
- Your answer: {brand_tone}

Brand Colours:  
- Example: "Use brand colours from this URL: [URL]" or list HEX codes  
- Your answer (URLs and/or HEX): {brand_colours}

Brand / Product URLs:  
- Example: Homepage, product pages, offer landing pages  
- Your answer (list URLs):
{urls}

Products:  
- Example: [List your key products or product categories, or URLs]  
- Your answer:
{products}

The Offer (exact wording):  
- Example:  
  Special Offer: Receive a £50 Amazon.co.uk Gift Card when you open a new Lifetime ISA by 19th December 2025.  
- Your answer: {offer_text}

Quote Code:  
- Example: AutumnDate  
- Your answer: {quote_code}

Example Testimonials:  
- Example: URLs to testimonials/case study pages  
- Your answer (URLs):
{testimonials}

Audience:  
- Example: "UK police officers aged 25–45" / "Busy parents in London"  
- Your answer: {audience}

Compliance / Restrictions:  
- Example: "FCA-regulated; avoid guarantees", "No medical claims", etc.  
- Your answer: {compliance}

---

### 0.2 DELIVERABLES NEEDED

Number of journeys required (1–4 recommended):  
- Your answer: {num_journeys}

Which deliverables do you want? (list all that apply)

1. Journey Markdown Documents (.md files)
   - Detailed journey specs for WATI implementation.
2. HTML Visualizations
   - A) Summary Workflow HTML (structure overview with key metrics)
   - B) Full Detail Workflow HTML (complete step-by-step journey with all copy)

Your answer (e.g. "Journeys: 3. Deliverables: 1, 2A, 2B"): {deliverables}

---

### 0.3 JOURNEY TIMELINE PREFERENCES

These act as **defaults** for all journeys unless obviously overridden by the product context.

Day 0 duration:  
- Example: 0–3 hours, 0–2 hours, 0–4 hours  
- Your answer: {day0_duration}

Day 0 – Step 1 timing (Welcome):  
- Example: Immediate  
- Your answer: {day0_step1_timing}

Day 0 – Step 2 timing (Benefits/info):  
- Example: +30 minutes, +1 hour  
- Your answer: {day0_step2_timing}

Day 0 – Step 3 timing (Decision buttons):  
- Example: +2 hours, +90 minutes  
- Your answer: {day0_step3_timing}

Day 1 start (from last Day 0 message):  
- Example: +24 hours, +12 hours, +48 hours  
- Your answer: {day1_start}

Day 2 start (from last Day 1 message):  
- Example: +24 hours, +12 hours  
- Your answer: {day2_start}

Day 3 start (from last Day 2 message):  
- Example: +24 hours, +12 hours  
- Your answer: {day3_start}

Final push timing (after discount reveal):  
- Example: +3 hours, +2 hours  
- Your answer: {final_push_timing}

---

### 0.4 JOURNEY STRUCTURE (GLOBAL RULES)

Each journey must follow this **base structure**:

DAY 0 ([YOUR SPECIFIED DURATION]):  
- Step 1: Welcome message ([YOUR TIMING])  
- Step 2: Benefits/info message ([YOUR TIMING])  
- Step 3: Interactive buttons question ([YOUR TIMING])  
  * 3 button options.  
  * Each button triggers unique auto-reply.  
  * Auto-replies include benefit-specific links.

DAY 1 ([YOUR TIMING] from Day 0):  
- Educational content (varies by button selection).  
- 1–2 messages.

DAY 2 ([YOUR TIMING] from Day 1):  
- Social proof / validation.  
- 2–3 messages.

DAY 3 ([YOUR TIMING] from Day 2):  
- Discount reveal (Limited Time Offer template).  
- Final push message ([YOUR TIMING] after discount).  
- All journeys use same discount code.  
- You specify urgency level:

Urgency level:  
- Example: subtle / medium / strong  
- Your answer: {urgency_level}

If you want exceptions (e.g. different durations per journey), specify here:  
- Your answer (optional): {journey_exceptions}

---

### 0.5 WATI PLATFORM LIMITS (REFERENCE – DO NOT EDIT)

You **must comply** with all of these:

- Message body: **max 200 characters**
- Button text: **max 20 characters**
- Header text: **max 60 characters**
- Footer text: **max 60 characters**
- Interactive buttons: **3 options** per question
- Delays: **≥3 seconds** before follow-up messages
- First message footer: `"Type STOP to opt-out"`

Message type rules:

- Use **BROADCAST/TEMPLATE** when:
  * It is the FIRST message in the journey (Day 0, Step 1), OR  
  * The message is sent **24+ hours** after the previous message.

- Use **CONVERSATIONAL** when:
  * Message is sent **within 24 hours** of the previous message.
  * Follow-up messages in the same day sequence.

You must automatically classify each step as BROADCAST or CONVERSATIONAL based on timing.

---

### 0.6 PERSONALISATION RULES

Global rules for all journeys:

- Exactly **1 decision point** per journey:
  * Day 0 – Step 3.
- Each decision:
  * 3 interactive button options.
- Each button triggers a unique auto-reply that includes:
  * Personalised message copy.
  * Benefit-specific link.
  * Image suggestion (with caption & alt text).
  * Appropriate tags.

Day 1 content must vary based on the Day 0 button selection.

---

### 0.7 BRAND VOICE SETTINGS

Sophistication level (1–10):  
- Example: 3 = very casual, 10 = very formal  
- Your answer: {sophistication_level}

Tone:  
- Example: warm / professional / clinical / friendly / playful / etc.  
- Your answer: {tone}

Emoji usage:  
- Example: minimal / strategic / frequent  
- Your answer: {emoji_usage}

Key brand attributes (keywords):  
- Example: trustworthy, expert, supportive, no-nonsense  
- Your answer:
{brand_attributes}

Language to avoid:  
- Example: "no slang", "avoid hypey claims", "no guarantees"  
- Your answer: {language_to_avoid}

---

## 1. NORMALISED CONFIG OBJECT (MODEL STEP 1)

**Your first task** after reading the user's inputs:

1. Validate completeness (assume missing fields are "unknown" but never hallucinate URLs).
2. Build a normalised `CONFIG` object in **YAML**, with this structure:

```yaml
GLOBAL:
  platform:        "<Platform>"
  format:          "<Format>"
  duration_label:  "<Overall duration description>"
  brand_name:      "<Brand Name>"
  industry:        "<Industry>"
  audience:        "<Audience>"
  discount_text:   "<The Offer text>"
  discount_code:   "<Quote Code>"
  brand_tone:      "<Brand Tone of Voice>"
  brand_attributes:
    - "<attribute1>"
    - "<attribute2>"
  brand_emoji_usage: "<minimal|strategic|frequent>"
  compliance_notes: "<Compliance / Restrictions>"

  brand_colours:
    primary:           "<HEX or best-guess from user input>"
    secondary:         "<HEX or best-guess>"
    accent:            "<HEX or best-guess>"
    conversion:        "<HEX or fallback to accent>"
    background_start:  "<HEX or darker tone>"
    background_end:    "<HEX or darker tone>"
    text_dark:         "<HEX>"
    text_light:        "<HEX>"

  urls:
    homepage:         "<main site if provided>"
    product_pages:    ["<url1>", "<url2>", "..."]
    offer_pages:      ["<url1>", "<url2>", "..."]
    testimonials:     ["<url1>", "<url2>", "..."]

  products:
    - "<product 1 or product type>"
    - "<product 2 or product type>"

  urgency_level: "<subtle|medium|strong>"

TIMELINE_DEFAULTS:
  day0_duration:      "<e.g. 0–3 hours>"
  day0_step1_timing:  "<e.g. Immediate>"
  day0_step2_timing:  "<e.g. +30 minutes>"
  day0_step3_timing:  "<e.g. +2 hours>"

  day1_start:         "<e.g. +24 hours>"
  day2_start:         "<e.g. +24 hours>"
  day3_start:         "<e.g. +24 hours>"
  final_push_timing:  "<e.g. +3 hours>"

WATI_LIMITS:
  message_body_max: 200
  button_text_max: 20
  header_text_max: 60
  footer_text_max: 60
  buttons_per_msg: 3
  min_delay_seconds: 3

  message_type_rules:
    - "Step is BROADCAST if first message or ≥24h gap"
    - "Step is CONVERSATIONAL if <24h gap"

JOURNEYS:
  # You must create this array based on:
  # - Number of journeys requested
  # - User context, product mix, and goals
  # Each journey must follow the Day 0–3 structure and timing defaults.

  - id: "journey_1_slug"
    label: "Journey 1 – <short descriptive label>"
    primary_goal: "<e.g. first purchase, trial booking, application start>"

    meta:
      entry:       "<where leads come from>"
      target:      "<who they are>"
      goal:        "<business goal for this journey>"
      extra_label: "<Duration|Focus>"
      extra_value: "<e.g. 3 days from lead to conversion>"
      total_steps: <int>

    days:
      - code: "D0"
        title: "<Day 0 title>"
        meta:  "<Day 0 duration + purpose>"

        steps:
          - number: 1
            role: "standard"
            title: "<Welcome message title>"
            message_type: "BROADCAST"        # or CONVERSATIONAL based on timing
            timing: "<TIMELINE_DEFAULTS.day0_step1_timing>"

          - number: 2
            role: "standard"
            title: "<Benefits/info message title>"
            message_type: "CONVERSATIONAL"
            timing: "<TIMELINE_DEFAULTS.day0_step2_timing>"

          - number: 3
            role: "decision"
            title: "<Interactive question title>"
            message_type: "CONVERSATIONAL"
            timing: "<TIMELINE_DEFAULTS.day0_step3_timing>"

        branch:
          header: "<description of the 3 personalisation paths>"
          options:
            - "<Path 1 label>"
            - "<Path 2 label>"
            - "<Path 3 label>"

      - code: "D1"
        title: "<Day 1 title>"
        meta:  "<Day 1 purpose and start timing>"

        steps:
          # 1–2 messages; educational; vary by branch

      - code: "D2"
        title: "<Day 2 title>"
        meta:  "<Day 2 purpose and start timing>"

        steps:
          # 2–3 messages; social proof / validation

      - code: "D3"
        title: "<Day 3 title>"
        meta:  "<Day 3 purpose and start timing>"

        steps:
          # Discount reveal + final push

    summary_stats:
      - label: "Total Steps"
        value: "<computed>"
      - label: "Decision Points"
        value: "1"
      - label: "Days Active"
        value: "4"
      - label: "Primary Goal"
        value: "<primary_goal>"

  # Repeat for each journey requested, adjusting meta, segments and focus
```

You must output this `CONFIG` YAML first, then the deliverables.

---

## 2. DELIVERABLE 1: JOURNEY MARKDOWN DOCUMENTS (.md)

For each journey in `JOURNEYS`, create a separate Markdown section or file spec with:

* Journey name and goal.
* Table or bullet list for every step including:
  * Step number, day code (D0–D3).
  * Message type (BROADCAST/CONVERSATIONAL).
  * Full message copy (≤200 chars body, respecting header/footer limits).
  * Button text (≤20 chars; 3 options only where interactive).
  * Exact timing (relative to previous step).
  * Auto-reply copy for each interactive button (with links).
  * Tags to apply.
  * Asset requirements (image, caption, alt text).
  * Product / benefit links.
  * Node IDs for WATI (you invent a consistent, human-readable convention).

Use this general format:

```markdown
# Journey 1 – <Journey label>

## Overview

- Goal: <primary_goal>
- Entry: <meta.entry>
- Target: <meta.target>
- Duration: <GLOBAL.duration_label>

## Steps

### Day 0 – <Day 0 title> (<Day 0 meta>)

**Step 1 (D0-S1)** – <Step title>  
- Type: BROADCAST  
- Timing: <timing>  
- Message body (≤200 chars):  
  "<copy>"  
- Footer (if used, ≤60 chars):  
  "Type STOP to opt-out"  
- Buttons: _(if any)_  
- Tags: [tag_1, tag_2]  
- Assets: [image / none] (caption, alt text)  
- WATI Node ID: `journey1_d0_s1_welcome`

...and so on for all steps, including auto-replies for each interactive button.
```

Respect all WATI limits and brand voice.

---

## 3. DELIVERABLE 2A: SUMMARY WORKFLOW HTML

Create a single HTML `<html>...</html>` document that provides a high-level overview of the journey.

**CRITICAL DESIGN REQUIREMENTS:**
* Use a **maximum of 3 colors** with 20% tint variations for visual separation
* **NO emojis or icons** anywhere in the HTML
* **NO implementation notes section**
* Clean, professional design with clear visual hierarchy

**REQUIRED SECTIONS:**

1. **Campaign Strategy**
   * Journey title and description
   * Key metrics cards showing:
     * Total Days
     * Total Messages
     * Interactive Messages
     * Total Duration (hours)

2. **Journey Timeline**
   * Day-by-day breakdown with:
     * Day headers (e.g., "DAY 0: Immediate Engagement")
     * Step cards showing:
       * Step title
       * Step type (Broadcast/Template or Conversational)
       * Timing (e.g., "IMMEDIATE", "+30 seconds", "+24 hours")
       * Brief description of step purpose
     * Visual flow indicators (arrows, connectors)
     * Wait times between steps clearly marked

3. **Core Principles**
   * List of 4-6 core principles that guide the journey
   * Each principle in a card format with brief description

4. **Assets Required for Journey**
   * Organized by day (Day 0, Day 1, etc.)
   * For each asset:
     * Asset name/description
     * Which step it's used in
     * Asset specifications (format, size, dimensions if applicable)

5. **URLs Used for Journey**
   * List all URLs used throughout the journey
   * For each URL:
     * The URL itself
     * Which steps use this URL
     * Purpose (e.g., "Product page", "Demo booking", "Testimonials")

6. **Discounts Used for Journey**
   * List any discount codes or offers
   * Discount details (amount, code, validity)
   * Which steps mention the discount

**STYLING:**
* Use brand colors from `CONFIG.GLOBAL.brand_colours` (max 3 colors)
* Apply 20% opacity variations (e.g., rgba with 0.2, 0.4, 0.6, 0.8) for visual separation
* White content blocks on light background
* Clear borders and spacing
* Professional, clean layout

---

## 4. DELIVERABLE 2B: FULL DETAIL WORKFLOW HTML

Create a single HTML `<html>...</html>` document that shows the complete detailed journey.

**CRITICAL DESIGN REQUIREMENTS:**
* Use a **maximum of 3 colors** with 20% tint variations for visual separation
* **NO emojis or icons** anywhere in the HTML
* **NO implementation notes section**
* Complete step-by-step breakdown with all message copy

**REQUIRED SECTIONS:**

1. **Journey Header**
   * Journey title
   * Subtitle: "Complete Detailed Visual Journey"
   * Key metrics:
     * Total Messages
     * Interactive Messages
     * Total Days
     * Total Hours

2. **Day-by-Day Detailed Breakdown**
   For each day (Day 0, Day 1, Day 2, etc.):
   
   * **Day Header**
     * Day name and purpose (e.g., "DAY 0: Immediate Engagement")
     * Duration indicator
   
   * **Step Cards** (for each step):
     * Step number and title
     * Send timing (e.g., "SEND AT: 0 hours", "SEND AT: Day 1")
     * Message type (Broadcast/Template or Conversational)
     * **Full message copy** (header, body, footer if applicable)
     * **Buttons/Quick Replies** with:
       * Button text
       * **Links/URLs** clearly displayed
       * Destination URLs
     * **Call-to-Actions** clearly marked with:
       * CTA text
       * **Full URL** displayed
       * Purpose (e.g., "Book a Demo", "Learn More")
     * **Media/Assets**:
       * Asset name
       * Caption if applicable
       * Alt text
     * **Auto-Reply Sections** (if interactive):
       * Which button triggers this auto-reply
       * Auto-reply message copy
       * Links in auto-reply
       * Wait time after auto-reply
     * **Conditional Logic** (if applicable):
       * Conditions clearly stated
       * Branch paths shown
     * **Wait Time** to next step

3. **Complete Journey Summary**
   * Summary metrics:
     * Total Messages (per user)
     * Interactive Messages (per user)
     * Total Days (per user)
     * Total Hours (per user)
     * Total Steps (per user)
   * Key Learnings (bullet points about journey structure)
   * **DO NOT include "Ready for Implementation" section**

**STYLING:**
* Use brand colors from `CONFIG.GLOBAL.brand_colours` (max 3 colors)
* Apply 20% opacity variations for visual separation
* Color-coded step types:
  * Standard messages (primary color)
  * Decision points (accent color)
  * Conversion steps (conversion color)
* White content blocks on light background
* Clear visual flow with connectors and arrows
* Professional, clean layout

**IMPORTANT:**
* Ensure all **buttons have their links/URLs clearly displayed**
* Ensure all **call-to-actions show the full URL** they link to
* Ensure all **assets are listed** with their usage context
* Ensure **conditional logic and branches** are clearly visualized

---

## 7. OUTPUT ORDER

When you respond:

1. Output the **`CONFIG` YAML** first.
2. Then:
   * Journey Markdown specs.
   * Summary Workflow HTML.
   * Full Detail Workflow HTML.

Keep each HTML deliverable clearly separated with headings:

```text
=== CONFIG YAML ===

...yaml...

=== JOURNEY MARKDOWN DOCUMENTS ===

...markdown...

=== HTML A – SUMMARY WORKFLOW ===

...html...

=== HTML B – FULL DETAIL WORKFLOW ===

...html...
```

Ensure:

* All messages respect WATI limits.
* All journeys follow Day 0–3 structure and timings.
* Brand voice and compliance constraints are honoured.
"""
    
    # Format the prompt with actual values
    unique_selling_points_str = '\n'.join(f"- {item}" for item in get_list('unique_selling_points')) or "- (Not specified)"
    urls_list = []
    if get_value('url_homepage'):
        urls_list.append(f"- Homepage: {get_value('url_homepage')}")
    urls_list.extend([f"- {url}" for url in get_list('url_product_pages')])
    urls_list.extend([f"- {url}" for url in get_list('url_offer_pages')])
    urls_str = '\n'.join(urls_list) if urls_list else "- (Not specified)"
    
    products_str = '\n'.join(f"- {item}" for item in get_list('products')) or "- (Not specified)"
    testimonials_str = '\n'.join(f"- {url}" for url in get_list('url_testimonials')) or "- (Not specified)"
    brand_attributes_str = '\n'.join(f"- {item}" for item in get_list('brand_attributes')) or "- (Not specified)"
    
    return prompt.format(
        platform=get_value('platform', 'WATI (WhatsApp marketing automation)'),
        format=get_value('format', 'B2C consumer acquisition journeys'),
        duration_overall=get_value('duration_overall', '3 days + initial Day 0 (0-3 hours)'),
        discount=get_value('discount', ''),
        brand_name=get_value('brand_name', ''),
        industry=get_value('industry', ''),
        unique_selling_points=unique_selling_points_str,
        brand_tone=get_value('brand_tone', ''),
        brand_colours=get_value('brand_colours', ''),
        urls=urls_str,
        products=products_str,
        offer_text=get_value('offer_text', ''),
        quote_code=get_value('quote_code', ''),
        testimonials=testimonials_str,
        audience=get_value('audience', ''),
        compliance=get_value('compliance', ''),
        num_journeys=get_value('num_journeys', '1'),
        deliverables=get_value('deliverables', 'Journeys: 1. Deliverables: 1, 2A, 2B'),
        day0_duration=get_value('day0_duration', '0-3 hours'),
        day0_step1_timing=get_value('day0_step1_timing', 'Immediate'),
        day0_step2_timing=get_value('day0_step2_timing', '+30 minutes'),
        day0_step3_timing=get_value('day0_step3_timing', '+2 hours'),
        day1_start=get_value('day1_start', '+24 hours'),
        day2_start=get_value('day2_start', '+24 hours'),
        day3_start=get_value('day3_start', '+24 hours'),
        final_push_timing=get_value('final_push_timing', '+3 hours'),
        urgency_level=get_value('urgency_level', 'medium'),
        journey_exceptions=get_value('journey_exceptions', ''),
        sophistication_level=get_value('sophistication_level', '7'),
        tone=get_value('tone', 'professional'),
        emoji_usage=get_value('emoji_usage', 'minimal'),
        brand_attributes=brand_attributes_str,
        language_to_avoid=get_value('language_to_avoid', '')
    )

