# REUSABLE PROMPT: WhatsApp Journey Generator

Copy this prompt to recreate similar journey visualizations in future chats.

---

## 📋 THE COMPLETE PROMPT

```
I need you to create complete WhatsApp marketing journeys with comprehensive visualizations.

CONTEXT:
- Platform: WATI (WhatsApp marketing automation)
- Format: B2C consumer acquisition journeys
- Duration: 3 days + initial Day 0 (0-3 hours)
- Discount: [YOUR DISCOUNT CODE & PERCENTAGE]
- Brand: [YOUR BRAND NAME]
- Products: [LIST YOUR PRODUCTS]

brand name is police friendly and they offer financial services products for the uk police force.
This is there about us website: https://policefriendly.org.uk/why-policefriendly
I would recommend this being a 2 day journey. Initial onboarding when they become a lead. They will become a lead either on the website or via meta lead form.
We want to look at only the following 1 products for the journey. 
This needs to be the lifetime isa product:
https://www.metfriendly.org.uk/save-regularly/lifetime-isa/ have also attached the product information
This is the application form for the lifetime isa:
https://www.metfriendly.org.uk/save-regularly/lifetime-isa/lifetime-isa-application-form/?hsCtaAttrib=191206193974
This is the offer for the lifetime isa:
Special Offer: Receive a £50 Amazon.co.uk Gift Card when you open a new Lifetime ISA by 19th December 2025.
Quote code: Autumn25. this code can be used in a whatsapp message as a coupon.
continue with the generation but only 1 journey and only for this product.
Brand and tone of voice remain the same
Each journey should focus on people getting a quote. they need to do to this page on the website for each product to fill in an application:
Brand voice, use content this web page to understand tone of voice: https://www.metfriendly.org.uk/why-metfriendly/what-is-a-friendly-society/ and this https://policefriendly.org.uk/why-policefriendly
No emojis.
There are testimonials are herE: https://www.metfriendly.org.uk/why-metfriendly/testimonials/
Use these brand colours from this website: https://policefriendly.org.uk/


DELIVERABLES NEEDED:

1. JOURNEY MARKDOWN DOCUMENTS (.md files)
   Create [NUMBER] complete journey documents, each including:
   - Complete message copy for every step
   - Character counts (max 200 chars per message body)
   - Button text (max 20 chars per button)
   - Exact timing and delays between messages
   - Message type specified (Broadcast/Template or Conversational)
   - Auto-reply copy for each interactive button option
   - Tag structure for tracking
   - Asset requirements (images needed)
   - Product/benefit page links
   - Node IDs for WATI implementation

2. HTML VISUALIZATIONS (3 types)

   A) FULL DETAILED VISUALIZATION
   - Tabbed interface to switch between journeys
   - Complete message copy displayed in cards
   - All button specifications and destinations
   - All timing/delays clearly shown
   - Auto-reply sections visible after interactive buttons
   - Character counts for each message
   - Tags and assets listed
   - Day-by-day breakdown
   - Color-coded message types
   - Styled with brand colors (if provided)
   
   B) WORKFLOW OVERVIEW (Structure Only - No Detailed Copy)
   - Clean visual timeline for each journey
   - Step cards showing: title, type, timing
   - Color-coded elements:
     * Blue = Standard messages (or your primary color)
     * Orange = Decision points (or your accent color)
     * Green = Conversion steps (or your secondary color)
   - Personalization branches clearly marked
   - Journey summary stats (steps, duration, key metrics)
   - Perfect for strategy reviews and presentations
   - Styled with brand colors (if provided)
   
   C) COMPARISON SUMMARY
   - Side-by-side journey comparison cards
   - Comparison table with all features
   - Common elements across journeys
   - Implementation checklist
   - Styled with brand colors (if provided)

3. JOURNEY STRUCTURE REQUIREMENTS

   TIMELINE CUSTOMIZATION:
   Specify your preferred timeline:
   - Day 0 duration: [e.g., 0-3 hours, 0-2 hours, 0-4 hours]
   - Day 0 Step 1 timing: [e.g., Immediate]
   - Day 0 Step 2 timing: [e.g., +30 minutes, +1 hour]
   - Day 0 Step 3 timing: [e.g., +2 hours, +90 minutes]
   - Day 1 start: [e.g., +24 hours, +12 hours, +48 hours from Day 0]
   - Day 2 start: [e.g., +24 hours, +12 hours from Day 1]
   - Day 3 start: [e.g., +24 hours, +12 hours from Day 2]
   - Final push timing: [e.g., +3 hours, +2 hours after discount reveal]

   Each journey must follow this structure:
   
   DAY 0 ([YOUR SPECIFIED DURATION]):
   - Step 1: Welcome message ([YOUR TIMING - e.g., immediate])
   - Step 2: Benefits/info message ([YOUR TIMING - e.g., +30 minutes])
   - Step 3: Interactive buttons question ([YOUR TIMING - e.g., +2 hours])
     * MUST have 3 button options
     * Each button triggers unique auto-reply
     * Auto-replies include benefit-specific links
   
   DAY 1 ([YOUR TIMING] from Day 0):
   - Educational content (varies by button selection)
   - 1-2 messages
   
   DAY 2 ([YOUR TIMING] from Day 1):
   - Social proof / validation
   - 2-3 messages
   
   DAY 3 ([YOUR TIMING] from Day 2):
   - Discount reveal (Limited Time Offer template)
   - Final push message ([YOUR TIMING] after discount)
   - All journeys use same discount code
   - [YOUR SPECIFIED] urgency on discount

4. WATI PLATFORM COMPLIANCE

   All messages must comply with WATI limits:
   - Message body: Maximum 200 characters
   - Button text: Maximum 20 characters
   - Header text: Maximum 60 characters
   - Footer text: Maximum 60 characters
   - Interactive buttons: 3 options per question
   - Delays: 3 seconds before follow-up messages
   - First message footer: "Type STOP to opt-out"
   
   MESSAGE TYPE RULES (CRITICAL):
   Use BROADCAST/TEMPLATE message when:
   - It is the FIRST message in the journey (Day 0, Step 1)
   - OR when the message is sent 24+ hours after the last message
   
   Use CONVERSATIONAL message when:
   - Message is sent within 24 hours of the previous message
   - Follow-up messages in same day sequence
   
   Examples:
   - Day 0 Step 1 (immediate) = BROADCAST (first message)
   - Day 0 Step 2 (+30 min) = CONVERSATIONAL (within 24hrs)
   - Day 0 Step 3 (+2 hours) = CONVERSATIONAL (within 24hrs)
   - Day 1 Step 1 (+24 hours) = BROADCAST (24+ hours gap)
   - Day 1 Step 2 (+2 hours) = CONVERSATIONAL (within 24hrs)
   - Day 2 Step 1 (+24 hours) = BROADCAST (24+ hours gap)
   - Day 3 Step 1 (+24 hours) = BROADCAST (24+ hours gap)

5. PERSONALIZATION REQUIREMENTS

   - Each journey has 1 decision point (Step 3 on Day 0)
   - 3 interactive button options at decision point
   - Each button triggers unique auto-reply with:
     * Personalized message copy
     * Relevant benefit-specific link
     * Image with caption
     * Appropriate tags
   - Day 1 content varies based on selection

6. BRAND VOICE GUIDELINES

   Maintain consistent brand voice:
   - Sophistication level: [SPECIFY 1-10, where 10 is most formal]
   - Tone: [warm/professional/clinical/friendly/etc]
   - Emoji usage: [minimal/strategic/frequent]
   - Key brand attributes: [LIST YOUR BRAND KEYWORDS]
   - Language to avoid: [SPECIFY IF ANY]

---

MY SPECIFIC DETAILS:

TIMELINE SPECIFICATIONS:
Day 0 duration: [e.g., 0-3 hours]
Day 0 Step 1 timing: [e.g., Immediate]
Day 0 Step 2 timing: [e.g., +30 minutes]
Day 0 Step 3 timing: [e.g., +2 hours]
Day 1 start: [e.g., +24 hours from Day 0]
Day 2 start: [e.g., +24 hours from Day 1]
Day 3 start: [e.g., +24 hours from Day 2]
Final push timing: [e.g., +3 hours after discount reveal]
Discount urgency: [e.g., 48 hours]

BRAND INFORMATION:
Brand Name: [Your brand name]
Industry: [Your industry]
Unique Selling Points: [What makes you different]

PRODUCTS & JOURNEY DETAILS:

Journey 1: [Product Name or Focus - e.g., "Brand Introduction"]
- Entry point: [Where users come from - e.g., "Facebook ads, Instagram"]
- Target audience: [Who they are - e.g., "First-time visitors, ages 25-45"]
- Journey goal: [What you want - e.g., "Convert to any product purchase"]
- Unique focus: [What to emphasize - e.g., "Brand values and product range"]
- Personalization options:
  * Button 1: [e.g., "Anti-Aging ✨"]
  * Button 2: [e.g., "Acne Treatment 💎"]
  * Button 3: [e.g., "Wellness 🧘"]

Journey 2: [Product/Focus]
- Entry point: [Source]
- Target audience: [Description]
- Journey goal: [Objective]
- Unique focus: [What to emphasize]
- Personalization options:
  * Button 1: [Option]
  * Button 2: [Option]
  * Button 3: [Option]

Journey 3: [Product/Focus]
- Entry point:
- Target audience:
- Journey goal:
- Unique focus:
- Personalization options:
  * Button 1:
  * Button 2:
  * Button 3:

Journey 4: [Product/Focus]
- Entry point:
- Target audience:
- Journey goal:
- Unique focus:
- Personalization options:
  * Button 1:
  * Button 2:
  * Button 3:

DISCOUNT & OFFER DETAILS:
- Discount code: [YOUR_CODE]
- Discount value: [PERCENTAGE]%
- Offer validity: [NUMBER] hours
- Offer reveal: Day 3
- Urgency messaging: [Preferred urgency language]

PRODUCT LINKS:
Main product pages:
- Product 1: [Full URL]
- Product 2: [Full URL]
- Product 3: [Full URL]
- Product 4: [Full URL]

Benefit-specific pages (if available):
- Anti-aging/wrinkles: [URL or "not available"]
- Acne/clarity: [URL or "not available"]
- Wellness/mood: [URL or "not available"]
- Other benefit: [URL or "not available"]

BRAND VOICE SPECIFICATIONS:
- Sophistication level: [1-10]
- Overall tone: [Description - e.g., "Professional yet approachable"]
- Key brand attributes: [e.g., "Swiss-engineered, clinical-grade, premium"]
- Emoji strategy: [e.g., "Strategic use only - ✨💎🧘⚡"]
- Language to include: [Specific terms to use]
- Language to avoid: [Specific terms to avoid]

BRAND COLORS FOR HTML VISUALIZATIONS:
Primary color: [HEX code - e.g., #667eea]
Secondary color: [HEX code - e.g., #764ba2]
Accent color: [HEX code - e.g., #10b981]
Background gradient start: [HEX code - optional]
Background gradient end: [HEX code - optional]
Text color (dark): [HEX code - e.g., #2c3e50]
Text color (light): [HEX code - e.g., #5a6c7d]

Note: If you don't have specific brand colors, Claude will use default professional colors.

SPECIAL REQUIREMENTS:
- [Any specific requirements for messaging]
- [Character limits or special constraints]
- [Compliance requirements]
- [Specific features to highlight per journey]
- [Any content to avoid]

ADDITIONAL CONTEXT:
[Add any other relevant information about your brand, audience, or goals]

---

WORKFLOW INSTRUCTIONS:

Please create the journeys systematically:
1. Start with Journey 1 markdown document
2. Then Journey 2, 3, and 4 markdown documents
3. Create all 3 HTML visualizations
4. Create master summary document
5. Provide update confirmations

After delivery, I may request:
- Copy refinements
- Link updates
- Timing adjustments
- Additional steps
- HTML regeneration

---

## HTML VISUALIZATION SPECIFICATIONS

CRITICAL: You MUST generate exactly TWO HTML files with the exact structure, styling, and all required elements specified below. Do not omit any sections, cards, or styling elements.

### FILE 1: workflow_overview.html

PURPOSE: High-level strategy visualization showing journey structure, timing, and flow without detailed message copy.

REQUIRED STRUCTURE (ALL ELEMENTS MUST BE INCLUDED):

1. **HTML HEADER** (Required):
   - DOCTYPE, html lang="en", meta charset, viewport
   - Title: "[Journey Name] - Workflow Overview"
   - Complete CSS stylesheet in <style> tag (see CSS below)

2. **BODY STRUCTURE** (Required - ALL sections):
   - Container div with max-width: 1200px
   - Header section with:
     * h1: Journey name
     * Subtitle: "Strategy & Structure Visualization - [Brand Name]"
     * journey-stats grid with 5 stat-boxes showing:
       - Days (number)
       - Steps (number)
       - Decision Points (number)
       - Segments (number)
       - Duration (e.g., "27h")
   - timeline-container section
   - For EACH day:
     * day-section div
     * day-header with day-title and day-duration
     * step-timeline div with step-timeline::before pseudo-element
     * For EACH step:
       - step-card div with appropriate class (broadcast, conversational, decision, conversion)
       - step-header with step-number, step-title, step-badges
       - step-content with purpose, content summary, next timing
       - If decision point: decision-branches section with branch-options grid
   - key-metrics section with 4 metric-card divs:
     * Expected Open Rate
     * Button Click Rate
     * Application Start
     * Completion Rate
   - legend section with legend-items showing all message types
   - footer with brand info and offer details

3. **REQUIRED CSS STYLES** (Copy exactly, adapt colors to brand):

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, rgb(233, 233, 233) 0%, rgb(213, 213, 213) 100%);
    padding: 40px 20px;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

header {
    background: linear-gradient(135deg, rgb(49, 88, 145) 0%, rgb(37, 66, 109) 100%);
    color: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin-bottom: 40px;
}

h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-weight: 600;
}

.subtitle {
    font-size: 1.2em;
    opacity: 0.95;
}

.journey-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-top: 25px;
}

.stat-box {
    background: rgba(255,255,255,0.15);
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}

.stat-number {
    font-size: 2em;
    font-weight: bold;
    display: block;
}

.stat-label {
    font-size: 0.9em;
    opacity: 0.9;
    margin-top: 5px;
}

.timeline-container {
    background: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.day-section {
    margin-bottom: 50px;
}

.day-header {
    background: linear-gradient(135deg, rgb(49, 88, 145) 0%, rgb(37, 66, 109) 100%);
    color: white;
    padding: 20px 30px;
    border-radius: 10px;
    margin-bottom: 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.day-title {
    font-size: 1.8em;
    font-weight: 600;
}

.day-duration {
    font-size: 1em;
    opacity: 0.9;
    background: rgba(255,255,255,0.2);
    padding: 8px 16px;
    border-radius: 20px;
}

.step-timeline {
    position: relative;
    padding-left: 60px;
}

.step-timeline::before {
    content: '';
    position: absolute;
    left: 20px;
    top: 0;
    bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, rgb(49, 88, 145) 0%, rgb(212, 68, 55) 100%);
}

.step-card {
    position: relative;
    margin-bottom: 30px;
    background: #f8f9fa;
    border-radius: 10px;
    padding: 25px;
    border: 2px solid #e9ecef;
    transition: all 0.3s ease;
}

.step-card:hover {
    transform: translateX(5px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.step-card::before {
    content: '';
    position: absolute;
    left: -47px;
    top: 28px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: white;
    border: 4px solid rgb(49, 88, 145);
    box-shadow: 0 0 0 4px white;
}

.step-card.broadcast::before {
    border-color: rgb(212, 68, 55);
}

.step-card.decision::before {
    border-color: rgb(255, 165, 0);
    width: 18px;
    height: 18px;
    left: -49px;
    top: 26px;
}

.step-card.conversion::before {
    border-color: rgb(34, 139, 34);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}

.step-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    flex-wrap: wrap;
    gap: 10px;
}

.step-number {
    background: rgb(49, 88, 145);
    color: white;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.1em;
}

.step-title {
    flex: 1;
    font-size: 1.3em;
    font-weight: 600;
    color: rgb(49, 88, 145);
    margin-left: 15px;
}

.step-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.badge {
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 0.8em;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-broadcast {
    background: rgba(212, 68, 55, 0.1);
    color: rgb(212, 68, 55);
    border: 1px solid rgb(212, 68, 55);
}

.badge-conversational {
    background: rgba(49, 88, 145, 0.1);
    color: rgb(49, 88, 145);
    border: 1px solid rgb(49, 88, 145);
}

.badge-timing {
    background: rgba(108, 117, 125, 0.1);
    color: #495057;
    border: 1px solid #6c757d;
}

.step-content {
    margin-top: 15px;
    color: #495057;
    line-height: 1.8;
}

.step-content p {
    margin-bottom: 10px;
}

.step-content strong {
    color: #212529;
}

.decision-branches {
    margin-top: 20px;
    padding: 20px;
    background: rgba(255, 165, 0, 0.05);
    border: 2px solid rgba(255, 165, 0, 0.3);
    border-radius: 8px;
}

.branch-title {
    font-weight: 600;
    color: rgb(255, 140, 0);
    margin-bottom: 12px;
    font-size: 1.1em;
}

.branch-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}

.branch-option {
    background: white;
    padding: 12px;
    border-radius: 6px;
    border-left: 3px solid rgb(255, 165, 0);
    font-size: 0.95em;
}

.key-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 40px 0;
}

.metric-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    border: 2px solid #e9ecef;
    text-align: center;
}

.metric-card h3 {
    color: rgb(49, 88, 145);
    margin-bottom: 15px;
    font-size: 1.2em;
}

.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    color: rgb(212, 68, 55);
    margin: 10px 0;
}

.metric-label {
    color: #6c757d;
    font-size: 0.95em;
}

.legend {
    background: white;
    padding: 25px;
    border-radius: 12px;
    margin-top: 40px;
    border: 2px solid #e9ecef;
}

.legend-title {
    font-size: 1.3em;
    color: rgb(49, 88, 145);
    margin-bottom: 20px;
    font-weight: 600;
}

.legend-items {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 12px;
}

.legend-dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    flex-shrink: 0;
}

.legend-dot.broadcast {
    background: rgb(212, 68, 55);
    border: 3px solid rgba(212, 68, 55, 0.3);
}

.legend-dot.conversational {
    background: rgb(49, 88, 145);
    border: 3px solid rgba(49, 88, 145, 0.3);
}

.legend-dot.decision {
    background: rgb(255, 165, 0);
    border: 3px solid rgba(255, 165, 0, 0.3);
}

.legend-dot.conversion {
    background: rgb(34, 139, 34);
    border: 3px solid rgba(34, 139, 34, 0.3);
}

.legend-text {
    font-size: 0.95em;
    color: #495057;
}

footer {
    margin-top: 60px;
    text-align: center;
    color: #6c757d;
    font-size: 0.9em;
}
```

4. **REQUIRED CONTENT ELEMENTS** (MUST include all):
   - Header with journey name and stats (5 stat boxes)
   - Every day section with header and duration
   - Every step card with: number, title, badges, purpose, content summary, next timing
   - Decision branches section for interactive steps (if applicable)
   - Key metrics section (4 metric cards minimum)
   - Legend section (all message types)
   - Footer with brand and offer info

---

### FILE 2: full_detailed.html

PURPOSE: Complete implementation guide with full message copy, character counts, tags, assets, and all technical details.

⚠️ **CRITICAL**: You MUST use the EXACT CSS classes, structure, and HTML format shown below. Do NOT create your own CSS classes or structure. Copy the CSS exactly and use the exact HTML structure pattern provided.

REQUIRED STRUCTURE (ALL ELEMENTS MUST BE INCLUDED):

1. **HTML HEADER** (Required):
   - DOCTYPE, html lang="en", meta charset, viewport
   - Title: "[Journey Name] WhatsApp Journey (Full Detail)"
   - Complete CSS stylesheet in <style> tag (see CSS below)

2. **BODY STRUCTURE** (Required - ALL sections):
   - Container div with max-width: 1400px
   - Header section with:
     * h1: Journey name
     * Subtitle: "Complete Implementation Guide - [Brand Name]"
     * journey-meta grid with 6+ meta-item divs showing:
       - Duration
       - Total Messages
       - Offer
       - Code
       - Valid Until
       - Decision Points
   - content section
   - For EACH day:
     * day-section div
     * day-header with day-title and day-duration
     * For EACH step:
       - step-card div with class (broadcast, conversational, interactive)
       - step-header with step-title and step-badges
       - step-info grid with: Timing, Delay Before Next, Message Type
       - message-content section with:
         * message-section for Header Text (if applicable)
         * message-section for Body Copy (REQUIRED)
         * message-section for Footer Text (if applicable)
         * message-section for Image Caption (if applicable)
         * Each message-text div MUST include char-count span
       - If interactive: button-group with button-item divs
       - If auto-reply: auto-reply-card section
       - tags-section with tag spans (REQUIRED for every step)
       - assets-section with asset-item divs (REQUIRED for every step)
   - flow-diagram section with flow-content (ASCII diagram)
   - summary-grid with 4 summary-card divs:
     * Journey Metrics
     * Technical Setup
     * Product Details
     * Campaign Offer
   - footer with brand info

3. **REQUIRED CSS STYLES** (Copy exactly, adapt colors to brand):

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, rgb(233, 233, 233) 0%, rgb(213, 213, 213) 100%);
    padding: 40px 20px;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

header {
    background: linear-gradient(135deg, rgb(49, 88, 145) 0%, rgb(37, 66, 109) 100%);
    color: white;
    padding: 40px;
    border-radius: 15px 15px 0 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-weight: 600;
}

.subtitle {
    font-size: 1.2em;
    opacity: 0.95;
    margin-bottom: 30px;
}

.journey-meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 25px;
}

.meta-item {
    background: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid rgb(212, 68, 55);
}

.meta-label {
    font-size: 0.9em;
    opacity: 0.9;
    margin-bottom: 5px;
}

.meta-value {
    font-size: 1.1em;
    font-weight: 600;
}

.content {
    background: white;
    padding: 40px;
    border-radius: 0 0 15px 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.day-section {
    margin-bottom: 60px;
}

.day-header {
    background: linear-gradient(135deg, rgb(49, 88, 145) 0%, rgb(37, 66, 109) 100%);
    color: white;
    padding: 20px 30px;
    border-radius: 10px;
    margin-bottom: 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.day-title {
    font-size: 1.8em;
    font-weight: 600;
}

.day-duration {
    font-size: 1em;
    opacity: 0.9;
    background: rgba(255,255,255,0.2);
    padding: 8px 16px;
    border-radius: 20px;
}

.step-card {
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 25px;
    position: relative;
    transition: all 0.3s ease;
}

.step-card:hover {
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.step-card.broadcast {
    border-left: 6px solid rgb(212, 68, 55);
}

.step-card.conversational {
    border-left: 6px solid rgb(49, 88, 145);
}

.step-card.interactive {
    border-left: 6px solid rgb(255, 165, 0);
}

.step-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 15px;
}

.step-title {
    font-size: 1.5em;
    color: rgb(49, 88, 145);
    font-weight: 600;
    flex: 1;
}

.step-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.badge {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-broadcast {
    background: rgba(212, 68, 55, 0.1);
    color: rgb(212, 68, 55);
    border: 1px solid rgb(212, 68, 55);
}

.badge-conversational {
    background: rgba(49, 88, 145, 0.1);
    color: rgb(49, 88, 145);
    border: 1px solid rgb(49, 88, 145);
}

.badge-timing {
    background: rgba(108, 117, 125, 0.1);
    color: #495057;
    border: 1px solid #6c757d;
}

.step-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
    padding: 20px;
    background: white;
    border-radius: 8px;
}

.info-item {
    display: flex;
    flex-direction: column;
}

.info-label {
    font-size: 0.85em;
    color: #6c757d;
    margin-bottom: 5px;
    font-weight: 600;
}

.info-value {
    font-size: 1em;
    color: #212529;
    font-weight: 500;
}

.message-content {
    margin-top: 20px;
}

.message-section {
    margin-bottom: 20px;
}

.section-label {
    font-size: 0.9em;
    color: rgb(49, 88, 145);
    font-weight: 600;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.message-text {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #dee2e6;
    font-size: 1.05em;
    line-height: 1.6;
    position: relative;
}

.char-count {
    position: absolute;
    top: 8px;
    right: 12px;
    font-size: 0.75em;
    color: #6c757d;
    background: rgba(233, 233, 233, 0.8);
    padding: 4px 8px;
    border-radius: 4px;
}

.char-count.warning {
    color: rgb(212, 68, 55);
    background: rgba(212, 68, 55, 0.1);
}

.button-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 15px;
}

.button-item {
    background: rgb(49, 88, 145);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    text-align: center;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.button-text {
    flex: 1;
}

.button-dest {
    font-size: 0.85em;
    opacity: 0.9;
    background: rgba(255,255,255,0.2);
    padding: 4px 10px;
    border-radius: 4px;
}

.auto-reply-card {
    background: rgba(255, 165, 0, 0.05);
    border: 2px solid rgba(255, 165, 0, 0.3);
    border-radius: 10px;
    padding: 20px;
    margin-top: 15px;
}

.auto-reply-header {
    color: rgb(255, 140, 0);
    font-weight: 600;
    margin-bottom: 10px;
    font-size: 1.1em;
}

.tags-section {
    margin-top: 25px;
    padding: 15px;
    background: rgba(49, 88, 145, 0.05);
    border-radius: 8px;
}

.tag {
    display: inline-block;
    background: rgb(49, 88, 145);
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.85em;
    margin: 4px;
}

.assets-section {
    margin-top: 20px;
    padding: 15px;
    background: rgba(212, 68, 55, 0.05);
    border-radius: 8px;
}

.asset-item {
    padding: 8px 0;
    border-bottom: 1px dashed #dee2e6;
}

.asset-item:last-child {
    border-bottom: none;
}

.flow-diagram {
    background: white;
    padding: 30px;
    border-radius: 12px;
    margin: 40px 0;
    border: 2px solid #e9ecef;
}

.flow-title {
    font-size: 1.5em;
    color: rgb(49, 88, 145);
    margin-bottom: 20px;
    font-weight: 600;
}

.flow-content {
    font-family: 'Courier New', monospace;
    font-size: 0.95em;
    line-height: 1.8;
    color: #495057;
    white-space: pre;
    overflow-x: auto;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.summary-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    border: 2px solid #e9ecef;
}

.summary-card h3 {
    color: rgb(49, 88, 145);
    margin-bottom: 15px;
    font-size: 1.3em;
}

.summary-card ul {
    list-style: none;
    padding-left: 0;
}

.summary-card li {
    padding: 8px 0;
    border-bottom: 1px dashed #dee2e6;
}

.summary-card li:last-child {
    border-bottom: none;
}

.summary-card li::before {
    content: "✓ ";
    color: rgb(212, 68, 55);
    font-weight: bold;
    margin-right: 8px;
}

footer {
    margin-top: 60px;
    text-align: center;
    color: #6c757d;
    font-size: 0.9em;
}

@media print {
    body {
        background: white;
    }
    .step-card {
        page-break-inside: avoid;
    }
}
```

4. **EXACT HTML STRUCTURE EXAMPLE** (Copy this pattern exactly):

```html
<!-- STEP EXAMPLE - Use this exact structure for every step -->
<div class="step-card broadcast">
    <div class="step-header">
        <div class="step-title">Step 1: Welcome Message</div>
        <div class="step-badges">
            <span class="badge badge-broadcast">Broadcast</span>
            <span class="badge badge-timing">Immediate</span>
        </div>
    </div>

    <div class="step-info">
        <div class="info-item">
            <div class="info-label">Timing</div>
            <div class="info-value">Immediate upon subscription</div>
        </div>
        <div class="info-item">
            <div class="info-label">Delay Before Next</div>
            <div class="info-value">30 minutes</div>
        </div>
        <div class="info-item">
            <div class="info-label">Message Type</div>
            <div class="info-value">BROADCAST/TEMPLATE</div>
        </div>
    </div>

    <div class="message-content">
        <div class="message-section">
            <div class="section-label">Header Text</div>
            <div class="message-text">
                <span class="char-count">26/60</span>
                Welcome to Police Friendly
            </div>
        </div>

        <div class="message-section">
            <div class="section-label">Body Copy</div>
            <div class="message-text">
                <span class="char-count">196/200</span>
                Thank you for your interest in our Lifetime ISA. We're a member-owned friendly society supporting the Police Family since 1893. No shareholders. No commission. Just your financial future.
            </div>
        </div>

        <div class="message-section">
            <div class="section-label">Footer Text</div>
            <div class="message-text">
                <span class="char-count">19/60</span>
                Type STOP to opt-out
            </div>
        </div>
    </div>

    <div class="tags-section">
        <div class="section-label">Tags Applied</div>
        <span class="tag">journey:lifetime_isa</span>
        <span class="tag">day:0</span>
        <span class="tag">step:welcome</span>
    </div>

    <div class="assets-section">
        <div class="section-label">Assets Required</div>
        <div class="asset-item">None (text only)</div>
    </div>
</div>
```

**For Interactive Steps with Buttons:**
```html
<div class="message-section">
    <div class="section-label">Interactive Buttons</div>
    <div class="button-group">
        <div class="button-item">
            <span class="button-text">First Home (10 chars)</span>
            <span class="button-dest">→ Step 4a</span>
        </div>
        <div class="button-item">
            <span class="button-text">Retirement Savings (18 chars)</span>
            <span class="button-dest">→ Step 4b</span>
        </div>
    </div>
</div>
```

**For Auto-Reply Steps:**
```html
<div class="auto-reply-card">
    <div class="auto-reply-header">Personalized Response</div>
    <div class="message-section">
        <div class="section-label">Body Copy</div>
        <div class="message-text">
            <span class="char-count">197/200</span>
            Perfect for first-time buyers. Save towards properties up to £450,000...
        </div>
    </div>
</div>
```

5. **REQUIRED CONTENT ELEMENTS** (MUST include all for EVERY step):
   - Header with journey name and meta items (6+ items)
   - Every day section with header
   - Every step card MUST include:
     * step-header with title and badges
     * step-info grid (3 items: Timing, Delay, Message Type)
     * message-content with ALL applicable sections:
       - Header Text (if used) with char-count
       - Body Copy (REQUIRED) with char-count
       - Footer Text (if used) with char-count
       - Image Caption (if used) with char-count
     * button-group (if interactive) with all buttons
     * auto-reply-card (if auto-reply) with full content
     * tags-section (REQUIRED - minimum 3 tags per step)
     * assets-section (REQUIRED - list all assets, use "None" if none)
   - flow-diagram with ASCII flow chart
   - summary-grid with 4 summary cards (all required)
   - Footer

5. **CHARACTER COUNT REQUIREMENTS**:
   - EVERY message-text div MUST have a char-count span
   - Format: `<span class="char-count">XXX/200</span>` or `<span class="char-count warning">XXX/200</span>` if at limit
   - Calculate actual character count and display it
   - Warning class if >= 195 characters

6. **TAGS REQUIREMENTS**:
   - Every step MUST have tags-section
   - Minimum 3 tags per step
   - Format: `journey:[name]`, `day:[number]`, `step:[name]`, plus segment/timing tags as needed

7. **ASSETS REQUIREMENTS**:
   - Every step MUST have assets-section
   - List all required assets (images, graphics, etc.)
   - If none required, show: `<div class="asset-item">None (text only)</div>`
   - Use checkmark (✓) for required assets

---

## CRITICAL OUTPUT REQUIREMENTS

When generating the HTML files:

⚠️ **MOST IMPORTANT**: You MUST use the EXACT CSS classes and HTML structure provided above. DO NOT:
- Create your own CSS classes (like .whatsapp-preview, .msg-bubble, .meta-row, etc.)
- Use different HTML structures (like tabs, different card layouts, etc.)
- Modify the CSS class names
- Use CSS variables or different styling approaches
- Create WhatsApp-style message bubbles or previews

✅ **YOU MUST**:
1. **USE EXACT CSS CLASSES**: Use ONLY the classes defined in the CSS above (.step-card, .step-header, .step-info, .message-content, .message-section, .message-text, .char-count, .tags-section, .assets-section, etc.)
2. **FOLLOW EXACT HTML STRUCTURE**: Use the exact HTML structure pattern shown in the example above
3. **DO NOT OMIT ANY ELEMENTS**: Every section, card, badge, tag, and asset section must be included
4. **COPY CSS EXACTLY**: Copy the CSS styles exactly as provided above (adapt only brand colors in gradients)
5. **INCLUDE ALL STEPS**: Every step from the journey markdown must appear in both HTML files
6. **CHARACTER COUNTS**: Every message must show actual character count in the char-count span (positioned absolutely in top-right)
7. **TAGS FOR EVERY STEP**: No step should be without tags-section with minimum 3 tags
8. **ASSETS FOR EVERY STEP**: No step should be without assets-section (use "None (text only)" if applicable)
9. **COMPLETE STRUCTURE**: Header with journey-meta grid, all days, all steps, flow-diagram, summary-grid, footer - all required
10. **BRAND COLORS**: Adapt ONLY the gradient colors in header and day-header to match brand (if provided)
11. **VALID HTML**: Ensure all HTML is properly closed and valid
12. **NO PLACEHOLDERS**: Use actual content, not placeholder text
13. **STEP-INFO GRID**: Every step MUST have step-info grid with 3 info-item divs (Timing, Delay Before Next, Message Type)
14. **MESSAGE SECTIONS**: Use message-section divs with section-label and message-text divs for each message part

Please begin!
```

---

## 💡 HOW TO USE

1. **Copy the entire prompt** above (everything between the ``` marks)
2. **Replace all [BRACKETED] sections** with your information
3. **Paste into a new Claude chat**
4. **Receive**:
   - 4 complete journey .md files
   - 3 HTML visualizations
   - Master summary
   - Documentation

---

## 📝 EXAMPLE (Déesse PRO)

Here's how we filled it for this project:

```
BRAND INFORMATION:
Brand Name: Déesse PRO
Industry: Premium LED beauty tech
Unique Selling Points: Swiss-engineered, NASA-proven, 30+ years research

TIMELINE CUSTOMIZATION:
- Day 0 duration: 0-3 hours
- Day 0 Step 1 timing: Immediate
- Day 0 Step 2 timing: +30 minutes
- Day 0 Step 3 timing: +2 hours
- Day 1 start: +24 hours from Day 0
- Day 2 start: +24 hours from Day 1
- Day 3 start: +24 hours from Day 2
- Final push timing: +3 hours after discount reveal
- Discount urgency: 48 hours

Journey 1: Brand Overall Introduction
- Entry point: General brand awareness ads, social media
- Target audience: First-time visitors, cold traffic, luxury beauty seekers
- Journey goal: Convert to any device purchase
- Unique focus: Brand introduction, all 3 devices, identify interest
- Personalization options:
  * Button 1: "Anti-Aging ✨"
  * Button 2: "Acne & Clarity 💎"
  * Button 3: "Wellness & Mood 🧘"

[... etc for all 4 journeys ...]

DISCOUNT & OFFER DETAILS:
- Discount code: WELCOME15
- Discount value: 15%
- Offer validity: 48 hours
- Urgency messaging: "Offer ends soon" / "Last chance"

PRODUCT LINKS:
- PRO Mask: https://deessepro.com/products/pro-by-deesse-pro
- Sculpta: https://deessepro.com/products/sculpta-by-deesse-pro
- Express: https://deessepro.com/products/express-by-deesse-pro

Benefit pages:
- Anti-aging: https://deessepro.com/pages/fine-lines-and-wrinkles
- Acne: https://deessepro.com/pages/how-it-works?slide=acneorblemishes
- Wellness: https://deessepro.com/pages/improved-mood

BRAND VOICE:
- Sophistication: 7/10
- Tone: Sophisticated yet warm, scientific but approachable
- Key attributes: Swiss-engineered, clinical-grade, NASA-proven, medical-grade
- Emoji strategy: Strategic only (✨💎🧘⚡🔬)
- Avoid: "Cheap", "budget", overly casual language

BRAND COLORS FOR HTML:
- Primary color: #667eea (purple/blue)
- Secondary color: #764ba2 (deep purple)
- Accent color: #10b981 (green - for conversion steps)
- Background gradient start: #667eea
- Background gradient end: #764ba2
- Text color (dark): #2c3e50
- Text color (light): #5a6c7d

SPECIAL REQUIREMENTS:
- Journey 2: Focus on treatment modes and wavelengths
- Journey 3: Emphasize handheld convenience vs masks
- Journey 4: Entry-level but maintain premium language
- All journeys max 3 days
- No cross-selling in welcome journeys
```

---

## 🎯 TIPS FOR SUCCESS

**DO:**
✅ Fill in ALL bracketed sections
✅ Be specific about brand voice
✅ Provide actual URLs
✅ Specify your audience clearly
✅ List unique features per product
✅ Mention any compliance needs
✅ Include brand colors from your website

**Finding Your Brand Colors:**
1. Visit your website
2. Right-click → Inspect Element
3. Look for CSS color values (HEX codes like #667eea)
4. Or use a color picker browser extension
5. Or ask your design team for the brand style guide

**DON'T:**
❌ Leave sections blank
❌ Request more than 4 journeys at once
❌ Mix B2B and B2C
❌ Forget discount details
❌ Skip brand voice section
❌ Use RGB instead of HEX (convert at https://htmlcolorcodes.com)

---

## 🔄 REFINING THE OUTPUT

After Claude delivers, you can say:

**Copy changes:**
"Update Journey 2, Step 5 - focus more on [topic]"

**Link updates:**
"Change all anti-aging links to: [URL]"

**Structure changes:**
"Add a step to Day 2 about [topic]"

**Regenerate:**
"Regenerate the HTML visualizations with updates"

---

## 📦 YOU'LL RECEIVE

1. Journey markdown files (4)
2. Full detailed HTML visualization
3. Workflow overview HTML (structure only)
4. Comparison summary HTML
5. Master summary document
6. Confirmation documents

**Ready for:** Team review, WATI upload, asset creation, implementation

---

## 🚀 AFTER GENERATION

1. Review journey documents
2. Check HTML visualizations
3. Request any tweaks
4. Generate WATI JSON (ask Claude)
5. Create asset brief (ask Claude)
6. Test before launch
7. Deploy to WATI
8. Monitor and optimize

---

**Save this prompt for reuse with any brand or product!** 🎉
