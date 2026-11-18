"""
Interactive Web UI for live browser-based testing of the Link Analysis API.
"""

HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI-Powered Website Link Analysis API</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .gradient-header {
      background: linear-gradient(135deg, #1e1e38 0%, #0f172a 100%);
    }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
  <!-- Header -->
  <header class="gradient-header border-b border-slate-800 py-6 px-6 shadow-lg">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <div class="flex items-center gap-3">
          <span class="text-3xl">🔍</span>
          <h1 class="text-2xl font-bold tracking-tight text-white">Website Link Analysis API</h1>
          <span class="bg-indigo-500/20 text-indigo-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-indigo-500/30">FastAPI</span>
          <span class="bg-emerald-500/20 text-emerald-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-emerald-500/30">v1.0.0</span>
        </div>
        <p class="text-slate-400 text-sm mt-1">AI-Powered Competitor, SEO, Search Query & Target Audience Intelligence</p>
      </div>
      <div class="flex gap-2">
        <a href="/docs" target="_blank" class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow">
          <span>Swagger /docs</span>
          <span>↗</span>
        </a>
        <a href="/health" target="_blank" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium px-4 py-2 rounded-lg transition-colors border border-slate-700">
          Health
        </a>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-6xl mx-auto p-6 space-y-6">
    <!-- Search Bar Card -->
    <div class="bg-slate-800/80 backdrop-blur rounded-xl p-6 border border-slate-700 shadow-xl">
      <h2 class="text-lg font-semibold text-white mb-2">Analyze Any Website URL</h2>
      <p class="text-sm text-slate-400 mb-4">Enter a public website URL below to extract business insights across 5 structured intelligence dimensions.</p>
      
      <form id="analyzeForm" class="flex flex-col sm:flex-row gap-3">
        <input 
          type="url" 
          id="urlInput" 
          required 
          placeholder="https://example.com" 
          value="https://example.com"
          class="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-base"
        />
        <button 
          type="submit" 
          id="submitBtn"
          class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg disabled:opacity-50"
        >
          <span id="btnText">Analyze Website</span>
          <span id="btnSpinner" class="hidden animate-spin">⏳</span>
        </button>
      </form>

      <!-- Quick presets -->
      <div class="mt-3 flex items-center gap-2 text-xs text-slate-400">
        <span>Try sample:</span>
        <button type="button" onclick="setPreset('https://example.com')" class="text-indigo-400 hover:underline">example.com</button>
        <span>•</span>
        <button type="button" onclick="setPreset('https://dxora.com')" class="text-indigo-400 hover:underline">dxora.com</button>
        <span>•</span>
        <button type="button" onclick="setPreset('https://stripe.com')" class="text-indigo-400 hover:underline">stripe.com</button>
      </div>
    </div>

    <!-- Error Banner -->
    <div id="errorBanner" class="hidden bg-rose-950/60 border border-rose-800 text-rose-200 p-4 rounded-xl flex items-start gap-3">
      <span class="text-xl">⚠️</span>
      <div>
        <div class="font-semibold text-rose-100" id="errorCode">Error</div>
        <div class="text-sm" id="errorMessage">An error occurred.</div>
      </div>
    </div>

    <!-- Results Container -->
    <div id="resultsContainer" class="hidden space-y-6">
      <!-- Section 0: Brand Summary Header -->
      <div class="bg-gradient-to-r from-indigo-950/50 to-slate-800/80 rounded-xl p-6 border border-indigo-900/50 shadow-lg">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wider text-indigo-400 font-semibold">Analyzed Brand</div>
            <h2 id="brandName" class="text-2xl font-bold text-white mt-1">Brand Name</h2>
            <div id="brandCategory" class="inline-block bg-indigo-500/20 text-indigo-300 text-xs font-semibold px-2.5 py-0.5 rounded-full mt-2">Category</div>
            <p id="brandSummary" class="text-slate-300 text-sm mt-3 max-w-3xl leading-relaxed"></p>
          </div>
          <div class="bg-slate-900/80 p-4 rounded-lg border border-slate-700/60 text-xs space-y-1.5 min-w-[200px]">
            <div class="text-slate-400 font-medium">Metadata</div>
            <div class="text-slate-300">Model: <span id="metaModel" class="font-mono text-indigo-300"></span></div>
            <div class="text-slate-300">Duration: <span id="metaTime" class="font-mono text-emerald-400"></span></div>
            <div class="text-slate-300">Analyzed Size: <span id="metaChars" class="font-mono text-slate-200"></span> chars</div>
          </div>
        </div>
      </div>

      <!-- Section 1: Competitor Analysis -->
      <div class="bg-slate-800/70 rounded-xl p-6 border border-slate-700 shadow-md">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xl">⚔️</span>
          <h3 class="text-lg font-bold text-white">Section 1: Competitor vs Your Brand Details</h3>
        </div>
        <p id="brandOverview" class="text-slate-300 text-sm mb-4"></p>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm border-collapse">
            <thead>
              <tr class="border-b border-slate-700 text-slate-400 text-xs uppercase bg-slate-900/50">
                <th class="p-3">Competitor</th>
                <th class="p-3">Main Service</th>
                <th class="p-3">Target Market</th>
                <th class="p-3">Key Strengths</th>
                <th class="p-3">Your Brand Advantage</th>
                <th class="p-3">Opportunity</th>
              </tr>
            </thead>
            <tbody id="competitorsTableBody" class="divide-y divide-slate-700/50">
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 2: Top 5 Target Search Queries -->
      <div class="bg-slate-800/70 rounded-xl p-6 border border-slate-700 shadow-md">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xl">🎯</span>
          <h3 class="text-lg font-bold text-white">Section 2: Top 5 Target Search Queries</h3>
        </div>
        <p class="text-xs text-slate-400 mb-4">Targeted customer search queries spanning Google, Facebook, Instagram, LinkedIn, and X.</p>
        
        <div id="searchQueriesList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        </div>
      </div>

      <!-- Section 3: SEO Improvements -->
      <div class="bg-slate-800/70 rounded-xl p-6 border border-slate-700 shadow-md space-y-4">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xl">🚀</span>
          <h3 class="text-lg font-bold text-white">Section 3: SEO Improvement Recommendations</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Recommended Title -->
          <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-700/60">
            <div class="text-xs text-indigo-400 font-semibold uppercase">Recommended SEO Title</div>
            <div id="seoTitle" class="text-base font-bold text-white mt-1"></div>
            <p id="seoTitleRationale" class="text-xs text-slate-400 mt-2"></p>
          </div>

          <!-- Recommended Meta Description -->
          <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-700/60">
            <div class="text-xs text-emerald-400 font-semibold uppercase">Recommended Meta Description</div>
            <div id="seoMetaDesc" class="text-sm text-slate-200 mt-1 italic"></div>
            <p id="seoMetaSummary" class="text-xs text-slate-400 mt-2"></p>
          </div>
        </div>

        <!-- Keywords -->
        <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-700/60">
          <div class="text-xs text-slate-400 font-semibold uppercase mb-2">Keyword Intelligence</div>
          <div class="space-y-2">
            <div>
              <span class="text-xs text-slate-400">Primary:</span>
              <span id="seoPrimaryKw" class="inline-block bg-indigo-500/20 text-indigo-300 text-xs px-2.5 py-0.5 rounded font-mono ml-2"></span>
            </div>
            <div>
              <span class="text-xs text-slate-400">Secondary:</span>
              <span id="seoSecondaryKw" class="ml-2"></span>
            </div>
            <div>
              <span class="text-xs text-slate-400">Long-Tail:</span>
              <span id="seoLongTailKw" class="ml-2"></span>
            </div>
          </div>
        </div>

        <!-- Supporting Content -->
        <div>
          <div class="text-xs text-slate-400 font-semibold uppercase mb-2">Supporting Content Blueprint</div>
          <div id="supportingContentList" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
        </div>
      </div>

      <!-- Section 4: Top 5 Services -->
      <div class="bg-slate-800/70 rounded-xl p-6 border border-slate-700 shadow-md">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xl">💼</span>
          <h3 class="text-lg font-bold text-white">Section 4: Top 5 Services Identified</h3>
        </div>
        <div id="servicesList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
      </div>

      <!-- Section 5: Target Audience Identification -->
      <div class="bg-slate-800/70 rounded-xl p-6 border border-slate-700 shadow-md space-y-4">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xl">👥</span>
          <h3 class="text-lg font-bold text-white">Section 5: Target Audience Identification</h3>
        </div>

        <!-- 5 Marketing Segments -->
        <div>
          <div class="text-xs text-slate-400 font-semibold uppercase mb-3">5 Recommended Audience Segments</div>
          <div id="audienceSegmentsList" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3"></div>
        </div>

        <!-- Personas & Needs -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-700/60">
            <div class="text-xs text-indigo-400 font-semibold uppercase mb-2">Buyer Personas</div>
            <div id="personasContainer" class="space-y-3"></div>
          </div>
          <div class="bg-slate-900/60 p-4 rounded-lg border border-slate-700/60">
            <div class="text-xs text-emerald-400 font-semibold uppercase mb-2">Customer Needs & Challenges</div>
            <ul id="customerNeedsList" class="list-disc list-inside text-sm text-slate-300 space-y-1"></ul>
          </div>
        </div>
      </div>

      <!-- Raw JSON View Toggle -->
      <div class="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
        <details>
          <summary class="cursor-pointer text-sm font-semibold text-indigo-400 hover:text-indigo-300 select-none">
            Toggle Raw Structured JSON Response
          </summary>
          <pre id="rawJson" class="mt-4 p-4 bg-slate-950 rounded-lg text-xs font-mono text-emerald-400 overflow-x-auto max-h-96"></pre>
        </details>
      </div>
    </div>
  </main>

  <script>
    function setPreset(url) {
      document.getElementById('urlInput').value = url;
    }

    const form = document.getElementById('analyzeForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const errorBanner = document.getElementById('errorBanner');
    const errorCode = document.getElementById('errorCode');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContainer = document.getElementById('resultsContainer');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const url = document.getElementById('urlInput').value.trim();
      if (!url) return;

      // Loading State
      submitBtn.disabled = true;
      btnText.textContent = "Analyzing...";
      btnSpinner.classList.remove('hidden');
      errorBanner.classList.add('hidden');
      resultsContainer.classList.add('hidden');

      try {
        const res = await fetch('/link-analysis', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ url: url })
        });

        const data = await res.json();

        if (!res.ok || !data.success) {
          const err = data.error || {};
          errorCode.textContent = `Error ${res.status}: ${err.code || 'REQUEST_FAILED'}`;
          errorMessage.textContent = err.message || 'Failed to analyze website.';
          errorBanner.classList.remove('hidden');
          return;
        }

        renderResults(data);
      } catch (err) {
        errorCode.textContent = "Network Error";
        errorMessage.textContent = err.message || "Could not reach the server.";
        errorBanner.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        btnText.textContent = "Analyze Website";
        btnSpinner.classList.add('hidden');
      }
    });

    function renderResults(data) {
      const brand = data.brand || {};
      const analysis = data.analysis || {};
      const meta = data.metadata || {};

      // Brand
      document.getElementById('brandName').textContent = brand.name || 'Brand';
      document.getElementById('brandCategory').textContent = brand.category || 'Category';
      document.getElementById('brandSummary').textContent = brand.summary || '';

      // Meta
      document.getElementById('metaModel').textContent = meta.model_used || 'engine';
      document.getElementById('metaTime').textContent = `${meta.execution_time_seconds || 0}s`;
      document.getElementById('metaChars').textContent = meta.character_count_analyzed || 0;

      // Section 1: Competitors
      const compAnalysis = analysis.competitor_analysis || {};
      document.getElementById('brandOverview').textContent = compAnalysis.brand_overview || '';
      const tbody = document.getElementById('competitorsTableBody');
      tbody.innerHTML = '';
      (compAnalysis.competitors || []).forEach(c => {
        const row = document.createElement('tr');
        row.className = "hover:bg-slate-800/40";
        const compAdv = (c.comparison_with_brand && c.comparison_with_brand.your_brand_advantage) || 'High agility & cost-efficiency';
        const opp = (c.comparison_with_brand && c.comparison_with_brand.opportunity_to_improve) || 'Enhance market reach';
        row.innerHTML = `
          <td class="p-3 font-semibold text-white">${c.name}</td>
          <td class="p-3 text-slate-300">${c.main_service}</td>
          <td class="p-3 text-slate-400">${c.target_market}</td>
          <td class="p-3 text-slate-300 text-xs">${(c.strengths || []).join(', ')}</td>
          <td class="p-3 text-emerald-400 text-xs">${compAdv}</td>
          <td class="p-3 text-indigo-300 text-xs">${opp}</td>
        `;
        tbody.appendChild(row);
      });

      // Section 2: Queries
      const qList = document.getElementById('searchQueriesList');
      qList.innerHTML = '';
      (analysis.target_search_queries || []).forEach(q => {
        const div = document.createElement('div');
        div.className = "bg-slate-900/60 p-4 rounded-lg border border-slate-700/60 flex flex-col justify-between";
        div.innerHTML = `
          <div>
            <div class="flex items-center justify-between gap-2 mb-2">
              <span class="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded font-medium">${q.intent}</span>
              <div class="flex gap-1">
                ${(q.platforms || []).map(p => `<span class="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">${p}</span>`).join('')}
              </div>
            </div>
            <div class="text-sm font-semibold text-white mb-2">"${q.query}"</div>
            <p class="text-xs text-slate-400 mb-2">${q.business_relevance}</p>
          </div>
          <div class="text-[11px] text-slate-500 border-t border-slate-800 pt-2 mt-2">Target: ${q.target_audience}</div>
        `;
        qList.appendChild(div);
      });

      // Section 3: SEO
      const seo = analysis.seo_improvements || {};
      document.getElementById('seoTitle').textContent = seo.recommended_title || '';
      document.getElementById('seoTitleRationale').textContent = seo.title_improvement_rationale || '';
      document.getElementById('seoMetaDesc').textContent = seo.meta_description || '';
      document.getElementById('seoMetaSummary').textContent = seo.meta_description_summary || '';
      document.getElementById('seoPrimaryKw').textContent = seo.primary_keyword || '';
      document.getElementById('seoSecondaryKw').innerHTML = (seo.secondary_keywords || []).map(k => `<span class="inline-block bg-slate-800 text-slate-300 text-xs px-2 py-0.5 rounded mr-1">${k}</span>`).join('');
      document.getElementById('seoLongTailKw').innerHTML = (seo.long_tail_keywords || []).map(k => `<span class="inline-block bg-slate-800 text-slate-400 text-xs px-2 py-0.5 rounded mr-1 mb-1">${k}</span>`).join('');

      const supList = document.getElementById('supportingContentList');
      supList.innerHTML = '';
      (seo.supporting_content || []).forEach(sc => {
        const item = document.createElement('div');
        item.className = "bg-slate-800/50 p-3 rounded border border-slate-700/50 text-xs";
        item.innerHTML = `
          <div class="font-semibold text-indigo-300">${sc.content_type}: ${sc.topic}</div>
          <div class="text-slate-400 mt-1">${sc.purpose}</div>
        `;
        supList.appendChild(item);
      });

      // Section 4: Services
      const sList = document.getElementById('servicesList');
      sList.innerHTML = '';
      (analysis.top_services || []).forEach(s => {
        const sDiv = document.createElement('div');
        sDiv.className = "bg-slate-900/60 p-4 rounded-lg border border-slate-700/60 flex flex-col justify-between";
        const badge = s.is_inferred 
          ? `<span class="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">Inferred</span>`
          : `<span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">Extracted</span>`;
        sDiv.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-bold text-white">${s.service_name}</h4>
              ${badge}
            </div>
            <p class="text-xs text-slate-300 mb-3">${s.description}</p>
          </div>
          <div class="space-y-1 text-[11px] text-slate-400 border-t border-slate-800 pt-2">
            <div><strong class="text-slate-300">Benefit:</strong> ${s.main_benefit}</div>
            <div><strong class="text-slate-300">Customer:</strong> ${s.target_customer}</div>
          </div>
        `;
        sList.appendChild(sDiv);
      });

      // Section 5: Target Audience
      const aud = analysis.target_audience || {};
      const segList = document.getElementById('audienceSegmentsList');
      segList.innerHTML = '';
      (aud.recommended_segments || []).forEach(seg => {
        const box = document.createElement('div');
        box.className = "bg-slate-900/80 p-3 rounded-lg border border-slate-700/60 text-xs";
        box.innerHTML = `
          <div class="font-bold text-indigo-300 mb-1">${seg.audience}</div>
          <div class="text-slate-200 font-medium mb-1">${seg.business_type}</div>
          <div class="text-slate-400 text-[11px]">${seg.requirement}</div>
        `;
        segList.appendChild(box);
      });

      const personas = document.getElementById('personasContainer');
      personas.innerHTML = '';
      (aud.customer_profiles || []).forEach(p => {
        const pBox = document.createElement('div');
        pBox.className = "text-xs space-y-1 border-b border-slate-800 pb-2 last:border-b-0";
        pBox.innerHTML = `
          <div class="font-semibold text-white">${p.role_or_persona}</div>
          <div class="text-slate-400"><strong class="text-rose-400">Pains:</strong> ${(p.pain_points || []).join(', ')}</div>
          <div class="text-slate-400"><strong class="text-emerald-400">Goals:</strong> ${(p.goals || []).join(', ')}</div>
        `;
        personas.appendChild(pBox);
      });

      const needs = document.getElementById('customerNeedsList');
      needs.innerHTML = '';
      (aud.customer_needs || []).forEach(n => {
        const li = document.createElement('li');
        li.textContent = n;
        needs.appendChild(li);
      });

      // Raw JSON
      document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);

      resultsContainer.classList.remove('hidden');
    }
  </script>
</body>
</html>
"""
