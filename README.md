# Real-Time Tech Job Skill Trend Intelligence

This project surfaces real-time trends in tech job skills by scraping postings, extracting and normalizing skills, aggregating trends over time, and forecasting future demand. It provides a small API and an interactive dashboard to answer practical questions for seekers and hiring teams.

## Part 1 — Project Scoping and Business Understanding

### Goal
Turn the idea into a clear specification with concrete questions, metrics, and success criteria that guide technical and product tradeoffs.

### Core Personas
- **Tech job seeker**
  - Needs to know which skills to learn or emphasize to improve job prospects and salary.
- **Career coach / university advisor**
  - Guides learners on curriculum and career paths based on current and emerging market demand.
- **Hiring manager / recruiter**
  - Benchmarks market demand and compensation, aligns JDs with realistic skills, and anticipates emerging needs.

### Key Questions the System Should Answer
- **Which skills are growing fastest** in data engineering roles in the last 12 months?
- **Which locations are paying above average** for ML engineer roles?
- **Which frameworks are emerging** in backend roles (e.g., FastAPI vs Django)?
- How does demand for a given skill (e.g., Kubernetes) **vary by role seniority** and **employment type** (remote, hybrid, onsite)?
- What are the **top co-occurring skills** with a target skill (e.g., dbt) in the last quarter?
- **Forecast**: where will demand for selected skills be in the **next 8–12 weeks**?

### Initial Scope (v0)
- **Time window**: Last 12 months of postings; retain historical accumulation going forward.
- **Geography**: US + Remote roles (global remote included); expand later.
- **Role categories**: Software Engineer (frontend, backend), Data Engineer, ML Engineer, MLOps.
- **Sources**: Indeed, RemoteOK, Wellfound, WeWorkRemotely (weekly to daily cadence, respectful rate limits).
- **Outputs**: Skill frequency trends weekly; cluster labels for role profiles; simple forecasts per skill.

### Success Metrics
- **Data coverage**
  - ≥ 10,000 unique postings collected within first 6–8 weeks.
  - De-duplication rate tracked; < 10% duplicates after cleaning.
- **Skill extraction quality**
  - ≥ 150 distinct normalized skills in taxonomy; precision (manual spot-check) ≥ 85% on sampled postings.
- **Usability**
  - A user can answer at least **5 real questions** in the dashboard without manual SQL.
  - p50 API latency < 300 ms for common queries (skills trend, top-N).
- **Reliability (ops)**
  - Scrape health check: weekly new postings count does not drop >40% without alert.
  - Forecast refresh completes on schedule (weekly) with success rate ≥ 95%.

### Assumptions
- Public job boards allow respectful scraping within ToS and robots guidance; dynamic pages may require Playwright.
- Skill taxonomy starts rule-based and is refined with LLM-assisted extraction over time.
- Postgres is sufficient initially; can evolve to managed Postgres + object storage for raw HTML snapshots.

### Deliverable of Part 1
This short design spec (above) acts as the reference for scope, product decisions, and success criteria. Subsequent parts (scraping, ETL, NLP, aggregation, forecasting, API, and dashboard) will align to these goals.

## Part 2 — Data Source Analysis and Legal‑Ethical Review

### Goal
Make a concrete, safe plan for where and how we will scrape.

### Selected Initial Sources (pilot)
- **RemoteOK**
  - Entry URLs: remote developer/data/ML categories (e.g., https://remoteok.com/remote-dev-jobs). Confirm exact role-specific paths via site navigation.
  - Pagination: next-page links at the bottom; confirm presence of page query params if any.
  - Detail links: job cards link to detail pages; extract hrefs from listing cards.
- **We Work Remotely (WWR)**
  - Entry URLs: category pages (e.g., https://weworkremotely.com/categories/remote-programming-jobs, data, devops).
  - Pagination: “Older Posts” links; confirm query pattern.
  - Detail links: each listing anchors to a detail page; extract hrefs.
- **Wellfound (AngelList)**
  - Entry URLs: remote-friendly role searches (confirm current paths, e.g., jobs with filters for remote and role).
  - Note: site structure can change; selectors must be verified in browser dev tools.

Indeed is large and frequently changes anti-scraping measures; consider as a separate, optional track after confirming ToS and feasibility.

### Robots/ToS Review Process
- Check robots.txt and terms for each domain before scraping:
  - RemoteOK: https://remoteok.com/robots.txt
  - WeWorkRemotely: https://weworkremotely.com/robots.txt
  - Wellfound: https://wellfound.com/robots.txt
- Proceed only for paths not disallowed by robots.txt and permitted by ToS. If disallowed or unclear, do not scrape; prefer official APIs or alternative public sources.

### What We Will Extract (public listing content only)
- Required fields: title, company, location (or remote), posting URL, posted date, tags/skills, description snippet, salary if publicly shown.
- No collection of personal data. No emails/usernames unless part of the public job description text (and even then, do not persist as separate PII fields).

### Selectors (to be validated per site in DevTools)
- Listing pages: CSS selectors for job cards (e.g., container classes), anchors for detail links, pagination link/button.
- Detail pages: title, company, location, description container, tags/skills, salary block, posted date.
- Note: selectors may change; keep rules in `backend/scraping/*_scraper.py` and unit-test against saved HTML snapshots in `data/raw/`.

### Respectful Scraping Policy
- Rate limiting: max ~1 request/second per domain, concurrency=1.
- Jitter: random sleep 200–800ms added to base delay to avoid burst patterns.
- Retries: exponential backoff for transient 5xx/429 (e.g., 0.5s, 1s, 2s, cap at 3 attempts), respect Retry-After headers.
- Backoff/stop: on repeated 403/anti-bot signals or captcha, stop scraping that domain and alert.
- Headers: set a descriptive User-Agent (project name + contact). Avoid pretending to be a browser beyond basic headers.
- Caching: snapshot listing HTML as NDJSON or HTML in `data/raw/{domain}/YYYYMMDD/` to limit repeated fetches.

### Pagination Strategies (confirm per site)
- Follow explicit “Next”/“Older” links on category pages.
- If numeric pages are supported (e.g., `?page=N`), cap initial crawl depth (e.g., first 5 pages) to limit load while we validate quality.

### What We Will Not Do
- No scraping behind logins or paywalls.
- No bypassing technical measures (no captcha solving, no headless browser stealth techniques).
- No collection or storage of PII beyond company and job posting details.
- Immediate removal on request; respect site takedowns and changes to robots/ToS.

### Output of Part 2
- A concrete per-site plan (entry URLs, pagination approach, fields/selectors, rate limits) as above.
- Implementation next steps: encode per-site settings in `config/settings_example.yaml` and implement scrapers in `backend/scraping/` using a shared base with rate limiting and retries.

## Part 3 — Scraper Design and Implementation

### Goal
Build robust, reusable scrapers that collect job postings and store them in a validated raw form.

### Architecture
- **Location**: `backend/scraping/`
  - **`base_scraper.py`**: shared HTTP client, rate limiting (≈1 req/s), retries/backoff, HTML snapshotting, helpers.
  - **Site scrapers**: `remoteok_scraper.py`, `weworkremotely_scraper.py`, `wellfound_scraper.py`.
  - **CLI**: `scripts/run_scrapers_once.py` to run selected scrapers and print/store results.
- **Schema (Pydantic) — raw record**
  - Validated at scrape-time to ensure consistent downstream processing.
  - Fields:
    - `job_id: str`
    - `source: str`
    - `title: str | None`
    - `company: str | None`
    - `location_raw: str | None`
    - `posted_raw: str | None` (e.g., "3 days ago", ISO date string if available)
    - `description_raw: str | None`
    - `salary_raw: str | None`
    - `job_type: str | None` (e.g., Full-time, Contract)
    - `url: str`
    - `scraped_at: datetime`

### Core Behaviors
- **HTTP client**: `httpx` with timeouts and a descriptive `User-Agent`.
- **Rate limiting + jitter**: 1 req/s/domain target with 200–800ms jitter.
- **Retries/backoff**: exponential for 429/5xx; stop on repeated 403/captcha.
- **HTML snapshots**: store a few listing and job pages under `data/raw/{source}/YYYYMMDD/` for debugging.
- **Logging**: per-site counts of fetched, parsed, stored, and failed; errors include URL context.

### Per-site scraping plan (selectors to be validated in DevTools)
- **RemoteOK**
  - Listing URLs: role/category pages.
  - Find job anchors to detail pages; follow to detail.
  - Extract: title, company, location, description container, salary (if visible), tags/job type, posted text.
- **We Work Remotely (WWR)**
  - Listing URLs: category pages (programming, data, devops).
  - Extract anchors to detail; parse title, company, location, description, salary, type, posted.
- **Wellfound (AngelList)**
  - Listing/search pages filtered for remote/role; confirm stable selectors.
  - Extract detail similarly; some content may be dynamic — consider Playwright only if robots/ToS and need justify.

### ID and de-duplication
- **`job_id`**: derive from stable slug/ID in URL or page data attributes. If none, hash of `source+url`.
- Maintain a simple seen-URL set per run; DB-level de-dupe will occur in ETL.

### Storage format (pilot)
- **Option A (files)**: write NDJSON to `data/processed/raw_jobs_{source}_{YYYYMMDD}.ndjson`.
- **Option B (DB)**: insert into `jobs_raw` table via loader (added in Part 4). For Part 3, file output is sufficient.

### CLI usage (planned)
- Example runs (to be implemented in `scripts/run_scrapers_once.py`):
  - `python scripts/run_scrapers_once.py --source remoteok --max-jobs 50` (prints to stdout and writes NDJSON)
  - `python scripts/run_scrapers_once.py --all --max-per-source 50`

### Quality and safety checks
- Random sample snapshot review each run (5–10 jobs) to spot selector drift.
- Respect robots/ToS; no logins/paywalls; no PII beyond company and job details.

---

## Repository Layout (high level)
See the scaffolded directories for backend, data, scripts, notebooks, and frontend. Proceed to implement Parts 2–10 using this spec as guidance.
