import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "documentation" in data
        assert "analysis_endpoint" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "llm_provider" in data


@pytest.mark.asyncio
async def test_link_analysis_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"url": "https://example.com"}
        response = await client.post("/link-analysis", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Top-level structure verification
        assert data["success"] is True
        assert data["website"] == "https://example.com"
        assert "brand" in data
        assert "analysis" in data
        assert "metadata" in data

        # Brand details verification
        brand = data["brand"]
        assert brand["name"] != ""
        assert brand["category"] != ""
        assert brand["summary"] != ""

        analysis = data["analysis"]

        # Section 1: Competitor Analysis
        competitor_analysis = analysis["competitor_analysis"]
        assert "brand_overview" in competitor_analysis
        assert len(competitor_analysis["competitors"]) >= 3
        for comp in competitor_analysis["competitors"]:
            assert comp["name"] != ""
            assert comp["main_service"] != ""
            assert comp["target_market"] != ""
            assert len(comp["strengths"]) > 0
            assert "comparison_with_brand" in comp
            assert "your_brand_advantage" in comp["comparison_with_brand"]
            assert "opportunity_to_improve" in comp["comparison_with_brand"]

        assert len(competitor_analysis["brand_strengths"]) > 0
        assert len(competitor_analysis["brand_advantages"]) > 0
        assert len(competitor_analysis["opportunities"]) > 0

        # Section 2: Top 5 Target Search Queries
        queries = analysis["target_search_queries"]
        assert len(queries) == 5
        for q in queries:
            assert q["query"] != ""
            assert len(q["platforms"]) > 0
            assert q["intent"] != ""
            assert q["business_relevance"] != ""
            assert q["target_audience"] != ""
            assert "unverified search volumes must not be hallucinated" in q["search_volume_note"]

        # Section 3: SEO Improvements
        seo = analysis["seo_improvements"]
        assert seo["primary_keyword"] != ""
        assert len(seo["secondary_keywords"]) > 0
        assert len(seo["long_tail_keywords"]) > 0
        assert seo["recommended_title"] != ""
        assert seo["meta_description"] != ""
        assert len(seo["supporting_content"]) > 0
        for content in seo["supporting_content"]:
            assert content["content_type"] != ""
            assert content["topic"] != ""
            assert content["purpose"] != ""

        # Section 4: Top 5 Services
        services = analysis["top_services"]
        assert len(services) >= 1
        assert len(services) <= 5
        for svc in services:
            assert svc["service_name"] != ""
            assert svc["description"] != ""
            assert svc["target_industry"] != ""
            assert svc["target_customer"] != ""
            assert svc["main_benefit"] != ""
            assert isinstance(svc["is_inferred"], bool)

        # Section 5: Target Audience Identification
        audience = analysis["target_audience"]
        assert len(audience["primary_audience"]) > 0
        assert len(audience["secondary_audience"]) > 0
        assert len(audience["industries"]) > 0
        assert len(audience["business_types"]) > 0
        assert len(audience["customer_profiles"]) > 0
        assert len(audience["recommended_segments"]) == 5
        for seg in audience["recommended_segments"]:
            assert seg["audience"] != ""
            assert seg["business_type"] != ""
            assert seg["requirement"] != ""


@pytest.mark.asyncio
async def test_ssrf_blocked_localhost():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"url": "http://127.0.0.1:8000"}
        response = await client.post("/link-analysis", json=payload)
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "SSRF_FORBIDDEN"


@pytest.mark.asyncio
async def test_ssrf_blocked_cloud_metadata():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"url": "http://169.254.169.254/latest/meta-data/"}
        response = await client.post("/link-analysis", json=payload)
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "SSRF_FORBIDDEN"


@pytest.mark.asyncio
async def test_invalid_scheme():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"url": "ftp://example.com/file"}
        response = await client.post("/link-analysis", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_URL"


@pytest.mark.asyncio
async def test_missing_payload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/link-analysis", json={})
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
