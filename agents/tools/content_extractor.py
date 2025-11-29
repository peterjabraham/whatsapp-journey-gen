"""
Content extractor tool - extracts structured data from URLs and text.

Extracts value proposition, product info, social proof, CTAs, brand elements,
and assets that feed into WhatsApp journey creation.
"""

import re
import sys
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
import requests
from bs4 import BeautifulSoup

# Increase recursion limit for complex HTML parsing
sys.setrecursionlimit(5000)


# ============================================================================
# EXTRACTION SCHEMA
# ============================================================================

@dataclass
class ValueProposition:
    """Core value messaging - used for Day 0 welcome hooks."""
    headline: str = ""
    subheadline: str = ""
    key_benefits: List[str] = field(default_factory=list)


@dataclass
class ProductInfo:
    """Product/service details - used for educational content."""
    name: str = ""
    description: str = ""
    features: List[str] = field(default_factory=list)  # What it does
    outcomes: List[str] = field(default_factory=list)  # What customer gets


@dataclass
class SocialProof:
    """Trust elements - used for Day 2-3 credibility building."""
    testimonials: List[str] = field(default_factory=list)
    stats: List[str] = field(default_factory=list)  # "10,000+ customers"
    trust_badges: List[str] = field(default_factory=list)  # Certifications


@dataclass
class CTAs:
    """Call-to-action elements - used for buttons throughout journey."""
    primary: str = ""  # "Apply Now", "Book Demo"
    secondary: str = ""  # "Learn More"
    urls: Dict[str, str] = field(default_factory=dict)  # {action: url}


@dataclass
class BrandElements:
    """Brand identity - influences message tone and styling."""
    name: str = ""
    colors: List[str] = field(default_factory=list)
    tone_keywords: List[str] = field(default_factory=list)
    industry: str = ""


@dataclass
class Assets:
    """Available content assets - for media attachments in messages."""
    pdfs: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)


@dataclass
class ExtractedContent:
    """Complete extraction result from a source."""
    source: str = ""
    source_type: str = ""  # "url" or "pdf"
    value_proposition: ValueProposition = field(default_factory=ValueProposition)
    product: ProductInfo = field(default_factory=ProductInfo)
    social_proof: SocialProof = field(default_factory=SocialProof)
    ctas: CTAs = field(default_factory=CTAs)
    brand: BrandElements = field(default_factory=BrandElements)
    assets: Assets = field(default_factory=Assets)
    raw_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# Schema for reference (matches dataclasses above)
EXTRACTION_SCHEMA = {
    "value_proposition": {
        "headline": "str - Main promise/tagline",
        "subheadline": "str - Supporting statement",
        "key_benefits": "list - Top 3-5 benefits",
    },
    "product": {
        "name": "str - Product/service name",
        "description": "str - What it is",
        "features": "list - What it does",
        "outcomes": "list - What customer gets",
    },
    "social_proof": {
        "testimonials": "list - Customer quotes",
        "stats": "list - Numbers like '10,000+ customers'",
        "trust_badges": "list - Certifications, awards",
    },
    "ctas": {
        "primary": "str - Main action button text",
        "secondary": "str - Secondary action text",
        "urls": "dict - {action: url} mapping",
    },
    "brand": {
        "name": "str - Company/brand name",
        "colors": "list - Hex color codes",
        "tone_keywords": "list - Professional, Friendly, etc.",
        "industry": "str - Detected vertical",
    },
    "assets": {
        "pdfs": "list - PDF file references",
        "videos": "list - Video URLs",
        "images": "list - Image URLs",
    },
}


# ============================================================================
# URL EXTRACTION
# ============================================================================

def extract_from_url(url: str, timeout: int = 15) -> ExtractedContent:
    """
    Extract structured content from a URL.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        ExtractedContent with all extracted elements
    """
    result = ExtractedContent(source=url, source_type="url")
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        result.raw_text = f"Error fetching URL: {str(e)}"
        return result
    
    # Try lxml first (more robust), fall back to html.parser
    try:
        soup = BeautifulSoup(html, 'lxml')
    except Exception:
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except RecursionError:
            # If parsing fails, extract text with regex fallback
            result.raw_text = re.sub(r'<[^>]+>', ' ', html)[:5000]
            result.value_proposition.headline = "Content extraction limited"
            return result
    
    # Extract value proposition
    result.value_proposition = _extract_value_prop(soup)
    
    # Extract product info
    result.product = _extract_product_info(soup)
    
    # Extract social proof
    result.social_proof = _extract_social_proof(soup)
    
    # Extract CTAs
    result.ctas = _extract_ctas(soup, url)
    
    # Extract brand elements
    result.brand = _extract_brand(soup, html)
    
    # Extract assets
    result.assets = _extract_assets(soup, url)
    
    # Store raw text for additional processing
    result.raw_text = soup.get_text(separator='\n', strip=True)[:5000]
    
    return result


def _extract_value_prop(soup: BeautifulSoup) -> ValueProposition:
    """Extract headline, subheadline, and key benefits."""
    vp = ValueProposition()
    
    # Try to get headline from h1
    h1 = soup.find('h1')
    if h1:
        vp.headline = h1.get_text(strip=True)
    
    # Try meta description for subheadline
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        vp.subheadline = meta_desc['content'][:200]
    
    # Look for OG description as fallback
    if not vp.subheadline:
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            vp.subheadline = og_desc['content'][:200]
    
    # Extract benefits from bullet lists near top of page
    benefits = []
    for ul in soup.find_all('ul')[:5]:  # Check first 5 lists
        for li in ul.find_all('li')[:5]:  # Max 5 items per list
            text = li.get_text(strip=True)
            if 10 < len(text) < 150:  # Reasonable benefit length
                benefits.append(text)
    
    vp.key_benefits = benefits[:5]  # Max 5 benefits
    
    return vp


def _extract_product_info(soup: BeautifulSoup) -> ProductInfo:
    """Extract product name, description, features, and outcomes."""
    product = ProductInfo()
    
    # Product name from title or h1
    title = soup.find('title')
    if title:
        # Usually format is "Product Name | Company" or "Product Name - Company"
        title_text = title.get_text(strip=True)
        product.name = re.split(r'[|\-–—]', title_text)[0].strip()
    
    # Product description from first substantial paragraph
    for p in soup.find_all('p')[:10]:
        text = p.get_text(strip=True)
        if 50 < len(text) < 500:
            product.description = text
            break
    
    # Features from lists with feature-like content
    features = []
    outcomes = []
    
    for li in soup.find_all('li'):
        text = li.get_text(strip=True)
        if 10 < len(text) < 150:
            # Outcomes often start with "Get", "Achieve", "Save", etc.
            if re.match(r'^(get|achieve|save|earn|receive|enjoy|access)', text.lower()):
                outcomes.append(text)
            else:
                features.append(text)
    
    product.features = features[:8]
    product.outcomes = outcomes[:5]
    
    return product


def _extract_social_proof(soup: BeautifulSoup) -> SocialProof:
    """Extract testimonials, stats, and trust badges."""
    sp = SocialProof()
    
    # Look for testimonials in blockquotes or specific classes
    for quote in soup.find_all(['blockquote', 'q']):
        text = quote.get_text(strip=True)
        if 20 < len(text) < 500:
            sp.testimonials.append(text)
    
    # Also look for elements with testimonial-like classes
    testimonial_patterns = ['testimonial', 'review', 'quote', 'customer-say']
    for pattern in testimonial_patterns:
        for elem in soup.find_all(class_=re.compile(pattern, re.I)):
            text = elem.get_text(strip=True)
            if 20 < len(text) < 500 and text not in sp.testimonials:
                sp.testimonials.append(text)
    
    sp.testimonials = sp.testimonials[:3]  # Max 3 testimonials
    
    # Extract stats (numbers with context)
    text = soup.get_text()
    stat_patterns = [
        r'\d+[,\d]*\+?\s*(?:customers?|users?|clients?|members?)',
        r'\d+%\s*(?:increase|growth|improvement|savings?)',
        r'£?\$?\d+[,\d]*(?:k|m|bn?)?\s*(?:saved|earned|raised)',
        r'\d+\+?\s*(?:years?|countries|locations)',
    ]
    
    for pattern in stat_patterns:
        matches = re.findall(pattern, text, re.I)
        sp.stats.extend(matches[:2])
    
    sp.stats = list(set(sp.stats))[:5]  # Dedupe, max 5
    
    # Trust badges from alt text or specific patterns
    badge_patterns = ['certified', 'award', 'trusted', 'accredited', 'member of']
    for img in soup.find_all('img'):
        alt = img.get('alt', '').lower()
        for pattern in badge_patterns:
            if pattern in alt:
                sp.trust_badges.append(img.get('alt', ''))
    
    sp.trust_badges = sp.trust_badges[:5]
    
    return sp


def _extract_ctas(soup: BeautifulSoup, base_url: str) -> CTAs:
    """Extract call-to-action buttons and their URLs."""
    ctas = CTAs()
    
    # Primary CTA patterns
    primary_patterns = ['apply', 'sign up', 'get started', 'book', 'buy', 'start', 'try']
    secondary_patterns = ['learn more', 'find out', 'discover', 'see how', 'explore']
    
    # Look for buttons and links
    for elem in soup.find_all(['button', 'a']):
        text = elem.get_text(strip=True).lower()
        href = elem.get('href', '')
        
        # Make URL absolute
        if href and not href.startswith(('http', 'mailto', 'tel', '#', 'javascript')):
            if href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
        
        # Check for primary CTA
        if not ctas.primary:
            for pattern in primary_patterns:
                if pattern in text:
                    ctas.primary = elem.get_text(strip=True)
                    if href:
                        ctas.urls[ctas.primary] = href
                    break
        
        # Check for secondary CTA
        if not ctas.secondary:
            for pattern in secondary_patterns:
                if pattern in text:
                    ctas.secondary = elem.get_text(strip=True)
                    if href:
                        ctas.urls[ctas.secondary] = href
                    break
    
    return ctas


def _extract_brand(soup: BeautifulSoup, html: str) -> BrandElements:
    """Extract brand name, colors, tone, and industry."""
    brand = BrandElements()
    
    # Brand name from OG site_name or title
    og_site = soup.find('meta', attrs={'property': 'og:site_name'})
    if og_site and og_site.get('content'):
        brand.name = og_site['content']
    else:
        title = soup.find('title')
        if title:
            # Try to get company name from end of title
            parts = re.split(r'[|\-–—]', title.get_text(strip=True))
            if len(parts) > 1:
                brand.name = parts[-1].strip()
            else:
                brand.name = parts[0].strip()
    
    # Extract colors from CSS
    brand.colors = _extract_colors(html)
    
    # Detect tone from content
    text = soup.get_text().lower()
    tone_indicators = {
        'professional': ['professional', 'expert', 'trusted', 'reliable', 'established'],
        'friendly': ['friendly', 'easy', 'simple', 'fun', 'enjoy'],
        'innovative': ['innovative', 'cutting-edge', 'modern', 'advanced', 'smart'],
        'caring': ['caring', 'support', 'help', 'understand', 'family'],
        'premium': ['premium', 'luxury', 'exclusive', 'elite', 'bespoke'],
    }
    
    for tone, keywords in tone_indicators.items():
        if any(kw in text for kw in keywords):
            brand.tone_keywords.append(tone)
    
    if not brand.tone_keywords:
        brand.tone_keywords = ['professional']  # Default
    
    # Detect industry from common keywords
    industry_indicators = {
        'financial services': ['isa', 'savings', 'investment', 'pension', 'mortgage', 'insurance', 'bank'],
        'e-commerce': ['shop', 'cart', 'checkout', 'delivery', 'shipping', 'buy now'],
        'saas': ['software', 'platform', 'dashboard', 'integration', 'api', 'automate'],
        'healthcare': ['health', 'medical', 'doctor', 'patient', 'clinic', 'treatment'],
        'education': ['learn', 'course', 'training', 'certificate', 'student', 'education'],
        'real estate': ['property', 'home', 'house', 'rent', 'buy', 'estate'],
    }
    
    for industry, keywords in industry_indicators.items():
        matches = sum(1 for kw in keywords if kw in text)
        if matches >= 2:
            brand.industry = industry
            break
    
    if not brand.industry:
        brand.industry = 'general business'
    
    return brand


def _extract_colors(html: str) -> List[str]:
    """Extract hex colors from HTML/CSS."""
    colors = set()
    
    # Hex pattern
    hex_pattern = r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![0-9A-Fa-f])'
    matches = re.findall(hex_pattern, html)
    
    for match in matches:
        color = f"#{match.upper()}"
        if len(match) == 3:
            color = f"#{match[0]*2}{match[1]*2}{match[2]*2}".upper()
        
        # Skip very light/dark colors
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            if (r > 240 and g > 240 and b > 240):  # Too white
                continue
            if (r < 15 and g < 15 and b < 15):  # Too black
                continue
            
            colors.add(color)
        except (ValueError, IndexError):
            continue
    
    return list(colors)[:6]


def _extract_assets(soup: BeautifulSoup, base_url: str) -> Assets:
    """Extract PDF, video, and image assets."""
    from urllib.parse import urljoin
    
    assets = Assets()
    
    # PDFs from links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.pdf'):
            full_url = urljoin(base_url, href) if not href.startswith('http') else href
            assets.pdfs.append(full_url)
    
    # Videos from various sources
    for video in soup.find_all('video'):
        src = video.get('src') or (video.find('source') and video.find('source').get('src'))
        if src:
            assets.videos.append(urljoin(base_url, src) if not src.startswith('http') else src)
    
    # YouTube/Vimeo embeds
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src', '')
        if 'youtube' in src or 'vimeo' in src:
            assets.videos.append(src)
    
    # Key images (skip icons/logos by size estimation)
    for img in soup.find_all('img')[:20]:
        src = img.get('src', '')
        alt = img.get('alt', '').lower()
        
        # Skip likely icons/logos
        if any(x in alt for x in ['icon', 'logo', 'arrow', 'button']):
            continue
        if any(x in src.lower() for x in ['icon', 'logo', '1x1', 'pixel']):
            continue
        
        if src:
            full_url = urljoin(base_url, src) if not src.startswith('http') else src
            assets.images.append(full_url)
    
    assets.pdfs = assets.pdfs[:5]
    assets.videos = assets.videos[:3]
    assets.images = assets.images[:10]
    
    return assets


# ============================================================================
# TEXT EXTRACTION (for PDF content)
# ============================================================================

def extract_from_text(text: str, source_name: str = "document") -> ExtractedContent:
    """
    Extract structured content from raw text (e.g., from PDF).
    
    Enhanced to extract all the same attributes as URL extraction.
    
    Args:
        text: The raw text content
        source_name: Name of the source for reference
        
    Returns:
        ExtractedContent with extracted elements
    """
    result = ExtractedContent(source=source_name, source_type="pdf")
    result.raw_text = text[:5000]
    
    lines = text.split('\n')
    clean_lines = [l.strip() for l in lines if l.strip()]
    
    # ========== VALUE PROPOSITION ==========
    result.value_proposition = _extract_value_prop_from_text(clean_lines, text)
    
    # ========== PRODUCT INFO ==========
    result.product = _extract_product_from_text(clean_lines, text, source_name)
    
    # ========== SOCIAL PROOF ==========
    result.social_proof = _extract_social_proof_from_text(clean_lines, text)
    
    # ========== CTAs ==========
    result.ctas = _extract_ctas_from_text(clean_lines, text)
    
    # ========== BRAND ==========
    result.brand = _extract_brand_from_text(clean_lines, text, source_name)
    
    # ========== ASSETS ==========
    result.assets = _extract_assets_from_text(text)
    
    return result


def _extract_value_prop_from_text(lines: List[str], full_text: str) -> ValueProposition:
    """Extract value proposition from text content."""
    vp = ValueProposition()
    
    # Look for explicit value proposition patterns first
    value_prop_patterns = [
        r'(?:the|our)\s+(?:platform|solution|system)\s+(?:that|for)\s+(.{20,150})',
        r'(?:revolutioni[sz]ing|transforming|streamlining)\s+(.{15,100})',
        r'(?:help(?:s|ing)?|enable(?:s|ing)?)\s+(?:you|organizations?|teams?|companies?)\s+(.{15,100})',
    ]
    
    for pattern in value_prop_patterns:
        match = re.search(pattern, full_text, re.I)
        if match:
            vp.headline = match.group(0).strip()
            break
    
    # Headline: First substantial line that looks like a title
    if not vp.headline:
        for i, line in enumerate(lines[:10]):
            # Skip very short lines or lines that look like headers/page numbers
            if len(line) < 10 or len(line) > 150:
                continue
            if re.match(r'^(page\s*\d+|table of contents|\d+\.)', line.lower()):
                continue
            # Skip lines that are all caps (likely section headers)
            if line.isupper() and len(line) > 30:
                continue
            vp.headline = line
            break
    
    # Subheadline: Second substantial line or first paragraph-like content
    found_headline = False
    for line in lines[:15]:
        if line == vp.headline:
            found_headline = True
            continue
        if found_headline and 20 < len(line) < 300:
            vp.subheadline = line
            break
    
    # Key benefits: Look for bullet points and benefit-like statements
    benefits = []
    benefit_patterns = [
        r'(?:•|-|\*|✓|✔|→|►)\s*(.{15,150})',  # Bullet points
        r'(?:benefit|advantage|feature)s?:\s*(.{15,150})',  # Labeled benefits
        r'(?:save|reduce|streamline|automate|simplify|track|manage)\s+(.{10,100})',  # Action-oriented benefits
    ]
    
    for pattern in benefit_patterns:
        matches = re.findall(pattern, full_text, re.I | re.M)
        for match in matches:
            cleaned = match.strip().rstrip('.')
            if cleaned and cleaned not in benefits and len(cleaned) > 10:
                benefits.append(cleaned)
    
    # Also check for numbered lists
    numbered_pattern = r'^\d+[.):]\s*(.{15,150})'
    for line in lines:
        match = re.match(numbered_pattern, line)
        if match:
            item = match.group(1).strip()
            if item and item not in benefits:
                benefits.append(item)
    
    vp.key_benefits = benefits[:5]
    return vp


def _extract_product_from_text(lines: List[str], full_text: str, source_name: str) -> ProductInfo:
    """Extract product information from text content."""
    product = ProductInfo()
    
    # Product name: Try to find from source filename or prominent text
    # Check filename first (e.g., "LISA_Guide.pdf" -> "LISA Guide")
    name_from_file = re.sub(r'[_-]', ' ', source_name.rsplit('.', 1)[0])
    name_from_file = re.sub(r'\s+', ' ', name_from_file).strip()
    
    # Look for product/service name patterns in text
    name_patterns = [
        r'(?:introducing|welcome to|about)\s+([A-Z][A-Za-z\s]{3,30})',
        r'(?:the|our)\s+([A-Z][A-Za-z\s]{3,30})\s+(?:is|offers|provides)',
        r'^([A-Z][A-Za-z\s]{3,30})(?:\s*[-–:])?\s*(?:your|the|a)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, full_text, re.M)
        if match:
            product.name = match.group(1).strip()
            break
    
    if not product.name:
        product.name = name_from_file[:50] if len(name_from_file) > 3 else ""
    
    # Description: Find first paragraph-like content (50-500 chars)
    for line in lines:
        if 50 < len(line) < 500:
            # Skip if it looks like a list item or header
            if not line.startswith(('•', '-', '*', '✓', '✔', '1.', '2.')):
                product.description = line
                break
    
    # Features: What the product does
    features = []
    feature_keywords = ['feature', 'include', 'offer', 'provide', 'enable', 'allow']
    
    for line in lines:
        line_lower = line.lower()
        # Check for feature indicators
        if any(kw in line_lower for kw in feature_keywords):
            if 10 < len(line) < 200:
                features.append(line)
        # Check bullet points that describe capabilities
        if line.startswith(('•', '-', '*', '✓', '✔')):
            item = line.lstrip('•-*✓✔ ').strip()
            if 10 < len(item) < 150:
                if not re.match(r'^(get|achieve|save|earn|receive|enjoy|you)', item.lower()):
                    features.append(item)
    
    product.features = list(dict.fromkeys(features))[:8]  # Dedupe, max 8
    
    # Outcomes: What customer gets (benefit-focused)
    outcomes = []
    outcome_starters = r'^(get|achieve|save|earn|receive|enjoy|access|gain|unlock|discover)'
    
    for line in lines:
        item = line.lstrip('•-*✓✔ ').strip()
        if re.match(outcome_starters, item.lower()) and 10 < len(item) < 150:
            outcomes.append(item)
    
    product.outcomes = outcomes[:5]
    return product


def _extract_social_proof_from_text(lines: List[str], full_text: str) -> SocialProof:
    """Extract social proof from text content."""
    sp = SocialProof()
    
    # Testimonials: Look for quoted text and attribution patterns
    testimonials = []
    
    # Pattern 1: Text in quotes
    quote_pattern = r'["""](.{20,300})["""]'
    quotes = re.findall(quote_pattern, full_text)
    testimonials.extend(quotes[:3])
    
    # Pattern 2: Attribution-style quotes ("... - Name, Company")
    attribution_pattern = r'(.{20,300})\s*[-–—]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    for match in re.finditer(attribution_pattern, full_text):
        quote = match.group(1).strip().strip('"\'""''')
        if quote and len(quote) > 20:
            testimonials.append(f'{quote} - {match.group(2)}')
    
    sp.testimonials = list(dict.fromkeys(testimonials))[:3]
    
    # Stats: Extract numerical claims
    stat_patterns = [
        r'\d+[,\d]*\+?\s*(?:customers?|users?|clients?|members?|people)',
        r'\d+%\s*(?:increase|growth|improvement|savings?|more|better)',
        r'(?:over|more than)\s*\d+[,\d]*\s*(?:years?|customers?|members?)',
        r'£?\$?€?\d+[,\d]*(?:\.\d+)?(?:k|m|bn?|million|billion)?\s*(?:saved|raised|invested|earned)',
        r'\d+\+?\s*(?:years?|countries?|locations?|offices?)\s*(?:of experience|worldwide|globally)?',
        r'rated\s*\d+(?:\.\d+)?\s*(?:out of|/)\s*\d+',
        r'\d+(?:\.\d+)?★?\s*(?:star|rating)',
    ]
    
    for pattern in stat_patterns:
        matches = re.findall(pattern, full_text, re.I)
        sp.stats.extend(matches[:2])
    
    sp.stats = list(dict.fromkeys(sp.stats))[:5]
    
    # Trust badges: Look for certification/award mentions
    badge_patterns = [
        r'(?:certified|accredited|regulated)\s+by\s+([A-Za-z\s]+)',
        r'(?:member of|affiliated with)\s+([A-Za-z\s]+)',
        r'(?:winner|awarded?)\s+(?:of\s+)?([A-Za-z\s]+(?:award|prize))',
        r'(ISO\s*\d+|FCA|PRA|GDPR|SOC\s*\d+)\s*(?:certified|compliant|regulated)?',
    ]
    
    for pattern in badge_patterns:
        matches = re.findall(pattern, full_text, re.I)
        sp.trust_badges.extend([m.strip() for m in matches if m.strip()])
    
    sp.trust_badges = list(dict.fromkeys(sp.trust_badges))[:5]
    return sp


def _extract_ctas_from_text(lines: List[str], full_text: str) -> CTAs:
    """Extract call-to-action elements from text content."""
    ctas = CTAs()
    
    # Primary CTA patterns (action-oriented)
    primary_patterns = [
        r'(?:apply|sign up|get started|register|join|book|buy|start|try|subscribe)\s*(?:now|today|here|free)?',
        r'(?:open|create)\s*(?:an?\s*)?(?:account|profile)',
        r'(?:request|schedule)\s*(?:a\s*)?(?:demo|consultation|call)',
    ]
    
    for pattern in primary_patterns:
        match = re.search(pattern, full_text, re.I)
        if match:
            ctas.primary = match.group(0).strip().title()
            break
    
    if not ctas.primary:
        ctas.primary = "Get Started"  # Default
    
    # Secondary CTA patterns (info-oriented)
    secondary_patterns = [
        r'(?:learn|find out|discover|explore|read)\s*more',
        r'(?:download|get)\s*(?:the\s*)?(?:guide|brochure|pdf)',
        r'(?:contact|speak to|talk to)\s*(?:us|an? (?:advisor|expert))',
        r'see\s*(?:how|why|what)',
    ]
    
    for pattern in secondary_patterns:
        match = re.search(pattern, full_text, re.I)
        if match:
            ctas.secondary = match.group(0).strip().title()
            break
    
    if not ctas.secondary:
        ctas.secondary = "Learn More"  # Default
    
    # Extract URLs from text
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, full_text)
    
    for url in urls[:5]:
        # Try to categorize URL by keywords
        url_lower = url.lower()
        if any(x in url_lower for x in ['apply', 'signup', 'register', 'join']):
            ctas.urls[ctas.primary] = url
        elif any(x in url_lower for x in ['learn', 'about', 'info', 'guide']):
            ctas.urls[ctas.secondary] = url
        elif not ctas.urls:
            ctas.urls["Main Link"] = url
    
    return ctas


def _extract_brand_from_text(lines: List[str], full_text: str, source_name: str) -> BrandElements:
    """Extract brand elements from text content."""
    brand = BrandElements()
    
    # Brand name: Look for company name patterns
    name_patterns = [
        r'(?:©|copyright)\s*(?:\d{4}\s*)?([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|LLC|plc)?)',
        r'([A-Z][A-Za-z]+(?:\s+[A-Z][a-z]+)?)\s*(?:is|are)\s+(?:a|an|the)\s+(?:leading|trusted|premier)',
        r'(?:about|welcome to)\s+([A-Z][A-Za-z\s&]{2,30})',
        r'([A-Z][A-Za-z]+)\s+(?:©|®|™)',
        # Additional patterns for product names
        r'(?:introducing|discover|welcome to)\s+([A-Z][A-Za-z\s]+)',
        r'^([A-Z][A-Za-z]+(?:\s+[A-Z][a-z]+)?)\s*$',  # Standalone title line
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, full_text, re.M)
        if match:
            name = match.group(1).strip()
            if 2 < len(name) < 40:
                brand.name = name
                break
    
    # Fallback to filename
    if not brand.name:
        name_from_file = re.sub(r'[_-]', ' ', source_name.rsplit('.', 1)[0])
        # Clean up common prefixes/suffixes
        name_from_file = re.sub(r'\s*(guide|brochure|overview|info|document)\s*$', '', name_from_file, flags=re.I)
        parts = name_from_file.split()
        if parts:
            # Take first 2-3 words that look like a name
            brand.name = ' '.join(parts[:3]).strip()
    
    # Colors: Look for hex codes or color mentions (rare in PDFs)
    hex_pattern = r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![0-9A-Fa-f])'
    colors = re.findall(hex_pattern, full_text)
    brand.colors = [f"#{c.upper()}" for c in colors[:6]]
    
    # Tone keywords: Detect from language
    text_lower = full_text.lower()
    tone_indicators = {
        'professional': ['professional', 'expert', 'trusted', 'reliable', 'established', 'quality'],
        'friendly': ['friendly', 'easy', 'simple', 'fun', 'enjoy', 'love', 'happy'],
        'innovative': ['innovative', 'cutting-edge', 'modern', 'advanced', 'smart', 'technology', 'revolutionising', 'transforming'],
        'caring': ['caring', 'support', 'help', 'understand', 'family', 'community', 'together', 'impact', 'social'],
        'premium': ['premium', 'luxury', 'exclusive', 'elite', 'bespoke', 'exceptional'],
        'secure': ['secure', 'safe', 'protected', 'regulated', 'compliant', 'trusted'],
    }
    
    for tone, keywords in tone_indicators.items():
        if sum(1 for kw in keywords if kw in text_lower) >= 2:
            brand.tone_keywords.append(tone)
    
    if not brand.tone_keywords:
        brand.tone_keywords = ['professional']
    
    # Industry detection - EXPANDED with more specific patterns
    industry_indicators = {
        'financial services': ['isa', 'savings', 'investment', 'pension', 'mortgage', 'insurance', 'bank', 'finance', 'loan', 'credit', 'tax-free', 'bonus'],
        'e-commerce': ['shop', 'cart', 'checkout', 'delivery', 'shipping', 'buy now', 'order', 'product', 'store'],
        'saas': ['software', 'platform', 'dashboard', 'integration', 'api', 'automate', 'cloud', 'subscription', 'workflow', 'streamline'],
        'grant management': ['grant', 'funding', 'funder', 'grantee', 'social value', 'impact', 'community', 'charity', 'nonprofit', 'foundation', 'philanthropy', 'csr', 'giving'],
        'healthcare': ['health', 'medical', 'doctor', 'patient', 'clinic', 'treatment', 'wellness', 'care', 'therapy'],
        'education': ['learn', 'course', 'training', 'certificate', 'student', 'education', 'teach', 'degree', 'curriculum'],
        'real estate': ['property', 'home', 'house', 'rent', 'estate', 'mortgage', 'apartment', 'landlord'],
        'recruitment': ['job', 'career', 'hire', 'recruit', 'candidate', 'employer', 'vacancy', 'talent'],
        'travel': ['travel', 'hotel', 'flight', 'booking', 'vacation', 'holiday', 'destination', 'tourism'],
        'marketing automation': ['marketing', 'campaign', 'engagement', 'automation', 'crm', 'email', 'whatsapp', 'journey'],
    }
    
    best_industry = 'general business'
    best_score = 0
    
    for industry, keywords in industry_indicators.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_industry = industry
    
    # Require only 1 match for very specific industries
    specific_industries = ['grant management', 'marketing automation']
    if best_industry in specific_industries and best_score >= 1:
        brand.industry = best_industry
    elif best_score >= 2:
        brand.industry = best_industry
    else:
        brand.industry = 'general business'
    
    return brand


def _extract_assets_from_text(full_text: str) -> Assets:
    """Extract asset references from text content."""
    assets = Assets()
    
    # URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, full_text)
    
    for url in urls:
        url_lower = url.lower()
        if url_lower.endswith('.pdf'):
            assets.pdfs.append(url)
        elif any(x in url_lower for x in ['youtube', 'vimeo', 'video', '.mp4', '.webm']):
            assets.videos.append(url)
        elif any(url_lower.endswith(x) for x in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            assets.images.append(url)
    
    # Look for file references
    file_patterns = [
        r'(?:download|see|view|refer to)\s*(?:the\s*)?([A-Za-z0-9_-]+\.(?:pdf|doc|docx))',
        r'(?:attached|enclosed|included):\s*([A-Za-z0-9_-]+\.(?:pdf|doc|docx))',
    ]
    
    for pattern in file_patterns:
        matches = re.findall(pattern, full_text, re.I)
        assets.pdfs.extend(matches)
    
    # Dedupe
    assets.pdfs = list(dict.fromkeys(assets.pdfs))[:5]
    assets.videos = list(dict.fromkeys(assets.videos))[:3]
    assets.images = list(dict.fromkeys(assets.images))[:10]
    
    return assets

