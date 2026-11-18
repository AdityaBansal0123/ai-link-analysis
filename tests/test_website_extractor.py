import pytest
from app.services.website_extractor import WebsiteExtractor, ExtractedWebsiteContent


def test_parse_html_structure():
    extractor = WebsiteExtractor()
    sample_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Dxora Technologies - Cloud & AI Consulting</title>
        <meta name="description" content="Dxora Technologies builds scalable enterprise AI systems.">
        <meta name="keywords" content="AI, Cloud, FastAPI, Python">
        <meta property="og:site_name" content="Dxora Technologies">
    </head>
    <body>
        <header>
            <nav>
                <a href="/about">About Us</a>
                <a href="/services">Services</a>
                <a href="/contact">Contact</a>
            </nav>
        </header>
        <main>
            <h1>Engineering Tomorrow's Cloud & AI</h1>
            <section>
                <h2>Custom Software Engineering</h2>
                <p>We build full-stack web and cloud solutions for modern scale.</p>
            </section>
            <section>
                <h2>Machine Learning Automation</h2>
                <p>Deploy LLMs and machine learning pipelines securely into production.</p>
            </section>
        </main>
        <script>console.log("Noise");</script>
        <style>.hidden { display: none; }</style>
    </body>
    </html>
    """
    content: ExtractedWebsiteContent = extractor.parse_html(
        url="https://dxora.com",
        html_text=sample_html,
        status_code=200
    )

    assert content.title == "Dxora Technologies - Cloud & AI Consulting"
    assert content.meta_description == "Dxora Technologies builds scalable enterprise AI systems."
    assert "AI" in content.meta_keywords
    assert content.detected_brand_name == "Dxora Technologies"
    assert "Engineering Tomorrow's Cloud & AI" in content.headings["h1"]
    assert "Custom Software Engineering" in content.headings["h2"]
    assert "Machine Learning Automation" in content.headings["h2"]
    assert "console.log" not in content.cleaned_text
    assert "display: none" not in content.cleaned_text
    assert "About Us" in content.navigation_links
    assert content.char_count > 0


def test_brand_name_inference():
    extractor = WebsiteExtractor()

    # Case 1: OpenGraph site_name
    assert extractor._infer_brand_name("https://example.com", "Page Title", {"og:site_name": "Acme Corp"}) == "Acme Corp"

    # Case 2: Title with delimiter
    assert extractor._infer_brand_name("https://example.com", "High Performance Cloud | CloudScale", {}) in ["High Performance Cloud", "CloudScale"]

    # Case 3: Domain fallback
    assert extractor._infer_brand_name("https://www.stripe.com/pricing", "", {}) == "Stripe"
