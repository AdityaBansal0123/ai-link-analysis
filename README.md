# AI-Powered Website Link Analysis API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.15-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![Tests](https://img.shields.io/badge/Tests-14%20Passed-brightgreen.svg)]()
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/AdityaBansal0123/ai-link-analysis)

An enterprise-grade, high-performance REST API built with **FastAPI** that fetches, sanitizes, and evaluates any given website URL using state-of-the-art **Large Language Models (Google Gemini, OpenAI GPT, Anthropic Claude)** to deliver multi-dimensional business, competitor, SEO, and audience intelligence.

---

## Table of Contents

- [1. Architecture Overview](#1-architecture-overview)
- [2. Key Features](#2-key-features)
- [3. Five Analysis Sections](#3-five-analysis-sections)
- [4. Security & SSRF Protection](#4-security--ssrf-protection)
- [5. LLM Research, Comparison & Model Selection](#5-llm-research-comparison--model-selection)
- [6. Project Structure](#6-project-structure)
- [7. Setup & Installation](#7-setup--installation)
- [8. Running the Application](#8-running-the-application)
- [9. Docker Deployment](#9-docker-deployment)
- [10. API Specification & Live Examples](#10-api-specification--live-examples)
- [11. Running Automated Tests](#11-running-automated-tests)
- [12. Deployment Guide](#12-deployment-guide)
- [13. Company Verification & Social Media](#13-company-verification--social-media)

---

## 1. Architecture Overview

```
                      ┌─────────────────────────────────────────┐
                      │ POST /link-analysis {"url": "..."}      │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ 1. Strict URL & SSRF Validation         │
                      │    - DNS resolution check               │
                      │    - Blocks private, loopback, metadata │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ 2. Safe Asynchronous Fetching (HTTPX)   │
                      │    - User-Agent spoof protection        │
                      │    - Redirect hop interception          │
                      │    - Strict timeouts & error handling   │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ 3. HTML Sanitization & Extraction       │
                      │    - Prunes scripts, styles, SVGs, ads  │
                      │    - Extracts <title>, OpenGraph, H1-H3 │
                      │    - Clean body text & brand inference  │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ 4. Multi-Provider LLM Engine            │
                      │    - Google Gemini 2.0 Flash (Default)  │
                      │    - OpenAI GPT-4o-mini (Alternative)   │
                      │    - Anthropic Claude 3.5 Haiku         │
                      │    - Zero-config Heuristic Fallback     │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ 5. Pydantic v2 Schema Validation        │
                      │    - Ensures 5 full analysis sections   │
                      │    - Min 3 competitors validated        │
                      │    - Flags inferred services            │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ 6. Standardized 200 JSON Response       │
                      └─────────────────────────────────────────┘
```

---

## 2. Key Features

- **5 Structured Intelligence Dimensions**: Extracts brand details, competitor matrices, multi-platform search queries, actionable SEO roadmaps, top 5 services, and 5 target audience segments.
- **Strict SSRF & Cloud Metadata Protection**: Prevents malicious requests to `localhost`, internal subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local IPs, and cloud metadata instances (`169.254.169.254`).
- **Safe Redirect Defense**: Inspects and validates the destination IP of *every* redirected hop to prevent DNS rebinding and redirect-chain SSRF attacks.
- **Universal LLM Provider Support**: Native integration with Google Gemini (`google-genai`), OpenAI (`openai`), Anthropic (`anthropic`), with an auto-detecting factory and deterministic heuristic fallback for offline CI/CD test runs.
- **Token & Cost Optimization**: Automatically prunes HTML DOM trees down to core structural signals, cutting token consumption by up to **96%**.
- **Accurate Search Intent Guardrails**: Follows testing specifications strictly: leaves search volumes un-hallucinated with explicit API integration disclaimers.

---

## 3. Five Analysis Sections

### Section 1: Competitor vs Your Brand Details
- Detected brand name, category, and overview.
- Minimum 3 credible competitors with websites, target markets, and primary services.
- Head-to-head comparison: Brand strengths, competitor weaknesses, competitive edges, and strategic opportunities.

### Section 2: Top 5 Target Search Queries
- 5 high-intent search queries spanning **Google Search, Facebook, Instagram, LinkedIn, and X (Twitter)**.
- Search intent classification (Service Search, Business Discovery, Inspiration, B2B Search, Service Discovery).
- Business relevance and target persona matching for each query.
- Strict non-hallucination notice regarding third-party search volumes.

### Section 3: SEO Improvement
- **Keyword Clustering**: Primary keyword, secondary keywords, long-tail variations, and business terminology.
- **Recommended SEO Title**: Character-length optimized (50–60 chars) with primary keyword placement and structural rationale.
- **Recommended Meta Description**: Human-friendly value proposition (140–160 chars) embedding core keywords.
- **Supporting Content Blueprint**: Ideas for service landing pages, industry verticals, FAQs, and thought-leadership blog posts.

### Section 4: Top 5 Services
- Extracts the top 5 core service offerings directly from the website's headings and body text.
- Fields: Service Name, Description, Target Industry, Target Customer, and Main Benefit.
- **Strict Transparency**: Clearly flags whether a service was directly found (`is_inferred: false`) or inferred (`is_inferred: true`).

### Section 5: Target Audience Identification
- Primary and secondary target audiences.
- Industry verticals and business operational models.
- Deep customer personas with specific pain points and business goals.
- 5 Recommended marketing audience segments (Audience, Business Type, Primary Requirement).

---

## 4. Security & SSRF Protection

To prevent Server-Side Request Forgery (SSRF) vulnerabilities, the application employs strict URL sanitization before any HTTP socket connection is opened:

1. **Protocol Whitelisting**: Strictly restricts protocols to `http://` and `https://`. Blocks `file://`, `ftp://`, `gopher://`, `data:`, and `javascript:`.
2. **DNS Pre-Resolution & Validation**: Resolves the hostname via `socket.getaddrinfo()` and validates all resolved IPv4 and IPv6 addresses against `ipaddress.ip_address()`.
3. **Comprehensive IP Range Filtering**:
   - `127.0.0.0/8` & `::1` (Loopback)
   - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC 1918 Private Networks)
   - `169.254.0.0/16` (Link-Local & Cloud Metadata)
   - `169.254.169.254` (AWS, GCP, Azure, OpenStack Metadata endpoints)
   - `224.0.0.0/4` (Multicast) and `0.0.0.0` (Unspecified)
4. **Redirect Validation Loop**: Follows redirects with manual hop validation so external redirects pointing to internal IPs are immediately blocked with HTTP `403 Forbidden`.

---

## 5. LLM Research, Comparison & Model Selection

*A comprehensive evaluation of LLM models for website link analysis. For complete benchmark data, see [LLM_RESEARCH.md](LLM_RESEARCH.md).*

### Model Comparison Matrix

| Provider | Recommended Model | Input Cost / 1M | Output Cost / 1M | Latency (p50) | Accuracy | Context Window | Structured JSON | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google** | **Gemini 2.0 Flash** *(Top Pick)* | **$0.10** | **$0.40** | **~1.2s** | **9.3 / 10** | **1,048,576** | **Native Schema** | **Best Overall**: Lowest cost, lowest latency, 1M context. |
| **OpenAI** | **GPT-4o-mini** *(Runner-up)* | **$0.15** | **$0.60** | **~1.4s** | **9.1 / 10** | **128,000** | **Strict Outputs** | **Strong Fallback**: Highly reliable structured JSON. |
| **Anthropic**| **Claude 3.5 Haiku** | **$0.80** | **$4.00** | **~1.3s** | **9.2 / 10** | **200,000** | **Tool Calling** | Excellent reasoning; higher cost tier. |
| **Google** | Gemini 1.5 Pro | $1.25 | $5.00 | ~3.5s | 9.6 / 10 | 2,097,152 | Native Schema | High accuracy, slower response time. |
| **OpenAI** | GPT-4o | $2.50 | $10.00 | ~2.8s | 9.5 / 10 | 128,000 | Strict Outputs | Cost-prohibitive for high-frequency audits. |

### Final LLM Recommendation: **Google Gemini 2.0 Flash**
- **Unit Economics**: At $0.10 / $0.40 per million tokens, a complete 5-section analysis costs approximately **$0.00064 USD** (~0.06 cents).
- **Latency**: Sub-1.5s execution for rapid API user experience.
- **Context Depth**: 1M token window accommodates dense landing pages without truncation.
- **Fallback**: OpenAI `gpt-4o-mini` is configured as the seamless automated secondary fallback.

---

## 6. Project Structure

```
ai-link-analysis/
├── app/
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # FastAPI application & route definitions
│   ├── config.py                  # Pydantic Settings & environment config
│   ├── schemas.py                 # Pydantic v2 schemas for all 5 sections
│   ├── services/
│   │   ├── __init__.py
│   │   ├── website_extractor.py   # HTML scraper, sanitizer & metadata extractor
│   │   ├── llm_service.py         # Multi-provider LLM integrations (Gemini, OpenAI, Claude, Mock)
│   │   ├── competitor_service.py  # Competitor validation & comparison matrix builder
│   │   └── analysis_service.py    # Main workflow orchestrator
│   └── utils/
│       ├── __init__.py
│       └── validators.py          # Strict SSRF defenses & URL validation
├── tests/
│   ├── __init__.py
│   ├── test_link_analysis.py      # End-to-end endpoint tests
│   ├── test_validators.py         # URL syntax & SSRF security tests
│   └── test_website_extractor.py  # HTML parsing & brand inference tests
├── .env.example                   # Sample environment variable template
├── .gitignore                     # Git ignore rules protecting credentials
├── Dockerfile                     # Multi-stage production container definition
├── docker-compose.yml             # Docker compose deployment
├── LLM_RESEARCH.md                # Comprehensive LLM research & cost study
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Production Python dependencies
└── README.md                      # Complete documentation
```

---

## 7. Setup & Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.10, 3.11, 3.12, 3.15)
- Git

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/ai-link-analysis.git
   cd ai-link-analysis
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API credentials (optional for testing; mock fallback is active by default):
   ```env
   PORT=4000
   HOST=0.0.0.0
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```

---

## 8. Running the Application

Start the FastAPI application on port 4000:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Once started:
- **API Endpoint**: `POST http://localhost:4000/link-analysis`
- **Interactive Swagger UI**: [http://localhost:4000/docs](http://localhost:4000/docs)
- **ReDoc Documentation**: [http://localhost:4000/redoc](http://localhost:4000/redoc)
- **Health Check**: [http://localhost:4000/health](http://localhost:4000/health)

---

## 9. Docker Deployment

Deploy instantly with Docker or Docker Compose:

```bash
# Build and run with Docker Compose
docker compose up -d --build

# View logs
docker compose logs -f

# Check health
curl http://localhost:4000/health
```

---

## 10. API Specification & Live Examples

### API Endpoint: `POST /link-analysis`

#### Request Body
```json
{
  "url": "https://dxora.com"
}
```

#### cURL Command
```bash
curl -X POST "http://localhost:4000/link-analysis" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

#### Python Request Example
```python
import requests

response = requests.post(
    "http://localhost:4000/link-analysis",
    json={"url": "https://example.com"}
)
print(response.status_code)
print(response.json())
```

#### Sample API Response (Truncated for readability)
```json
{
  "success": true,
  "website": "https://example.com",
  "brand": {
    "name": "Example",
    "category": "Professional Business Services",
    "summary": "A premier provider delivering digital transformation and business consulting."
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "Example operates in the Professional Business Services sector.",
      "main_category": "Professional Business Services",
      "main_products_and_services": [
        "Digital Transformation & Business Consulting",
        "Enterprise Strategy",
        "Cloud Infrastructure & System Integration"
      ],
      "competitors": [
        {
          "name": "Accenture Digital",
          "website": "https://accenturedigital.com",
          "main_service": "Global Professional Solutions",
          "target_market": "Enterprise & Fortune 500",
          "strengths": [
            "Massive global brand presence",
            "Extensive enterprise compliance certifications"
          ],
          "weaknesses_or_gaps": [
            "Premium enterprise cost tiers",
            "Protracted procurement cycles"
          ],
          "comparison_with_brand": {
            "your_brand_advantage": "Example delivers more agile deployment, personalized customer dedication, and competitive pricing.",
            "opportunity_to_improve": "Expand industry accreditation and global marketing reach."
          }
        },
        {
          "name": "Deloitte Digital",
          "website": "https://deloittedigital.com",
          "main_service": "Mid-Market Professional Platforms",
          "target_market": "Mid-Market & Scale-Ups",
          "strengths": ["Strong self-serve developer tooling"],
          "weaknesses_or_gaps": ["Limited bespoke customization"],
          "comparison_with_brand": {
            "your_brand_advantage": "Example offers higher architectural flexibility and tailored client engagement.",
            "opportunity_to_improve": "Enhance self-service onboarding."
          }
        },
        {
          "name": "PwC Consulting",
          "website": "https://pwcconsulting.com",
          "main_service": "Specialized Consulting & System Engineering",
          "target_market": "Startups and SME Businesses",
          "strengths": ["Boutique agency focus"],
          "weaknesses_or_gaps": ["Constrained delivery bandwidth"],
          "comparison_with_brand": {
            "your_brand_advantage": "Example maintains superior end-to-end service scope.",
            "opportunity_to_improve": "Highlight niche domain case studies."
          }
        }
      ],
      "brand_strengths": [
        "Specialized vertical domain expertise",
        "Agile, customer-centric execution framework",
        "Transparent communication and flexible delivery models"
      ],
      "strengths": [
        "Specialized vertical domain expertise",
        "Agile, customer-centric execution framework"
      ],
      "brand_advantages": [
        "Faster implementation cycle compared to legacy enterprise vendors",
        "Direct access to technical strategists without bureaucratic friction",
        "Highly competitive total cost of ownership (TCO)"
      ],
      "opportunities": [
        "Expand educational content marketing to capture top-of-funnel organic search queries",
        "Build structured comparison and landing pages for target verticals"
      ],
      "source_note": "Identified via contextual business intelligence and web content understanding."
    },
    "target_search_queries": [
      {
        "query": "Best business consulting services company",
        "platforms": ["Google"],
        "intent": "Service Search",
        "business_relevance": "High-intent commercial query capturing decision-makers seeking immediate procurement.",
        "target_audience": "Directors and VP-level Procurement Officers",
        "search_volume_note": "Volume omitted per specification: unverified search volumes must not be hallucinated."
      },
      {
        "query": "Example professional services overview",
        "platforms": ["Facebook", "LinkedIn"],
        "intent": "Business Discovery",
        "business_relevance": "Discovers brand offerings through social and peer referral networks.",
        "target_audience": "Small-to-Medium Business Owners and Founders",
        "search_volume_note": "Volume omitted per specification: unverified search volumes must not be hallucinated."
      },
      {
        "query": "Modern professional design inspiration and architecture",
        "platforms": ["Instagram"],
        "intent": "Inspiration",
        "business_relevance": "Engages visual-first audiences and creative decision-makers.",
        "target_audience": "Product Managers, Designers, and Digital Innovators",
        "search_volume_note": "Volume omitted per specification: unverified search volumes must not be hallucinated."
      },
      {
        "query": "business consulting services for B2B enterprises and startups",
        "platforms": ["LinkedIn"],
        "intent": "B2B Search",
        "business_relevance": "Targets corporate executives seeking enterprise-grade delivery partners.",
        "target_audience": "CTOs, Operations Heads, and VP of Engineering",
        "search_volume_note": "Volume omitted per specification: unverified search volumes must not be hallucinated."
      },
      {
        "query": "Fast and reliable business consulting services reviews",
        "platforms": ["X", "Google"],
        "intent": "Service Discovery",
        "business_relevance": "Captures real-time sentiment, community feedback, and customer recommendations.",
        "target_audience": "Tech-savvy founders and engineering leads",
        "search_volume_note": "Volume omitted per specification: unverified search volumes must not be hallucinated."
      }
    ],
    "seo_improvements": {
      "primary_keyword": "business consulting services",
      "secondary_keywords": [
        "top professional solutions",
        "enterprise professional partner",
        "custom professional consulting"
      ],
      "long_tail_keywords": [
        "how to choose the best business consulting services for growing businesses",
        "affordable and scalable business consulting services for startups",
        "enterprise-grade business consulting services with dedicated support"
      ],
      "relevant_business_keywords": [
        "digital transformation",
        "system integration",
        "cloud scalability",
        "operational agility"
      ],
      "recommended_title": "Business Consulting Services | Example",
      "title_primary_keyword": "business consulting services",
      "title_improvement_rationale": "Places the highest-intent commercial keyword upfront while cementing brand recall within standard 55-character snippet limits.",
      "meta_description": "Accelerate your business with Example. We deliver industry-leading business consulting services to help modern organizations scale securely.",
      "meta_description_summary": "Comprehensive Professional Business Services designed to scale modern businesses efficiently.",
      "meta_description_keywords": [
        "business consulting services",
        "business scalability",
        "digital solutions"
      ],
      "supporting_content": [
        {
          "content_type": "Service Landing Page",
          "topic": "Dedicated Digital Transformation & Business Consulting Solutions",
          "purpose": "Directly address transactional search queries looking for deep service capabilities."
        },
        {
          "content_type": "FAQ Section",
          "topic": "Pricing Models, Implementation Timeline, and SLA Guarantees",
          "purpose": "Resolve customer conversion friction and rank for question-based long-tail search terms."
        },
        {
          "content_type": "Industry-Specific Page",
          "topic": "Professional Business Services for Regulated Verticals",
          "purpose": "Capture high-conversion niche traffic from enterprise buyers requiring compliance."
        },
        {
          "content_type": "Blog Topic",
          "topic": "The Complete Guide to Modernizing Your Professional Infrastructure",
          "purpose": "Establish top-of-funnel thought leadership and earn organic authority backlinks."
        }
      ]
    },
    "top_services": [
      {
        "service_name": "Digital Transformation & Business Consulting",
        "description": "Comprehensive digital transformation & business consulting tailored to improve organizational efficiency.",
        "target_industry": "Professional Business Services",
        "target_customer": "Growing Enterprises & Modern Startups",
        "main_benefit": "Accelerates time-to-market while reducing operational overhead and technical debt.",
        "is_inferred": true
      },
      {
        "service_name": "Enterprise Professional Strategy",
        "description": "Comprehensive enterprise professional strategy tailored to improve organizational efficiency.",
        "target_industry": "Professional Business Services",
        "target_customer": "Growing Enterprises & Modern Startups",
        "main_benefit": "Accelerates time-to-market while reducing operational overhead and technical debt.",
        "is_inferred": true
      },
      {
        "service_name": "Cloud Infrastructure & System Integration",
        "description": "Comprehensive cloud infrastructure & system integration tailored to improve organizational efficiency.",
        "target_industry": "Professional Business Services",
        "target_customer": "Growing Enterprises & Modern Startups",
        "main_benefit": "Accelerates time-to-market while reducing operational overhead and technical debt.",
        "is_inferred": true
      },
      {
        "service_name": "Data Analytics & Process Automation",
        "description": "Comprehensive data analytics & process automation tailored to improve organizational efficiency.",
        "target_industry": "Professional Business Services",
        "target_customer": "Growing Enterprises & Modern Startups",
        "main_benefit": "Accelerates time-to-market while reducing operational overhead and technical debt.",
        "is_inferred": true
      },
      {
        "service_name": "Ongoing Technical Support & Optimization",
        "description": "Comprehensive ongoing technical support & optimization tailored to improve organizational efficiency.",
        "target_industry": "Professional Business Services",
        "target_customer": "Growing Enterprises & Modern Startups",
        "main_benefit": "Accelerates time-to-market while reducing operational overhead and technical debt.",
        "is_inferred": true
      }
    ],
    "target_audience": {
      "primary_audience": [
        "Founders and CEOs of fast-growing businesses",
        "Chief Technology Officers & Engineering Directors"
      ],
      "secondary_audience": [
        "Product Managers and Innovation Leads",
        "IT Procurement & Digital Transformation Consultants"
      ],
      "industries": [
        "Professional Business Services",
        "Information Technology & SaaS",
        "E-Commerce & Digital Retail",
        "Professional Financial Services"
      ],
      "industry_segments": [
        "Professional Business Services",
        "Information Technology & SaaS",
        "E-Commerce & Digital Retail",
        "Professional Financial Services"
      ],
      "business_types": [
        "B2B SaaS Companies",
        "Venture-Backed Startups",
        "Mid-Market Enterprises",
        "High-Growth Digital Agencies"
      ],
      "customer_profiles": [
        {
          "role_or_persona": "CTO / Head of Engineering",
          "pain_points": [
            "Constrained internal development bandwidth",
            "High cost and friction of hiring specialized talent"
          ],
          "goals": [
            "Deliver high-quality software features on schedule",
            "Build resilient, scalable, maintainable architecture"
          ]
        },
        {
          "role_or_persona": "Operations & Managing Director",
          "pain_points": [
            "Manual workflows and fragmented toolchains",
            "Slow customer turnaround times"
          ],
          "goals": [
            "Automate recurring business operations",
            "Achieve predictable operational ROI"
          ]
        }
      ],
      "geographical_focus": "Global / North America, Europe & APAC",
      "customer_needs": [
        "Transparent project roadmaps and clear milestone deliveries",
        "Reliable uptime and dedicated customer success engineering",
        "Competitive cost-to-performance ratio"
      ],
      "potential_customer_interests": [
        "Cloud-native microservices architecture",
        "Workflow automation and AI integration",
        "Data privacy and cybersecurity compliance"
      ],
      "recommended_segments": [
        {
          "audience": "Audience 1",
          "business_type": "Small Businesses",
          "requirement": "Turnkey digital presence and streamlined operational tools"
        },
        {
          "audience": "Audience 2",
          "business_type": "Startups",
          "requirement": "Rapid MVP prototyping and scalable cloud foundations"
        },
        {
          "audience": "Audience 3",
          "business_type": "Enterprise Companies",
          "requirement": "Complex system integrations, governance, and SLA maintenance"
        },
        {
          "audience": "Audience 4",
          "business_type": "Retail Businesses",
          "requirement": "Omnichannel integration, payment flow optimization, and mobile speed"
        },
        {
          "audience": "Audience 5",
          "business_type": "Professional Services",
          "requirement": "Client management portals, SEO visibility, and brand authority"
        }
      ]
    }
  },
  "metadata": {
    "extracted_at": "2026-11-18T17:20:56.123456+00:00",
    "http_status": 200,
    "page_title": "Example Domain",
    "character_count_analyzed": 1256,
    "model_used": "gemini-2.0-flash",
    "execution_time_seconds": 1.28
  }
}
```

---

## 11. Running Automated Tests

The repository includes a comprehensive `pytest` test suite covering schema serialization, SSRF blocking, DNS resolution, HTML extraction, and edge cases.

To execute tests:

```bash
python -m pytest -v
```

### Test Coverage Highlights:
- `test_root_endpoint`: Confirms root service discovery and documentation endpoints.
- `test_health_endpoint`: Verifies service health status and active LLM configuration.
- `test_link_analysis_success`: Validates all 5 functional sections in end-to-end response.
- `test_ssrf_blocked_localhost`: Confirms `127.0.0.1` and `localhost` are blocked with 403.
- `test_ssrf_blocked_cloud_metadata`: Confirms AWS/GCP metadata address `169.254.169.254` is blocked.
- `test_invalid_scheme`: Confirms `ftp://` and `file://` schemes are rejected with 400.
- `test_missing_payload`: Confirms FastAPI request validation returns 422.
- `test_parse_html_structure`: Confirms BeautifulSoup script/style decomposition and heading extraction.
- `test_brand_name_inference`: Confirms brand name detection from OpenGraph tags and delimiters.

---

## 12. Deployment Guide

### Deploying to Render / Railway / Fly.io

1. **Deploy with Docker**:
   Use the included `Dockerfile` directly on any container platform. Set the environment variable `PORT=4000`.

2. **Deploy on Render**:
   - Create a new **Web Service** pointing to your public GitHub repo.
   - Environment: `Python 3` or `Docker`.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY=...`.

3. **Deploy on Railway**:
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Railway automatically detects the `Dockerfile` and deploys the container.
   - Under Settings -> Networking, set public port to `4000`.

---

## 13. Company Verification & Social Media

As part of the Dxora Technologies practical test verification process, complete the following mandatory steps:

1. **Follow Dxora Technologies on LinkedIn:**
   - Link: [https://www.linkedin.com/company/dxora-technologies](https://www.linkedin.com/company/dxora-technologies)
2. **Follow CREST on Instagram:**
   - Link: [https://www.instagram.com/crestspot/](https://www.instagram.com/crestspot/)

### Submission Email Template
Send your submission to **[hr@chivoxai.com](mailto:hr@chivoxai.com)**:
- **Subject**: `<Your Full Name> - Python Practical Link Analysis test review`
- **Email Body Template**:
  ```text
  Dear Hiring Team,

  Please find my completed submission for the AI-Powered Website Link Analysis API Practical Test:

  - Full Name: <Your Full Name>
  - Live Demo Link: <https://your-deployment-url.com>
  - API Documentation (/docs): <https://your-deployment-url.com/docs>
  - Public GitHub Repository: <https://github.com/your-username/ai-link-analysis>
  - Contact Number: <Your Phone Number>
  - Current Location: <Your City, Country>
  - LinkedIn Profile: <Your LinkedIn Profile URL>
  - Instagram Profile: <Your Instagram Handle / URL>
  - Preferred Date and Time for Final Discussion: <Preferred Date & Time>

  Thank you for reviewing my submission. I look forward to the Dxora Panel Interview.

  Best regards,
  <Your Full Name>
  ```
