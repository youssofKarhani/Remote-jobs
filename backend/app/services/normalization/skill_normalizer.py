"""Deterministic Technical Skill Normalizer.

Normalizes raw skill strings extracted from CVs into canonical taxonomy terms
while strictly preserving the raw text claim (Rule 3 & 4: Raw vs Normalized Separation).
Example: raw_value="MangoDB" -> normalized_value="MongoDB", category="database".
"""

from difflib import SequenceMatcher
import re
from typing import Dict, List, Optional, Tuple

from app.schemas.semantic_cv import SemanticSkill

# Canonical Taxonomy mapping:
# canonical_id -> (Canonical Display Name, Category, [Aliases / Common Misspellings / Variants])
SKILL_TAXONOMY: Dict[str, Tuple[str, str, List[str]]] = {
    # Backend & Languages
    "python": ("Python", "backend", ["python", "python3", "python 3", "python2", "py3", "py"]),
    "fastapi": ("FastAPI", "backend", ["fastapi", "fast api", "fast-api"]),
    "django": ("Django", "backend", ["django", "django rest framework", "drf"]),
    "flask": ("Flask", "backend", ["flask"]),
    "node": ("Node.js", "backend", ["node", "nodejs", "node.js", "node js"]),
    "golang": ("Go", "backend", ["go", "golang", "go lang"]),
    "java": ("Java", "backend", ["java", "core java", "java 8", "java 11", "java 17", "java 21"]),
    "csharp": ("C#", "backend", ["c#", "csharp", "c-sharp", ".net", "dotnet", ".net core"]),
    "cpp": ("C++", "backend", ["c++", "cpp"]),
    "rust": ("Rust", "backend", ["rust", "rustlang"]),
    "graphql": ("GraphQL", "backend", ["graphql", "graph ql"]),
    "rest_api": ("RESTful APIs", "backend", ["rest", "rest api", "rest apis", "restful", "restful api", "restful apis", "web apis"]),
    "pydantic": ("Pydantic", "backend", ["pydantic", "pydantic v2"]),
    "celery": ("Celery", "backend", ["celery", "celery worker"]),

    # Databases & Storage
    "postgresql": ("PostgreSQL", "database", ["postgresql", "postgres", "psql", "postgre sql", "postgreesql"]),
    "mongodb": ("MongoDB", "database", ["mongodb", "mongo db", "mangodb", "mongo"]),
    "mysql": ("MySQL", "database", ["mysql", "my sql"]),
    "redis": ("Redis", "database", ["redis", "redis cache"]),
    "elasticsearch": ("Elasticsearch", "database", ["elasticsearch", "elastic search", "opensearch"]),
    "sqlite": ("SQLite", "database", ["sqlite", "sqlite3"]),
    "sql": ("SQL", "database", ["sql", "structured query language", "ansi sql", "relational databases"]),

    # Frontend
    "react": ("React", "frontend", ["react", "reactjs", "react.js", "react js"]),
    "nextjs": ("Next.js", "frontend", ["nextjs", "next.js", "next js", "next 14", "next 15"]),
    "typescript": ("TypeScript", "frontend", ["typescript", "ts"]),
    "javascript": ("JavaScript", "frontend", ["javascript", "js", "ecmascript", "es6"]),
    "vue": ("Vue.js", "frontend", ["vue", "vuejs", "vue.js", "vue 3"]),
    "angular": ("Angular", "frontend", ["angular", "angularjs", "angular 2+"]),
    "html_css": ("HTML/CSS", "frontend", ["html", "html5", "css", "css3", "html/css", "html5/css3"]),
    "tailwind": ("Tailwind CSS", "frontend", ["tailwind", "tailwindcss", "tailwind css"]),

    # Cloud & DevOps
    "aws": ("Amazon Web Services", "cloud", ["aws", "amazon web services", "aws cloud", "amazon aws"]),
    "gcp": ("Google Cloud Platform", "cloud", ["gcp", "google cloud", "google cloud platform"]),
    "azure": ("Microsoft Azure", "cloud", ["azure", "microsoft azure", "ms azure"]),
    "docker": ("Docker", "devops", ["docker", "docker container", "docker containers", "docker compose"]),
    "kubernetes": ("Kubernetes", "devops", ["kubernetes", "k8s", "k8"]),
    "git": ("Git", "devops", ["git", "github", "gitlab", "bitbucket", "version control"]),
    "linux": ("Linux", "devops", ["linux", "ubuntu", "debian", "redhat", "centos", "unix"]),
    "ci_cd": ("CI/CD", "devops", ["ci/cd", "ci cd", "github actions", "gitlab ci", "jenkins"]),
    "terraform": ("Terraform", "devops", ["terraform", "tf (infra)"]),

    # AI, Machine Learning & Data
    "pytorch": ("PyTorch", "ai_ml", ["pytorch", "torch", "py torch"]),
    "tensorflow": ("TensorFlow", "ai_ml", ["tensorflow", "tf", "tensor flow"]),
    "scikit_learn": ("scikit-learn", "ai_ml", ["scikit-learn", "sklearn", "scikit learn"]),
    "pandas": ("Pandas", "data", ["pandas", "pd"]),
    "numpy": ("NumPy", "data", ["numpy", "np"]),
    "ollama": ("Ollama", "ai_ml", ["ollama"]),
    "langchain": ("LangChain", "ai_ml", ["langchain", "lang chain"]),
    "llamaindex": ("LlamaIndex", "ai_ml", ["llamaindex", "llama-index", "llama index"]),
    "airflow": ("Apache Airflow", "data", ["airflow", "apache airflow"]),
    "kafka": ("Apache Kafka", "data", ["kafka", "apache kafka"]),
    "spark": ("Apache Spark", "data", ["spark", "apache spark", "pyspark"]),
}

# Inverted index for O(1) alias lookups: cleaned_alias -> (canonical_name, category)
_ALIAS_LOOKUP: Dict[str, Tuple[str, str]] = {}
for canonical_id, (display_name, category, aliases) in SKILL_TAXONOMY.items():
    _ALIAS_LOOKUP[canonical_id] = (display_name, category)
    _ALIAS_LOOKUP[display_name.lower()] = (display_name, category)
    for alias in aliases:
        _ALIAS_LOOKUP[alias.lower().strip()] = (display_name, category)


def _clean_skill_token(token: str) -> str:
    """Clean and normalize a skill string for lookup."""
    t = token.lower().strip()
    t = re.sub(r"[\(\)\[\]\{\}]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def normalize_skill_name(raw_text: str) -> Tuple[Optional[str], Optional[str], float]:
    """Normalize a raw skill string.
    
    Returns:
        (canonical_name, category, confidence)
    """
    if not raw_text or not raw_text.strip():
        return None, None, 0.0

    cleaned = _clean_skill_token(raw_text)

    # 1. Exact match in alias lookup
    if cleaned in _ALIAS_LOOKUP:
        canonical_name, category = _ALIAS_LOOKUP[cleaned]
        return canonical_name, category, 1.0

    # 2. Substring or prefix match
    for alias, (canonical_name, category) in _ALIAS_LOOKUP.items():
        if len(alias) >= 4 and (cleaned == alias or cleaned.startswith(f"{alias} ") or cleaned.endswith(f" {alias}")):
            return canonical_name, category, 0.95

    # 3. Fuzzy match for typo tolerance (e.g. "MangoDB" -> "MongoDB", edit similarity >= 0.85)
    best_match: Optional[str] = None
    best_category: Optional[str] = None
    best_ratio = 0.0

    for alias, (canonical_name, category) in _ALIAS_LOOKUP.items():
        if len(alias) < 3 or len(cleaned) < 3:
            continue
        ratio = SequenceMatcher(None, cleaned, alias).ratio()
        if ratio > best_ratio and ratio >= 0.85:
            best_ratio = ratio
            best_match = canonical_name
            best_category = category

    if best_match:
        return best_match, best_category, round(best_ratio, 2)

    # Unknown / Unnormalized skill
    return None, None, 0.5


def normalize_skill_entity(skill: SemanticSkill) -> SemanticSkill:
    """Normalize a SemanticSkill in-place without altering its raw_value (Rule 3 & 4)."""
    canonical_name, category, confidence = normalize_skill_name(skill.raw_value)
    
    # Strictly preserve raw_value
    skill.normalized_value = canonical_name
    if category and not skill.category:
        skill.category = category
    
    # Store normalization confidence in provenance or metadata
    if hasattr(skill.provenance, "extraction_confidence"):
        # Combine extraction confidence with normalization confidence
        skill.provenance.extraction_confidence = round(
            min(skill.provenance.extraction_confidence, confidence), 2
        )
    return skill
