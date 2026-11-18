import datetime
import logging
import time
from typing import Dict, Any

from app.config import settings
from app.schemas import (
    LinkAnalysisResponse,
    BrandDetails,
    AnalysisResult,
    CompetitorAnalysis,
    SearchQueryItem,
    SEOImprovements,
    SupportingContentItem,
    ServiceItem,
    TargetAudience,
    CustomerProfile,
    AudienceSegment,
    AnalysisMetadata,
)
from app.services.website_extractor import WebsiteExtractor, ExtractedWebsiteContent
from app.services.llm_service import get_llm_service
from app.services.competitor_service import CompetitorService
from app.utils.validators import validate_and_sanitize_url, LLMServiceError

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Main orchestrator that coordinates extraction, LLM analysis,
    competitor benchmarking, and schema validation.
    """

    def __init__(self):
        self.extractor = WebsiteExtractor()

    async def analyze_link(self, url: str) -> LinkAnalysisResponse:
        start_time = time.time()
        start_dt = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. URL Validation & SSRF check
        clean_url, _ = validate_and_sanitize_url(url)
        logger.info(f"Initiating link analysis for: {clean_url}")

        # 2. Extract Website Content
        content: ExtractedWebsiteContent = await self.extractor.extract(clean_url)
        logger.info(f"Extracted {content.char_count} chars from {content.final_url} (status: {content.status_code})")

        # 3. LLM Processing
        llm = get_llm_service()
        raw_result: Dict[str, Any] = await llm.analyze_website(content)

        # 4. Parse & Normalize Brand Details
        raw_brand = raw_result.get("brand", {})
        brand_name = raw_brand.get("name") or content.detected_brand_name or "Target Brand"
        brand_category = raw_brand.get("category") or "Technology & Professional Services"
        brand_summary = raw_brand.get("summary") or content.meta_description or f"{brand_name} offers professional digital solutions."

        brand = BrandDetails(
            name=brand_name,
            category=brand_category,
            summary=brand_summary
        )

        # 5. Parse & Normalize Analysis Sections
        raw_analysis = raw_result.get("analysis", {})

        # Section 1: Competitor Analysis
        raw_comp_analysis = raw_analysis.get("competitor_analysis", {})
        validated_competitors = CompetitorService.ensure_valid_competitors(
            raw_competitors=raw_comp_analysis.get("competitors", []),
            brand_name=brand_name,
            category=brand_category,
            primary_service=raw_brand.get("category", "Digital Solutions")
        )

        brand_strengths_list = raw_comp_analysis.get("brand_strengths") or raw_comp_analysis.get("strengths") or ["Agile project execution", "Client-focused dedication"]

        competitor_analysis = CompetitorAnalysis(
            brand_overview=raw_comp_analysis.get("brand_overview", f"{brand_name} is a key player in the {brand_category} industry."),
            main_category=raw_comp_analysis.get("main_category", brand_category),
            main_products_and_services=raw_comp_analysis.get("main_products_and_services", [brand_category]),
            competitors=validated_competitors,
            brand_strengths=brand_strengths_list,
            strengths=brand_strengths_list,
            brand_advantages=raw_comp_analysis.get("brand_advantages", ["Faster time-to-market", "Tailored bespoke customer engagement"]),
            opportunities=raw_comp_analysis.get("opportunities", ["Expand organic SEO presence", "Broaden case studies & testimonials"]),
            source_note="Identified via contextual business intelligence and web content understanding."
        )

        # Section 2: Target Search Queries (Ensure exactly 5 items)
        raw_queries = raw_analysis.get("target_search_queries", [])
        search_queries = []
        platform_cycle = [
            ["Google"],
            ["Facebook", "Instagram"],
            ["Instagram"],
            ["LinkedIn"],
            ["X", "Google"]
        ]
        intent_cycle = ["Service Search", "Business Discovery", "Inspiration", "B2B Search", "Service Discovery"]

        for i in range(5):
            if i < len(raw_queries):
                q = raw_queries[i]
                search_queries.append(SearchQueryItem(
                    query=q.get("query", f"{brand_category} services"),
                    platforms=q.get("platforms") or platform_cycle[i],
                    intent=q.get("intent") or intent_cycle[i],
                    business_relevance=q.get("business_relevance", "High commercial intent capturing prospective buyers."),
                    target_audience=q.get("target_audience", "Prospective business clients and decision-makers."),
                    search_volume_note="Volume omitted per specification: unverified search volumes must not be hallucinated."
                ))
            else:
                search_queries.append(SearchQueryItem(
                    query=f"Top {brand_category.lower()} provider for businesses",
                    platforms=platform_cycle[i],
                    intent=intent_cycle[i],
                    business_relevance="Connects with active searchers seeking specialized services.",
                    target_audience="Founders, Executives, and Operations Directors",
                    search_volume_note="Volume omitted per specification: unverified search volumes must not be hallucinated."
                ))

        # Section 3: SEO Improvements
        raw_seo = raw_analysis.get("seo_improvements", {})
        raw_content = raw_seo.get("supporting_content", [])
        supporting_content = []
        for c in raw_content:
            supporting_content.append(SupportingContentItem(
                content_type=c.get("content_type", "Service Landing Page"),
                topic=c.get("topic", f"{brand_category} Capabilities"),
                purpose=c.get("purpose", "Increase organic visibility and answer search intent.")
            ))

        if not supporting_content:
            supporting_content = [
                SupportingContentItem(
                    content_type="Service Landing Page",
                    topic=f"Enterprise {brand_category} Solutions",
                    purpose="Capture high-intent transactional search traffic."
                ),
                SupportingContentItem(
                    content_type="FAQ Section",
                    topic="Project Delivery, SLA Guarantees, and Pricing",
                    purpose="Address customer hesitation and capture question-based queries."
                ),
                SupportingContentItem(
                    content_type="Industry-Specific Page",
                    topic=f"{brand_category} for High-Growth Startups",
                    purpose="Target specific market verticals with dedicated value propositions."
                ),
                SupportingContentItem(
                    content_type="Blog Topic",
                    topic=f"Key Trends Shaping Modern {brand_category}",
                    purpose="Drive top-of-funnel thought leadership and organic backlinks."
                )
            ]

        primary_kw = raw_seo.get("primary_keyword") or f"{brand_name.lower()} services"
        seo_improvements = SEOImprovements(
            primary_keyword=primary_kw,
            secondary_keywords=raw_seo.get("secondary_keywords") or [f"{primary_kw} solutions", f"best {primary_kw}"],
            long_tail_keywords=raw_seo.get("long_tail_keywords") or [f"affordable {primary_kw} for growing companies"],
            relevant_business_keywords=raw_seo.get("relevant_business_keywords") or ["digital solutions", "enterprise scalability"],
            recommended_title=raw_seo.get("recommended_title") or f"{primary_kw.title()} | {brand_name}",
            title_primary_keyword=raw_seo.get("title_primary_keyword") or primary_kw,
            title_improvement_rationale=raw_seo.get("title_improvement_rationale") or "Positions target primary keyword upfront to maximize SERP CTR.",
            meta_description=raw_seo.get("meta_description") or f"Discover premier {brand_category.lower()} by {brand_name}. Scale your business with proven solutions.",
            meta_description_summary=raw_seo.get("meta_description_summary") or f"Premier {brand_category.lower()} to scale your operations.",
            meta_description_keywords=raw_seo.get("meta_description_keywords") or [primary_kw, "business solutions"],
            supporting_content=supporting_content
        )

        # Section 4: Top 5 Services
        raw_services = raw_analysis.get("top_services", [])
        top_services = []
        for i, s in enumerate(raw_services[:5]):
            top_services.append(ServiceItem(
                service_name=s.get("service_name", f"Service {i+1}"),
                description=s.get("description", "Comprehensive service offering to accelerate client operations."),
                target_industry=s.get("target_industry", brand_category),
                target_customer=s.get("target_customer", "Enterprises and Startups"),
                main_benefit=s.get("main_benefit", "Reduces overhead and accelerates growth."),
                is_inferred=s.get("is_inferred", False)
            ))

        if not top_services:
            top_services.append(ServiceItem(
                service_name=f"Core {brand_category}",
                description="Turnkey digital and technical services tailored to client needs.",
                target_industry=brand_category,
                target_customer="Modern Growing Companies",
                main_benefit="Streamlines operations and expands technical capabilities.",
                is_inferred=True
            ))

        # Section 5: Target Audience
        raw_audience = raw_analysis.get("target_audience", {})
        customer_profiles = []
        for p in raw_audience.get("customer_profiles", []):
            customer_profiles.append(CustomerProfile(
                role_or_persona=p.get("role_or_persona", "Business Executive"),
                pain_points=p.get("pain_points", ["Resource bottlenecks"]),
                goals=p.get("goals", ["Improve efficiency and scale"])
            ))

        if not customer_profiles:
            customer_profiles = [
                CustomerProfile(
                    role_or_persona="Technical Founder / CTO",
                    pain_points=["Limited dev capacity", "High hiring costs"],
                    goals=["Rapid delivery of reliable digital infrastructure"]
                ),
                CustomerProfile(
                    role_or_persona="Operations Director",
                    pain_points=["Manual processes", "Fragmented legacy systems"],
                    goals=["Seamless system integration and operational speed"]
                )
            ]

        recommended_segments = []
        for seg in raw_audience.get("recommended_segments", []):
            recommended_segments.append(AudienceSegment(
                audience=seg.get("audience", f"Audience {len(recommended_segments)+1}"),
                business_type=seg.get("business_type", "Commercial Enterprise"),
                requirement=seg.get("requirement", "Scalable digital solutions")
            ))

        if len(recommended_segments) < 5:
            default_segments = [
                {"audience": "Audience 1", "business_type": "Small Businesses", "requirement": "Turnkey website & SEO foundation"},
                {"audience": "Audience 2", "business_type": "Startups", "requirement": "Rapid MVP development & scalable cloud setup"},
                {"audience": "Audience 3", "business_type": "Enterprise Companies", "requirement": "Custom software & high-availability integration"},
                {"audience": "Audience 4", "business_type": "Retail Businesses", "requirement": "E-commerce platform & payment integration"},
                {"audience": "Audience 5", "business_type": "Professional Services", "requirement": "Authoritative online presence & lead capture"},
            ]
            for seg in default_segments[len(recommended_segments):]:
                recommended_segments.append(AudienceSegment(
                    audience=seg["audience"],
                    business_type=seg["business_type"],
                    requirement=seg["requirement"]
                ))

        industries_list = raw_audience.get("industries") or raw_audience.get("industry_segments") or [brand_category, "Technology", "Commerce"]

        target_audience = TargetAudience(
            primary_audience=raw_audience.get("primary_audience", ["Founders & Executives", "Technical Directors"]),
            secondary_audience=raw_audience.get("secondary_audience", ["Product Managers", "Operations Leads"]),
            industries=industries_list,
            industry_segments=industries_list,
            business_types=raw_audience.get("business_types", ["B2B SaaS", "Startups", "Enterprise", "SMBs"]),
            customer_profiles=customer_profiles,
            geographical_focus=raw_audience.get("geographical_focus", "Global"),
            customer_needs=raw_audience.get("customer_needs", ["Reliable execution", "Clear milestone tracking", "Predictable ROI"]),
            potential_customer_interests=raw_audience.get("potential_customer_interests", ["Modern tech stacks", "AI automation", "Cloud scalability"]),
            recommended_segments=recommended_segments
        )

        analysis_result = AnalysisResult(
            competitor_analysis=competitor_analysis,
            target_search_queries=search_queries,
            seo_improvements=seo_improvements,
            top_services=top_services,
            target_audience=target_audience
        )

        execution_duration = round(time.time() - start_time, 2)
        model_name = getattr(llm, "model_name", "heuristic-engine")

        metadata = AnalysisMetadata(
            extracted_at=start_dt,
            http_status=content.status_code,
            page_title=content.title,
            character_count_analyzed=content.char_count,
            model_used=model_name,
            execution_time_seconds=execution_duration
        )

        return LinkAnalysisResponse(
            success=True,
            website=clean_url,
            brand=brand,
            analysis=analysis_result,
            metadata=metadata
        )
