#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-job-skill-trends}"

echo "Scaffolding into: $PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT"

dirs=(
  "config"
  "data/raw" "data/interim" "data/processed" "data/notebooks_data"
  "notebooks"
  "scripts"
  "backend"
  "backend/db"
  "backend/scraping"
  "backend/etl"
  "backend/nlp"
  "backend/modeling"
  "backend/api" "backend/api/routers"
  "backend/monitoring"
  "backend/utils"
  "frontend"
  "frontend/src"
  "frontend/src/api"
  "frontend/src/components" "frontend/src/components/Layout" "frontend/src/components/Charts" "frontend/src/components/Filters"
  "frontend/src/pages"
  "frontend/src/styles"
  "frontend/public"
)

for d in "${dirs[@]}"; do mkdir -p "$PROJECT_ROOT/$d"; done

files=(
  "README.md"
  "LICENSE"
  ".gitignore"
  "requirements.txt"
  "docker-compose.yml"
  ".env.example"

  "config/settings_example.yaml"
  "config/skill_taxonomy.yaml"

  "data/.gitkeep" "data/raw/.gitkeep" "data/interim/.gitkeep" "data/processed/.gitkeep" "data/notebooks_data/.gitkeep"

  "notebooks/01_eda_jobs.ipynb"
  "notebooks/02_skill_trends.ipynb"
  "notebooks/03_forecasting_playground.ipynb"

  "scripts/run_full_pipeline.py"
  "scripts/run_scrapers_once.py"
  "scripts/rebuild_analytics.py"
  "scripts/retrain_forecasts.py"

  "backend/__init__.py"
  "backend/db/__init__.py" "backend/db/models.py" "backend/db/schema.sql" "backend/db/session.py"
  "backend/scraping/__init__.py" "backend/scraping/base_scraper.py" "backend/scraping/indeed_scraper.py" "backend/scraping/remoteok_scraper.py" "backend/scraping/wellfound_scraper.py" "backend/scraping/weworkremotely_scraper.py"
  "backend/etl/__init__.py" "backend/etl/clean_jobs.py" "backend/etl/enrich_jobs.py" "backend/etl/loaders.py"
  "backend/nlp/__init__.py" "backend/nlp/skill_taxonomy.py" "backend/nlp/rule_based_extractor.py" "backend/nlp/llm_extractor.py" "backend/nlp/skill_pipeline.py"
  "backend/modeling/__init__.py" "backend/modeling/embeddings.py" "backend/modeling/clustering.py" "backend/modeling/trends_aggregation.py" "backend/modeling/forecasting.py" "backend/modeling/evaluation.py"
  "backend/api/__init__.py" "backend/api/main.py" "backend/api/routers/__init__.py" "backend/api/routers/skills.py" "backend/api/routers/clusters.py" "backend/api/routers/meta.py" "backend/api/schemas.py"
  "backend/monitoring/__init__.py" "backend/monitoring/logging_config.py" "backend/monitoring/scrape_health_checks.py" "backend/monitoring/drift_checks.py"
  "backend/utils/__init__.py" "backend/utils/config_loader.py" "backend/utils/time_utils.py" "backend/utils/text_utils.py"

  "frontend/README.md"
  "frontend/package.json"
  "frontend/vite.config.mts"
  "frontend/tsconfig.json"
  "frontend/src/main.tsx" "frontend/src/App.tsx" "frontend/src/api/client.ts"
  "frontend/src/pages/OverviewPage.tsx" "frontend/src/pages/SkillTrendsPage.tsx" "frontend/src/pages/RisingSkillsPage.tsx" "frontend/src/pages/RoleClustersPage.tsx"
  "frontend/src/styles/global.css"
  "frontend/public/index.html"
)

for f in "${files[@]}"; do
  touch "$PROJECT_ROOT/$f"
done

cat > "$PROJECT_ROOT/.gitignore" <<'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
.venv/
venv/
.ipynb_checkpoints/

# Data
data/raw/
data/interim/
data/processed/
data/notebooks_data/

# Node
node_modules/
dist/
build/

# OS/editor
.DS_Store
.vscode/

# Logs
logs/
*.log
EOF

cat > "$PROJECT_ROOT/.env.example" <<'EOF'
# Copy to .env and fill values
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/job_skill_trends
OPENAI_API_KEY=
EMBEDDINGS_PROVIDER=openai
ENV=dev
EOF

cat > "$PROJECT_ROOT/config/settings_example.yaml" <<'EOF'
app:
  env: dev
  log_level: INFO
database:
  url: ${DATABASE_URL}
scraping:
  providers: [indeed, remoteok, wellfound, weworkremotely]
  request_delay_seconds: 1.0
nlp:
  use_llm: false
  embeddings_provider: ${EMBEDDINGS_PROVIDER}
forecasting:
  horizon_weeks: 12
EOF

cat > "$PROJECT_ROOT/config/skill_taxonomy.yaml" <<'EOF'
families:
  languages: [python, javascript, typescript, java, go, rust, c++, sql]
  frameworks: [react, node.js, django, flask, spring, fastapi, next.js]
  data: [pandas, numpy, pyspark, airflow, kafka, snowflake, bigquery, dbt]
  cloud: [aws, gcp, azure, docker, kubernetes, terraform]
EOF

cat > "$PROJECT_ROOT/README.md" <<'EOF'
Real-Time Tech Job Skill Trend Intelligence
Scaffolded structure. Next: add minimal runnable stubs.
EOF

cat > "$PROJECT_ROOT/frontend/README.md" <<'EOF'
Frontend scaffold (Vite + React planned). To be initialized next.
EOF

echo "Scaffold complete."