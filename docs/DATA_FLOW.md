# Data Flow and Schema Documentation

Last updated: 2024-11-28

## Current Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    URLs     │  │    PDFs     │  │ Journey Type│  │  Overrides  │         │
│  │ (multiple)  │  │ (multiple)  │  │  B2B/B2C    │  │ name/colors │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                │                │
┌─────────────────────────────────────────┐ │                │
│        CONTENT EXTRACTION               │ │                │
├─────────────────────────────────────────┤ │                │
│                                         │ │                │
│  URL Path:                              │ │                │
│  ┌─────────────────────────────────┐    │ │                │
│  │      extract_from_url()         │    │ │                │
│  │  • HTML parsing with BS4/lxml   │    │ │                │
│  │  • Meta tags, OG tags           │    │ │                │
│  │  • CSS color extraction         │    │ │                │
│  │  • CTA button detection         │    │ │                │
│  │  • Asset link discovery         │    │ │                │
│  │  [COMPREHENSIVE ✓]              │    │ │                │
│  └─────────────────────────────────┘    │ │                │
│                                         │ │                │
│  PDF Path:                              │ │                │
│  ┌─────────────────────────────────┐    │ │                │
│  │    extract_pdf_from_bytes()     │    │ │                │
│  │  • PyMuPDF markdown extraction  │    │ │                │
│  └───────────────┬─────────────────┘    │ │                │
│                  ▼                      │ │                │
│  ┌─────────────────────────────────┐    │ │                │
│  │     extract_from_text()         │    │ │                │
│  │  (ENHANCED - matches URL)       │    │ │                │
│  │  • _extract_value_prop_from_text│    │ │                │
│  │  • _extract_product_from_text   │    │ │                │
│  │  • _extract_social_proof_text   │    │ │                │
│  │  • _extract_ctas_from_text      │    │ │                │
│  │  • _extract_brand_from_text     │    │ │                │
│  │  • _extract_assets_from_text    │    │ │                │
│  │  [COMPREHENSIVE ✓]              │    │ │                │
│  └─────────────────────────────────┘    │ │                │
│                                         │ │                │
└───────────────────┬─────────────────────┘ │                │
                    │                       │                │
                    ▼                       │                │
┌───────────────────────────────────────────┴────────────────┴────────────────┐
│                        ExtractedContent Schema                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   URL Extraction    │  PDF Extraction   │  Usage in Journey                 │
│   ─────────────────────────────────────────────────────────────              │
│                     │  (ENHANCED ✓)     │                                    │
│   value_proposition │                   │                                    │
│   ├── headline      │  ✓ Title detect   │  → Day 0 welcome hook              │
│   ├── subheadline   │  ✓ 2nd line       │  → Day 0 context                   │
│   └── key_benefits  │  ✓ Bullets/lists  │  → Day 0-1 instant value           │
│                     │                   │                                    │
│   product           │                   │                                    │
│   ├── name          │  ✓ Filename/text  │  → All messages header             │
│   ├── description   │  ✓ 1st paragraph  │  → Day 1 educational               │
│   ├── features      │  ✓ Bullet points  │  → Day 1 what it does              │
│   └── outcomes      │  ✓ Get/Achieve    │  → Day 1-2 what you get            │
│                     │                   │                                    │
│   social_proof      │                   │                                    │
│   ├── testimonials  │  ✓ Quotes/attrib  │  → Day 2 trust building            │
│   ├── stats         │  ✓ Stat patterns  │  → Day 2-3 credibility             │
│   └── trust_badges  │  ✓ Cert/award     │  → Throughout for trust            │
│                     │                   │                                    │
│   ctas              │                   │                                    │
│   ├── primary       │  ✓ Apply/Join     │  → All CTA buttons                 │
│   ├── secondary     │  ✓ Learn More     │  → Info buttons                    │
│   └── urls          │  ✓ URL patterns   │  → Button hrefs                    │
│                     │                   │                                    │
│   brand             │                   │                                    │
│   ├── name          │  ✓ ©/patterns     │  → Headers, signatures             │
│   ├── colors        │  ✓ Hex codes      │  → HTML styling                    │
│   ├── tone_keywords │  ✓ Keyword scan   │  → Message style                   │
│   └── industry      │  ✓ Industry kw    │  → Audience targeting              │
│                     │                   │                                    │
│   assets            │                   │                                    │
│   ├── pdfs          │  ✓ URL/refs       │  → Media attachments               │
│   ├── videos        │  ✓ Video URLs     │  → Media attachments               │
│   └── images        │  ✓ Image URLs     │  → Media attachments               │
│                     │                   │                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR PIPELINE                                 │
│                                                                              │
│   *** POST-EXTRACTION PROCESSING IS IDENTICAL FOR URL AND PDF ***            │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Both URL and PDF produce ExtractedContent → SAME downstream processing:     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ INPUT: ExtractedContent (from URL or PDF - identical structure)      │   │
│  │   • value_proposition: headline, subheadline, key_benefits           │   │
│  │   • product: name, description, features, outcomes                   │   │
│  │   • social_proof: testimonials, stats, trust_badges                  │   │
│  │   • ctas: primary, secondary, urls                                   │   │
│  │   • brand: name, colors, tone_keywords, industry                     │   │
│  │   • assets: pdfs, videos, images                                     │   │
│  └────────────────────────────┬─────────────────────────────────────────┘   │
│                               │                                              │
│                               ▼                                              │
│  Step 1: MERGE SOURCES (if multiple URLs/PDFs)                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  _extract_content() in orchestrator.py                                  │ │
│  │  • Primary source = first extraction (URL or PDF)                      │ │
│  │  • Supplement missing fields from additional sources                   │ │
│  │  • Extend list fields (benefits, features, testimonials, stats)       │ │
│  │  • Deduplicate and limit (max 5 benefits, 10 features, etc.)          │ │
│  │  OUTPUT: Single merged ExtractedContent                                │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                               │                                              │
│                               ▼                                              │
│  Step 2: BRAND ANALYSIS                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  analyze_brand(extracted.to_dict()) → BrandAnalysis                    │ │
│  │  INPUT: ExtractedContent.brand, value_proposition, product             │ │
│  │  OUTPUT:                                                               │ │
│  │    • company_name, industry                                            │ │
│  │    • tone[], formality_level, personality_traits[]                     │ │
│  │    • primary_color, accent_color, background_color                     │ │
│  │    • key_phrases[], words_to_avoid[], emoji_recommendation             │ │
│  │    • value_statement, differentiators[], target_emotion                │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                               │                                              │
│                               ▼                                              │
│  Step 3: AUDIENCE SUGGESTION                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  suggest_audiences(extracted.to_dict(), journey_type) → AudienceSugg   │ │
│  │  INPUT: ExtractedContent.brand.industry, product.name, key_benefits    │ │
│  │  OUTPUT:                                                               │ │
│  │    • journey_type (B2B/B2C)                                            │ │
│  │    • segments[]: AudienceSegment (name, description, demographics,     │ │
│  │                  pain_points[], goals[], awareness_level, buying_stage)│ │
│  │    • recommended_paths, segmentation_question                          │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                               │                                              │
│                               ▼                                              │
│  Step 4: OFFER GENERATION                                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  generate_offer_markdown(headline, discount, timeline, timing)         │ │
│  │  INPUT: value_proposition.headline + user_inputs                       │ │
│  │  OUTPUT: Markdown with:                                                │ │
│  │    • Offer details (headline, discount_code, valid_until, terms)      │ │
│  │    • Campaign timeline (start, end, duration)                         │ │
│  │    • Message timing config (delays between steps)                     │ │
│  │    • Journey structure (Day 0-3 overview)                             │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                               │                                              │
│                               ▼                                              │
│  Step 5: MERGE TO BRIEF                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  merge_to_brief(brand_md, audience_md, offer_md, platform_config)     │ │
│  │  OUTPUT: MergedBrief                                                   │ │
│  │    • combined_markdown: Single document with all sections              │ │
│  │    • Pre-generation checklist                                          │ │
│  │    • Platform constraints (WATI character limits, etc.)               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           REVIEW PAGE                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  User reviews/edits 4_combined_brief.md                                │ │
│  │  Can modify: brand info, audience, offer, timeline                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      JOURNEY GENERATOR                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  brief_to_prompt() → Adds HTML template specs                          │ │
│  │  call_model() → OpenRouter API (GPT/Claude/Llama)                     │ │
│  │  parse_files_from_content() → Extract file blocks                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  OUTPUT:                                                                     │
│  ├── journey.md              (markdown specification)                        │
│  ├── summary_workflow.html   (visual overview)                              │
│  └── full_detail_workflow.html (complete message copy)                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## URL vs PDF Processing Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROCESSING PATH COMPARISON                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   STEP              │   URL PATH              │   PDF PATH                  │
│   ──────────────────┼─────────────────────────┼───────────────────────────  │
│                     │                         │                             │
│   1. INPUT          │ URL string              │ PDF file bytes              │
│                     │                         │                             │
│   2. RAW EXTRACT    │ HTTP GET + BeautifulSoup│ PyMuPDF → markdown text     │
│                     │ (HTML parsing)          │                             │
│                     │                         │                             │
│   3. STRUCTURED     │ extract_from_url()      │ extract_from_text()         │
│      EXTRACTION     │ (HTML-specific parsing) │ (text pattern matching)     │
│                     │                         │                             │
│   4. OUTPUT         │ ExtractedContent        │ ExtractedContent            │
│      (IDENTICAL)    │ (same dataclass)        │ (same dataclass)            │
│                     │                         │                             │
│   ════════════════════════════════════════════════════════════════════════  │
│   FROM HERE ON, PROCESSING IS 100% IDENTICAL:                               │
│   ════════════════════════════════════════════════════════════════════════  │
│                     │                         │                             │
│   5. MERGE          │         ← _extract_content() merges both →            │
│                     │                                                       │
│   6. ANALYZE        │         ← analyze_brand(extracted.to_dict()) →        │
│                     │                                                       │
│   7. AUDIENCE       │         ← suggest_audiences(extracted.to_dict()) →    │
│                     │                                                       │
│   8. OFFER          │         ← generate_offer_markdown() →                 │
│                     │                                                       │
│   9. BRIEF          │         ← merge_to_brief() →                          │
│                     │                                                       │
│   10. REVIEW        │         ← User review/edit →                          │
│                     │                                                       │
│   11. GENERATE      │         ← Journey Generator (OpenRouter API) →        │
│                     │                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** The ONLY difference is in steps 2-3 (raw extraction → structured data). 
Steps 5-11 use the SAME code path regardless of input source.

---

## PDF Extraction Methods (IMPLEMENTED)

The `extract_from_text()` function now extracts all attributes:

| Attribute | Detection Method | Status |
|-----------|------------------|--------|
| `value_proposition.headline` | Title detection, skip headers/page nums | ✓ |
| `value_proposition.subheadline` | Second substantial line | ✓ |
| `value_proposition.key_benefits` | Bullet points, numbered lists | ✓ |
| `product.name` | Filename + text patterns ("Introducing X") | ✓ |
| `product.description` | First paragraph (50-500 chars) | ✓ |
| `product.features` | Bullet points, feature keywords | ✓ |
| `product.outcomes` | Lines starting with "Get/Achieve/Save" | ✓ |
| `social_proof.testimonials` | Quoted text, attribution patterns | ✓ |
| `social_proof.stats` | Number patterns (X+ customers, X%) | ✓ |
| `social_proof.trust_badges` | Certification/award mentions | ✓ |
| `ctas.primary` | "Apply/Sign up/Get started" patterns | ✓ |
| `ctas.secondary` | "Learn more/Find out" patterns | ✓ |
| `ctas.urls` | URL extraction + categorization | ✓ |
| `brand.name` | ©/trademark patterns, filename | ✓ |
| `brand.colors` | Hex code patterns | ✓ |
| `brand.tone_keywords` | Keyword frequency analysis | ✓ |
| `brand.industry` | Industry keyword patterns (8 industries) | ✓ |
| `assets.pdfs` | .pdf URLs, file references | ✓ |
| `assets.videos` | Video URLs (youtube/vimeo/.mp4) | ✓ |
| `assets.images` | Image URLs (.jpg/.png etc) | ✓ |

## Extraction Schema Reference

```
ExtractedContent
├── source: str                 # URL or filename
├── source_type: str            # "url" | "pdf" | "text"
│
├── value_proposition
│   ├── headline: str           # Main hook (Day 0)
│   ├── subheadline: str        # Supporting context
│   └── key_benefits: [str]     # Top 5 benefits
│
├── product
│   ├── name: str               # Product/service name
│   ├── description: str        # What it is
│   ├── features: [str]         # What it does
│   └── outcomes: [str]         # What customer gets
│
├── social_proof
│   ├── testimonials: [str]     # Customer quotes
│   ├── stats: [str]            # "10,000+ customers"
│   └── trust_badges: [str]     # Awards, certifications
│
├── ctas
│   ├── primary: str            # "Apply Now"
│   ├── secondary: str          # "Learn More"
│   └── urls: {action: url}     # Click targets
│
├── brand
│   ├── name: str               # Company name
│   ├── colors: [str]           # Hex codes
│   ├── tone_keywords: [str]    # Professional, Friendly
│   └── industry: str           # Detected vertical
│
├── assets
│   ├── pdfs: [str]             # PDF URLs
│   ├── videos: [str]           # Video URLs
│   └── images: [str]           # Image URLs
│
└── raw_text: str               # First 5000 chars
```

