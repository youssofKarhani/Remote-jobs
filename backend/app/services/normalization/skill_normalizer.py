"""Deterministic Technical Skill and Technology Normalizer.

Normalizes raw skill strings extracted from CVs into canonical taxonomy terms
while strictly preserving the verbatim text claim in raw_value (Rule 3 & 4).
Example: raw_value="MangoDB" -> normalized_value="MongoDB", category="database",
normalization_method="known_technology_alias_or_typo", normalization_confidence=0.96.

ARCHITECTURAL INVARIANT:
"FastAPI must NOT automatically create Python as an additional candidate claim.
Relationships between technologies may exist as metadata, but must not become
candidate evidence unless supported by source evidence."
"""

from difflib import SequenceMatcher
import re
from typing import Dict, List, Optional, Tuple

from app.schemas.semantic_cv import SemanticSkill

# Canonical Taxonomy mapping:
# canonical_id -> (Canonical Display Name, Category, [Aliases / Common Misspellings / Variants], [Related Technologies - METADATA ONLY])
SKILL_TAXONOMY: Dict[str, Tuple[str, str, List[str], List[str]]] = {
    # Backend & Languages
    "python": ("Python", "backend", ["python", "python3", "python 3", "python2", "py3", "py"], []),
    "fastapi": ("FastAPI", "backend", ["fastapi", "fast api", "fast-api"], ["Python"]),
    "django": ("Django", "backend", ["django", "django rest framework", "drf"], ["Python"]),
    "flask": ("Flask", "backend", ["flask"], ["Python"]),
    "node": ("Node.js", "backend", ["node", "nodejs", "node.js", "node js"], ["JavaScript"]),
    "golang": ("Go", "backend", ["go", "golang", "go lang"], []),
    "java": ("Java", "backend", ["java", "core java", "java 8", "java 11", "java 17", "java 21"], []),
    "csharp": ("C#", "backend", ["c#", "csharp", "c-sharp", ".net", "dotnet", ".net core"], []),
    "cpp": ("C++", "backend", ["c++", "cpp"], []),
    "rust": ("Rust", "backend", ["rust", "rustlang"], []),
    "graphql": ("GraphQL", "backend", ["graphql", "graph ql"], []),
    "rest_api": ("RESTful APIs", "backend", ["rest", "rest api", "rest apis", "restful", "restful api", "restful apis", "web apis"], []),
    "pydantic": ("Pydantic", "backend", ["pydantic", "pydantic v2"], ["Python"]),
    "celery": ("Celery", "backend", ["celery", "celery worker"], ["Python"]),

    # Databases & Storage
    "postgresql": ("PostgreSQL", "database", ["postgresql", "postgres", "psql", "postgre sql", "postgreesql"], ["SQL"]),
    "mongodb": ("MongoDB", "database", ["mongodb", "mongo db", "mangodb", "mongo"], []),
    "mysql": ("MySQL", "database", ["mysql", "my sql"], ["SQL"]),
    "redis": ("Redis", "database", ["redis", "redis cache"], []),
    "elasticsearch": ("Elasticsearch", "database", ["elasticsearch", "elastic search", "opensearch"], []),
    "sqlite": ("SQLite", "database", ["sqlite", "sqlite3"], ["SQL"]),
    "sql": ("SQL", "database", ["sql", "structured query language", "ansi sql", "relational databases"], []),

    # Frontend
    "react": ("React", "frontend", ["react", "reactjs", "react.js", "react js"], ["JavaScript"]),
    "nextjs": ("Next.js", "frontend", ["nextjs", "next.js", "next js", "next 14", "next 15"], ["React", "TypeScript"]),
    "typescript": ("TypeScript", "frontend", ["typescript", "ts"], ["JavaScript"]),
    "javascript": ("JavaScript", "frontend", ["javascript", "js", "ecmascript", "es6"], []),
    "vue": ("Vue.js", "frontend", ["vue", "vuejs", "vue.js", "vue 3"], ["JavaScript"]),
    "angular": ("Angular", "frontend", ["angular", "angularjs", "angular 2+"], ["TypeScript"]),
    "html_css": ("HTML/CSS", "frontend", ["html", "html5", "css", "css3", "html/css", "html5/css3"], []),
    "tailwind": ("Tailwind CSS", "frontend", ["tailwind", "tailwindcss", "tailwind css"], ["CSS"]),

    # Cloud & DevOps
    "aws": ("Amazon Web Services", "cloud", ["aws", "amazon web services", "aws cloud", "amazon aws"], []),
    "gcp": ("Google Cloud Platform", "cloud", ["gcp", "google cloud", "google cloud platform"], []),
    "azure": ("Microsoft Azure", "cloud", ["azure", "microsoft azure", "ms azure"], []),
    "docker": ("Docker", "devops", ["docker", "docker container", "docker containers", "docker compose"], []),
    "kubernetes": ("Kubernetes", "devops", ["kubernetes", "k8s", "k8"], []),
    "git": ("Git", "devops", ["git", "github", "gitlab", "bitbucket", "version control"], []),
    "linux": ("Linux", "devops", ["linux", "ubuntu", "debian", "redhat", "centos", "unix"], []),
    "ci_cd": ("CI/CD", "devops", ["ci/cd", "ci cd", "github actions", "gitlab ci", "jenkins"], []),
    "terraform": ("Terraform", "devops", ["terraform", "tf (infra)"], []),

    # AI, Machine Learning & Data
    "pytorch": ("PyTorch", "ai_ml", ["pytorch", "torch", "py torch"], ["Python"]),
    "tensorflow": ("TensorFlow", "ai_ml", ["tensorflow", "tf", "tensor flow"], ["Python"]),
    "scikit_learn": ("scikit-learn", "ai_ml", ["scikit-learn", "sklearn", "scikit learn"], ["Python"]),
    "pandas": ("Pandas", "data", ["pandas", "pd"], ["Python"]),
    "numpy": ("NumPy", "data", ["numpy", "np"], ["Python"]),
    "ollama": ("Ollama", "ai_ml", ["ollama"], []),
    "langchain": ("LangChain", "ai_ml", ["langchain", "lang chain"], ["Python"]),
    "llamaindex": ("LlamaIndex", "ai_ml", ["llamaindex", "llama-index", "llama index"], ["Python"]),
    "airflow": ("Apache Airflow", "data", ["airflow", "apache airflow"], ["Python"]),
    "kafka": ("Apache Kafka", "data", ["kafka", "apache kafka"], []),
    "spark": ("Apache Spark", "data", ["spark", "apache spark", "pyspark"], []),
}

# Inverted index for O(1) alias lookups: cleaned_alias -> (canonical_name, category, related_techs)
_ALIAS_LOOKUP: Dict[str, Tuple[str, str, List[str]]] = {}
for canonical_id, (display_name, category, aliases, related) in SKILL_TAXONOMY.items():
    _ALIAS_LOOKUP[canonical_id] = (display_name, category, related)
    _ALIAS_LOOKUP[display_name.lower()] = (display_name, category, related)
    for alias in aliases:
        _ALIAS_LOOKUP[alias.lower().strip()] = (display_name, category, related)


def _clean_skill_token(token: str) -> str:
    """Clean and normalize a skill string for lookup."""
    t = token.lower().strip()
    t = re.sub(r"[\(\)\[\]\{\}]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def normalize_skill_name(raw_text: str) -> Tuple[Optional[str], Optional[str], float, str, List[str]]:
    """Normalize a raw skill string.

    Returns:
        (canonical_name, category, confidence, normalization_method, related_technologies)
    """
    if not raw_text or not raw_text.strip():
        return None, None, 0.0, "none", []

    cleaned = _clean_skill_token(raw_text)

    # 1. Exact match in alias lookup
    if cleaned in _ALIAS_LOOKUP:
        canonical_name, category, related = _ALIAS_LOOKUP[cleaned]
        method = "exact_taxonomy_match" if cleaned == canonical_name.lower() else "known_technology_alias_or_typo"
        return canonical_name, category, 1.0, method, related

    # 2. Substring or prefix match
    for alias, (canonical_name, category, related) in _ALIAS_LOOKUP.items():
        if len(alias) >= 4 and (cleaned == alias or cleaned.startswith(f"{alias} ") or cleaned.endswith(f" {alias}")):
            return canonical_name, category, 0.95, "known_technology_alias_or_typo", related

    # 3. Fuzzy match for typo tolerance (e.g. "MangoDB" -> "MongoDB", edit similarity >= 0.85)
    best_match: Optional[str] = None
    best_category: Optional[str] = None
    best_related: List[str] = []
    best_ratio = 0.0

    for alias, (canonical_name, category, related) in _ALIAS_LOOKUP.items():
        if len(alias) < 3 or len(cleaned) < 3:
            continue
        ratio = SequenceMatcher(None, cleaned, alias).ratio()
        if ratio > best_ratio and ratio >= 0.85:
            best_ratio = ratio
            best_match = canonical_name
            best_category = category
            best_related = related

    if best_match:
        return best_match, best_category, round(best_ratio, 2), "known_technology_alias_or_typo", best_related

    # Unknown / Unnormalized skill: preserve raw without hallucinating a normalization
    return None, None, 0.5, "unrecognized_raw_preserved", []


def normalize_skill_entity(skill: SemanticSkill) -> SemanticSkill:
    """Normalize a SemanticSkill in-place without altering its verbatim raw_value (Rule 3 & 4).

    Guarantees that relationships to other technologies (e.g. FastAPI -> Python)
    are strictly stored in metadata and NEVER synthesize new candidate skill claims.
    """
    canonical_name, category, confidence, method, related = normalize_skill_name(skill.raw_value)

    # Strictly preserve raw_value; populate normalized_value
    skill.normalized_value = canonical_name
    if category and not skill.category:
        skill.category = category

    if not skill.metadata:
        skill.metadata = {}
    skill.metadata["normalization_method"] = method
    skill.metadata["normalization_confidence"] = confidence
    if related:
        # Informational metadata ONLY — never become candidate claims
        skill.metadata["related_technologies"] = related

    # Store normalization confidence in provenance
    if hasattr(skill.provenance, "extraction_confidence"):
        skill.provenance.extraction_confidence = round(
            min(skill.provenance.extraction_confidence, confidence), 2
        )
    return skill
