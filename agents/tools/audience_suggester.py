"""
Audience suggester tool - suggests audience segments based on vertical and product.

Can use provided audience info or suggest B2B/B2C segments based on
the detected industry and product characteristics.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class AudienceSegment:
    """Definition of a target audience segment."""
    name: str = ""
    type: str = "B2C"  # B2B or B2C
    description: str = ""
    
    # Demographics (B2C focused)
    age_range: str = ""
    location: str = ""
    occupation: str = ""
    income_level: str = ""
    
    # Firmographics (B2B focused)
    company_size: str = ""
    job_titles: List[str] = field(default_factory=list)
    industry: str = ""
    
    # Psychographics
    pain_points: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    objections: List[str] = field(default_factory=list)
    
    # Journey relevance
    awareness_level: str = "problem-aware"  # unaware, problem-aware, solution-aware, product-aware
    buying_stage: str = "consideration"  # awareness, consideration, decision
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudienceSuggestion:
    """Complete audience suggestion with multiple segments."""
    journey_type: str = "B2C"  # Primary journey type
    segments: List[AudienceSegment] = field(default_factory=list)
    recommended_paths: int = 2  # Number of personalization paths
    segmentation_question: str = ""  # Question to segment users
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['segments'] = [s.to_dict() for s in self.segments]
        return result


def suggest_audiences(
    extracted_content: Dict[str, Any],
    journey_type: str = "B2C",
    user_provided: Optional[Dict[str, Any]] = None
) -> AudienceSuggestion:
    """
    Suggest audience segments based on extracted content.
    
    Args:
        extracted_content: Output from content_extractor
        journey_type: "B2B" or "B2C"
        user_provided: Optional user-provided audience info
        
    Returns:
        AudienceSuggestion with segment definitions
    """
    suggestion = AudienceSuggestion(journey_type=journey_type)
    
    # Get context from extracted content
    brand = extracted_content.get('brand', {})
    product = extracted_content.get('product', {})
    value_prop = extracted_content.get('value_proposition', {})
    
    industry = brand.get('industry', 'general business')
    product_name = product.get('name', 'the product')
    benefits = value_prop.get('key_benefits', [])
    
    # If user provided audience info, use it as primary segment
    if user_provided:
        primary_segment = _create_segment_from_user_input(user_provided, journey_type)
        suggestion.segments.append(primary_segment)
        
        # Add a secondary suggested segment
        secondary = _suggest_secondary_segment(industry, journey_type, primary_segment)
        if secondary:
            suggestion.segments.append(secondary)
    else:
        # Generate suggested segments based on industry
        suggested_segments = _suggest_segments_for_industry(
            industry, 
            journey_type, 
            product_name,
            benefits
        )
        suggestion.segments.extend(suggested_segments)
    
    # Generate segmentation question
    suggestion.segmentation_question = _generate_segmentation_question(
        suggestion.segments,
        product_name
    )
    
    suggestion.recommended_paths = min(len(suggestion.segments), 3)
    
    return suggestion


def _create_segment_from_user_input(
    user_input: Dict[str, Any],
    journey_type: str
) -> AudienceSegment:
    """Create a segment from user-provided audience info."""
    segment = AudienceSegment(
        name=user_input.get('name', 'Primary Audience'),
        type=journey_type,
        description=user_input.get('description', ''),
        age_range=user_input.get('age_range', ''),
        location=user_input.get('location', ''),
        occupation=user_input.get('occupation', ''),
    )
    
    if journey_type == "B2B":
        segment.company_size = user_input.get('company_size', '')
        segment.job_titles = user_input.get('job_titles', [])
        segment.industry = user_input.get('industry', '')
    
    # Add pain points and goals if provided
    segment.pain_points = user_input.get('pain_points', [])
    segment.goals = user_input.get('goals', [])
    
    return segment


def _suggest_secondary_segment(
    industry: str,
    journey_type: str,
    primary: AudienceSegment
) -> Optional[AudienceSegment]:
    """Suggest a secondary segment different from the primary."""
    
    # Generate a contrasting segment
    if journey_type == "B2C":
        # If primary is young, suggest older
        if "18-" in primary.age_range or "25-" in primary.age_range:
            return AudienceSegment(
                name="Established Professionals",
                type="B2C",
                description="More established individuals with different priorities",
                age_range="35-55",
                awareness_level="solution-aware",
                buying_stage="consideration",
                pain_points=["Time constraints", "Want proven solutions"],
                goals=["Efficiency", "Reliability"],
            )
        else:
            return AudienceSegment(
                name="Young Professionals",
                type="B2C",
                description="Younger audience entering this market",
                age_range="25-35",
                awareness_level="problem-aware",
                buying_stage="awareness",
                pain_points=["New to this", "Budget conscious"],
                goals=["Getting started", "Learning"],
            )
    else:
        # B2B: suggest different company size
        return AudienceSegment(
            name="Growing Companies",
            type="B2B",
            description="Companies in growth phase",
            company_size="11-50 employees",
            job_titles=["Operations Manager", "Team Lead"],
            awareness_level="problem-aware",
            buying_stage="consideration",
            pain_points=["Scaling challenges", "Resource constraints"],
            goals=["Efficiency", "Growth enablement"],
        )


def _suggest_segments_for_industry(
    industry: str,
    journey_type: str,
    product_name: str,
    benefits: List[str]
) -> List[AudienceSegment]:
    """Suggest audience segments based on industry."""
    
    segments = []
    
    # Industry-specific segment suggestions
    industry_segments = {
        'financial services': {
            'B2C': [
                AudienceSegment(
                    name="First-Time Savers",
                    type="B2C",
                    description="Individuals new to saving/investing",
                    age_range="25-35",
                    awareness_level="problem-aware",
                    buying_stage="consideration",
                    pain_points=["Don't know where to start", "Confused by options", "Worried about risk"],
                    goals=["Build savings habit", "Understand their options", "Feel financially secure"],
                    motivations=["Future security", "Life milestones"],
                ),
                AudienceSegment(
                    name="Active Savers",
                    type="B2C",
                    description="People already saving but looking for better options",
                    age_range="30-50",
                    awareness_level="solution-aware",
                    buying_stage="decision",
                    pain_points=["Poor returns", "Limited flexibility", "High fees"],
                    goals=["Better returns", "Tax efficiency", "Consolidate savings"],
                    motivations=["Optimization", "Efficiency"],
                ),
            ],
            'B2B': [
                AudienceSegment(
                    name="HR & Benefits Managers",
                    type="B2B",
                    description="Decision makers for employee benefits",
                    job_titles=["HR Director", "Benefits Manager", "People Lead"],
                    company_size="50-500 employees",
                    awareness_level="solution-aware",
                    buying_stage="consideration",
                    pain_points=["Employee retention", "Benefits complexity", "Cost management"],
                    goals=["Improve benefits package", "Attract talent", "Easy administration"],
                ),
            ],
        },
        'saas': {
            'B2B': [
                AudienceSegment(
                    name="SMB Decision Makers",
                    type="B2B",
                    description="Small business owners and managers",
                    job_titles=["Founder", "CEO", "Operations Manager"],
                    company_size="1-50 employees",
                    awareness_level="problem-aware",
                    buying_stage="consideration",
                    pain_points=["Manual processes", "No budget for enterprise tools", "Need quick wins"],
                    goals=["Automate tasks", "Save time", "Professional appearance"],
                ),
                AudienceSegment(
                    name="Enterprise Champions",
                    type="B2B",
                    description="Internal advocates at larger companies",
                    job_titles=["Team Lead", "Department Manager", "Senior Analyst"],
                    company_size="200+ employees",
                    awareness_level="solution-aware",
                    buying_stage="consideration",
                    pain_points=["Need to justify ROI", "Integration concerns", "Security requirements"],
                    goals=["Prove value to leadership", "Solve team problems", "Career advancement"],
                ),
            ],
            'B2C': [
                AudienceSegment(
                    name="Productivity Seekers",
                    type="B2C",
                    description="Individuals wanting to work smarter",
                    age_range="25-45",
                    awareness_level="problem-aware",
                    buying_stage="consideration",
                    pain_points=["Too many tasks", "Disorganized", "Overwhelmed"],
                    goals=["Get organized", "Save time", "Reduce stress"],
                ),
            ],
        },
        'e-commerce': {
            'B2C': [
                AudienceSegment(
                    name="Value Seekers",
                    type="B2C",
                    description="Price-conscious shoppers looking for deals",
                    age_range="25-45",
                    awareness_level="solution-aware",
                    buying_stage="consideration",
                    pain_points=["Budget constraints", "Want best value", "Fear of missing deals"],
                    goals=["Save money", "Get quality", "Find deals"],
                    motivations=["Savings", "Smart shopping"],
                ),
                AudienceSegment(
                    name="Convenience Buyers",
                    type="B2C",
                    description="Time-pressed shoppers prioritizing ease",
                    age_range="30-55",
                    awareness_level="product-aware",
                    buying_stage="decision",
                    pain_points=["No time to shop around", "Want reliability", "Hate complicated checkout"],
                    goals=["Quick purchase", "Reliable delivery", "Easy returns"],
                    motivations=["Convenience", "Time-saving"],
                ),
            ],
        },
        'grant management': {
            'B2B': [
                AudienceSegment(
                    name="Grant-Making Organizations",
                    type="B2B",
                    description="Foundations, trusts, and corporate CSR teams managing grant programs",
                    job_titles=["Program Manager", "Grants Officer", "Foundation Director", "CSR Manager"],
                    company_size="10-500 employees",
                    awareness_level="problem-aware",
                    buying_stage="consideration",
                    pain_points=["Drowning in spreadsheets", "Manual application reviews", "Can't track impact", "Too much admin time"],
                    goals=["Streamline grant management", "Track social value", "Reduce admin burden", "Better funding decisions"],
                    motivations=["Create more impact", "Work smarter not harder"],
                ),
                AudienceSegment(
                    name="Community Organizations",
                    type="B2B",
                    description="Nonprofits and charities seeking funding and managing grants received",
                    job_titles=["Executive Director", "Fundraising Manager", "Development Officer"],
                    company_size="1-50 employees",
                    awareness_level="solution-aware",
                    buying_stage="consideration",
                    pain_points=["Complex application processes", "Reporting requirements", "Finding funding opportunities"],
                    goals=["Win more grants", "Simplify reporting", "Build funder relationships"],
                    motivations=["Secure funding", "Focus on mission"],
                ),
            ],
            'B2C': [
                AudienceSegment(
                    name="Productivity Seekers",
                    type="B2C",
                    description="Individuals seeking to streamline grant-related work",
                    age_range="25-45",
                    awareness_level="problem-aware",
                    buying_stage="consideration",
                    pain_points=["Too many tasks", "Disorganized workflows", "Overwhelmed by complexity"],
                    goals=["Get organized", "Save time", "Reduce stress"],
                    motivations=["Efficiency", "Work-life balance"],
                ),
            ],
        },
    }
    
    # Get segments for this industry and journey type
    industry_data = industry_segments.get(industry, {})
    suggested = industry_data.get(journey_type, [])
    
    if suggested:
        segments.extend(suggested)
    else:
        # Default segments
        if journey_type == "B2C":
            segments.append(AudienceSegment(
                name="Primary Audience",
                type="B2C",
                description=f"Target customers for {product_name}",
                age_range="25-55",
                awareness_level="problem-aware",
                buying_stage="consideration",
                pain_points=["Looking for solutions"],
                goals=benefits[:3] if benefits else ["Solve their problem"],
            ))
        else:
            segments.append(AudienceSegment(
                name="Business Decision Makers",
                type="B2B",
                description=f"Key decision makers for {product_name}",
                job_titles=["Manager", "Director", "VP"],
                company_size="10-500 employees",
                awareness_level="solution-aware",
                buying_stage="consideration",
                pain_points=["Need efficient solutions"],
                goals=["Improve operations", "Reduce costs"],
            ))
    
    return segments[:3]  # Max 3 segments


def _generate_segmentation_question(
    segments: List[AudienceSegment],
    product_name: str
) -> str:
    """Generate a question to segment users in the journey."""
    
    if len(segments) < 2:
        return "What's most important to you?"
    
    # Create question based on segment differences
    if segments[0].type == "B2C":
        # Check if segments differ by goal
        goals_differ = len(set(
            tuple(s.goals[:1]) for s in segments if s.goals
        )) > 1
        
        if goals_differ:
            return "What's your main goal right now?"
        
        # Check if segments differ by awareness
        return "How familiar are you with this type of product?"
    
    else:  # B2B
        return "What's your company's biggest challenge right now?"


def generate_audience_markdown(suggestion: AudienceSuggestion) -> str:
    """
    Generate markdown representation of audience suggestion.
    
    Args:
        suggestion: AudienceSuggestion result
        
    Returns:
        Markdown string for the audience section
    """
    
    md = f"""# Audience Segments

## Journey Type: {suggestion.journey_type}

**Recommended Personalization Paths:** {suggestion.recommended_paths}

**Segmentation Question:** "{suggestion.segmentation_question}"

---

"""
    
    for i, segment in enumerate(suggestion.segments, 1):
        pain_points = '\n'.join(f'- {p}' for p in segment.pain_points) if segment.pain_points else '- (Not specified)'
        goals = '\n'.join(f'- {g}' for g in segment.goals) if segment.goals else '- (Not specified)'
        motivations = '\n'.join(f'- {m}' for m in segment.motivations) if segment.motivations else '- (Not specified)'
        
        md += f"""## Segment {i}: {segment.name}

**Type:** {segment.type}

**Description:** {segment.description}

"""
        
        if segment.type == "B2C":
            md += f"""### Demographics

| Field | Value |
|-------|-------|
| Age Range | {segment.age_range or '(Not specified)'} |
| Location | {segment.location or '(Not specified)'} |
| Occupation | {segment.occupation or '(Not specified)'} |

"""
        else:
            job_titles = ', '.join(segment.job_titles) if segment.job_titles else '(Not specified)'
            md += f"""### Firmographics

| Field | Value |
|-------|-------|
| Company Size | {segment.company_size or '(Not specified)'} |
| Job Titles | {job_titles} |
| Industry | {segment.industry or '(Not specified)'} |

"""
        
        md += f"""### Psychographics

**Awareness Level:** {segment.awareness_level}
**Buying Stage:** {segment.buying_stage}

#### Pain Points

{pain_points}

#### Goals

{goals}

#### Motivations

{motivations}

---

"""
    
    return md

