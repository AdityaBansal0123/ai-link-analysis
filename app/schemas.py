from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


# ==========================================
# Request Schemas
# ==========================================

class LinkAnalysisRequest(BaseModel):
    """Request payload for website link analysis."""
    url: str = Field(
        ...,
        description="The full HTTP/HTTPS website URL to analyze.",
        examples=["https://dxora.com", "https://stripe.com"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com"
            }
        }
    )


# ==========================================
# Section 1: Competitor vs Your Brand Details
# ==========================================

class BrandDetails(BaseModel):
    name: str = Field(..., description="Brand or company name.")
    category: str = Field(..., description="Primary business sector or category.")
    summary: str = Field(..., description="Concise business overview / summary.")


class CompetitorComparison(BaseModel):
    your_brand_advantage: str = Field(..., description="How your brand differentiates or wins against this competitor.")
    opportunity_to_improve: str = Field(..., description="Market gap or feature to learn from this competitor.")


class CompetitorItem(BaseModel):
    name: str = Field(..., description="Competitor brand name.")
    website: Optional[str] = Field(None, description="Competitor website or domain if known.")
    main_service: str = Field(..., description="Competitor's primary product or offering.")
    target_market: str = Field(..., description="Competitor's primary target market segment.")
    strengths: List[str] = Field(default_factory=list, description="Competitor key strengths.")
    weaknesses_or_gaps: List[str] = Field(default_factory=list, description="Competitor weaknesses or market gaps.")
    comparison_with_brand: CompetitorComparison = Field(..., description="Direct head-to-head comparison.")


class CompetitorAnalysis(BaseModel):
    brand_overview: str = Field(..., description="Comprehensive overview of your brand positioning.")
    main_category: str = Field(..., description="Core business sector.")
    main_products_and_services: List[str] = Field(..., description="List of detected flagship products and services.")
    competitors: List[CompetitorItem] = Field(..., min_length=3, description="Minimum 3 identified competitors.")
    brand_strengths: List[str] = Field(..., description="Your brand's internal strengths.")
    strengths: Optional[List[str]] = Field(default_factory=list, description="Alias for brand_strengths.")
    brand_advantages: List[str] = Field(..., description="Your brand's competitive edges in the marketplace.")
    opportunities: List[str] = Field(..., description="Opportunities to improve market positioning.")
    source_note: str = Field(
        default="Identified via contextual business intelligence and web content understanding.",
        description="Data provenance notice."
    )


# ==========================================
# Section 2: Top 5 Target Search Queries
# ==========================================

class SearchQueryItem(BaseModel):
    query: str = Field(..., description="Target search query string.")
    platforms: List[str] = Field(..., description="Relevant platforms (Google, Facebook, Instagram, LinkedIn, X).")
    intent: str = Field(..., description="Search intent (e.g. Service Search, B2B Search, Inspiration, Discovery).")
    business_relevance: str = Field(..., description="Explanation of why this query drives qualified leads.")
    target_audience: str = Field(..., description="Specific audience group using this query.")
    search_volume_note: Optional[str] = Field(
        default="Volume omitted per testing specification: unverified search volumes must not be hallucinated without dedicated third-party API data.",
        description="Disclaimer on search volume reporting."
    )


# ==========================================
# Section 3: SEO Improvements
# ==========================================

class SupportingContentItem(BaseModel):
    content_type: str = Field(..., description="Type of content: Service Landing Page, Industry Page, FAQ, Blog, etc.")
    topic: str = Field(..., description="Recommended content title or subject.")
    purpose: str = Field(..., description="Search intent or SEO ranking purpose served by this content.")


class SEOImprovements(BaseModel):
    primary_keyword: str = Field(..., description="Primary high-intent business keyword.")
    secondary_keywords: List[str] = Field(..., description="Secondary keyword cluster.")
    long_tail_keywords: List[str] = Field(..., description="Long-tail keyword opportunities.")
    relevant_business_keywords: List[str] = Field(..., description="Broader industry/business terminology.")
    recommended_title: str = Field(..., description="SEO-optimized title tag (50-60 characters).")
    title_primary_keyword: str = Field(..., description="Primary keyword placed within the title.")
    title_improvement_rationale: str = Field(..., description="Rationale for the recommended title structure.")
    meta_description: str = Field(..., description="Recommended meta description (140-160 characters).")
    meta_description_summary: str = Field(..., description="Human-friendly value proposition in the description.")
    meta_description_keywords: List[str] = Field(..., description="Keywords embedded in the meta description.")
    supporting_content: List[SupportingContentItem] = Field(..., description="Content ideas to build search authority.")


# ==========================================
# Section 4: Top 5 Services
# ==========================================

class ServiceItem(BaseModel):
    service_name: str = Field(..., description="Name of the service or product.")
    description: str = Field(..., description="Concise explanation of the service.")
    target_industry: str = Field(..., description="Primary vertical or industry for this service.")
    target_customer: str = Field(..., description="Ideal customer persona or company type.")
    main_benefit: str = Field(..., description="Core business value delivered to the client.")
    is_inferred: bool = Field(
        default=False,
        description="True if inferred from broader context; False if explicitly stated on the website."
    )


# ==========================================
# Section 5: Target Audience Identification
# ==========================================

class CustomerProfile(BaseModel):
    role_or_persona: str = Field(..., description="Job role or buyer persona title.")
    pain_points: List[str] = Field(..., description="Core pain points this customer faces.")
    goals: List[str] = Field(..., description="Key objectives and business outcomes desired.")


class AudienceSegment(BaseModel):
    audience: str = Field(..., description="Audience identifier e.g., Audience 1, Audience 2.")
    business_type: str = Field(..., description="Type of company or client e.g., Small Businesses, Startups.")
    requirement: str = Field(..., description="Primary requirement or service needed.")


class TargetAudience(BaseModel):
    primary_audience: List[str] = Field(..., description="Primary audience segments.")
    secondary_audience: List[str] = Field(..., description="Secondary / adjacent audience segments.")
    industries: List[str] = Field(default_factory=list, description="Target industries (e.g. Healthcare, Fintech, Retail).")
    industry_segments: Optional[List[str]] = Field(default_factory=list, description="Industry segments.")
    business_types: List[str] = Field(..., description="Business operational models (e.g. B2B, SMB, Enterprise).")
    customer_profiles: List[CustomerProfile] = Field(..., description="Detailed personas with pain points & goals.")
    geographical_focus: Optional[str] = Field(default="Global", description="Geographic scope if detected or inferred.")
    customer_needs: List[str] = Field(..., description="Core customer needs and operational challenges.")
    potential_customer_interests: List[str] = Field(..., description="Related topics or technological interests.")
    recommended_segments: List[AudienceSegment] = Field(..., description="5 recommended audience segments.")


# ==========================================
# Unified Analysis & Top-Level Response
# ==========================================

class AnalysisResult(BaseModel):
    """The structured 5-section analysis payload."""
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[SearchQueryItem] = Field(..., min_length=5, max_length=5)
    seo_improvements: SEOImprovements
    top_services: List[ServiceItem] = Field(..., min_length=1, max_length=5)
    target_audience: TargetAudience


class AnalysisMetadata(BaseModel):
    extracted_at: str
    http_status: int
    page_title: Optional[str] = None
    character_count_analyzed: int
    model_used: str
    execution_time_seconds: float


class LinkAnalysisResponse(BaseModel):
    """Standardized top-level API response."""
    success: bool = True
    website: str
    brand: BrandDetails
    analysis: AnalysisResult
    metadata: Optional[AnalysisMetadata] = None


# ==========================================
# Error Response Schema
# ==========================================

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
