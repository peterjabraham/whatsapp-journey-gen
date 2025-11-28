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
    
    Args:
        text: The raw text content
        source_name: Name of the source for reference
        
    Returns:
        ExtractedContent with extracted elements
    """
    result = ExtractedContent(source=source_name, source_type="text")
    result.raw_text = text[:5000]
    
    # For text, we do simpler pattern matching
    lines = text.split('\n')
    
    # First non-empty substantial line is likely headline
    for line in lines:
        line = line.strip()
        if 10 < len(line) < 150:
            result.value_proposition.headline = line
            break
    
    # Extract bullet points as features/benefits
    benefits = []
    features = []
    
    for line in lines:
        line = line.strip()
        if line.startswith(('•', '-', '*', '✓', '✔')):
            item = line.lstrip('•-*✓✔ ').strip()
            if 10 < len(item) < 150:
                if re.match(r'^(get|achieve|save|earn|receive|enjoy)', item.lower()):
                    benefits.append(item)
                else:
                    features.append(item)
    
    result.value_proposition.key_benefits = benefits[:5]
    result.product.features = features[:8]
    
    # Extract stats
    stat_patterns = [
        r'\d+[,\d]*\+?\s*(?:customers?|users?|clients?|members?)',
        r'\d+%\s*(?:increase|growth|improvement)',
        r'£?\$?\d+[,\d]*(?:k|m)?\s*(?:saved|earned)',
    ]
    
    for pattern in stat_patterns:
        matches = re.findall(pattern, text, re.I)
        result.social_proof.stats.extend(matches[:2])
    
    result.social_proof.stats = list(set(result.social_proof.stats))[:5]
    
    return result

