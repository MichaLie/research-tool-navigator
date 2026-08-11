#!/usr/bin/env python3
"""Transparent read-only retrieval across the three research-tool catalogues.

The search score orders catalogue retrieval only. It is intentionally not a
suitability score, scientific assessment, or recommendation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


VERSION = "0.1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent

INDEXES = ("foundation_models", "autonomous_agents", "coding_agents")
DEFAULT_CATALOGUES = {
    "foundation_models": WORKSPACE_ROOT / "Foundation_models" / "models_final.json",
    "autonomous_agents": WORKSPACE_ROOT / "Autonomous_Agents" / "agents_final.json",
    "coding_agents": WORKSPACE_ROOT / "Coding_Agents" / "tools.json",
}
ID_PREFIX = {
    "foundation_models": "bfm-",
    "autonomous_agents": "asa-",
    "coding_agents": "rca-",
}
ROLE_LABEL = {
    "foundation_models": "foundation model",
    "autonomous_agents": "autonomous scientific agent",
    "coding_agents": "coding or data agent",
}

FIELD_WEIGHTS = {
    "foundation_models": {
        "id": 10.0,
        "name": 9.0,
        "aliases": 8.0,
        "modality": 7.0,
        "use_cases": 7.0,
        "io": 6.0,
        "description": 4.0,
        "status": 1.5,
    },
    "autonomous_agents": {
        "id": 10.0,
        "name": 9.0,
        "domain": 7.0,
        "category": 6.0,
        "outputs": 7.0,
        "inputs": 5.0,
        "notes": 4.0,
        "access": 1.5,
        "autonomy": 1.0,
    },
    "coding_agents": {
        "id": 10.0,
        "name": 9.0,
        "current_name": 9.0,
        "use_cases": 7.0,
        "type": 5.0,
        "capability": 4.0,
        "notes": 3.0,
        "suitability_notes": 3.0,
        "deployment": 2.0,
        "model_backend": 2.0,
        "data_handling_note": 1.5,
        "openness": 1.5,
        "runs_locally": 1.0,
    },
}

DISPLAY_FIELDS = {
    "foundation_models": ("modality", "description", "io", "use_cases", "status", "year", "verified"),
    "autonomous_agents": ("category", "domain", "inputs", "outputs", "access", "autonomy", "notes", "verified"),
    "coding_agents": (
        "vendor",
        "type",
        "deployment",
        "openness",
        "runs_locally",
        "use_cases",
        "data_handling",
        "pricing",
        "verified",
    ),
}

QUERY_WEIGHTS = {
    "required": 8.0,
    "outcome": 6.0,
    "domain": 5.0,
    "synonym": 2.5,
    "research_need": 0.5,
}

STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "can",
    "could",
    "for",
    "from",
    "have",
    "into",
    "need",
    "research",
    "researcher",
    "should",
    "that",
    "the",
    "their",
    "this",
    "tool",
    "tools",
    "using",
    "want",
    "with",
    "would",
}

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)

REQUEST_ID_PATTERN = re.compile(r"^rtn-[a-z0-9]+(?:-[a-z0-9]+)*$")
PROFILE_KEYS = {
    "schema_version",
    "request_id",
    "research_need",
    "domain",
    "intended_outputs",
    "input_description",
    "candidate_roles",
    "constraints",
    "search",
    "success_criteria",
    "non_goals",
    "contains_real_data",
    "contains_secrets",
    "researcher_confirmed",
}
CONSTRAINT_KEYS = {
    "intended_data_classification",
    "must_run_locally",
    "open_source_required",
    "account_allowed",
    "paid_services_allowed",
    "available_compute",
    "max_cost_eur",
}
SEARCH_KEYS = {
    "indexes",
    "domain_terms",
    "outcome_terms",
    "synonyms",
    "required_terms",
    "excluded_terms",
    "explicit_candidate_ids",
}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path, *, max_bytes: int | None = None) -> Any:
    if path.is_symlink():
        raise ValueError(f"Expected a regular JSON file, not a symbolic link: {path}")
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"Expected a regular JSON file: {path}")
    size = path.stat().st_size
    if max_bytes is not None and size > max_bytes:
        raise ValueError(f"JSON file exceeds {max_bytes} bytes: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except UnicodeDecodeError as exc:
        raise ValueError(f"JSON must be UTF-8: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.name}: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def assert_metadata_only(profile: dict[str, Any]) -> None:
    for text in iter_strings(profile):
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                raise ValueError("Query profile contains credential- or secret-shaped content")

        compact = re.sub(r"\s+", "", text).upper()
        if len(compact) >= 80 and re.fullmatch(r"[ACGTUN]+", compact):
            raise ValueError("Query profile appears to contain a nucleotide sequence; describe modality and scale instead")

        for token in re.findall(r"[A-Za-z]+", text):
            if len(token) >= 100 and re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYBXZJUO]+", token.upper()):
                raise ValueError("Query profile appears to contain an amino-acid sequence; describe modality and scale instead")

        for token in re.findall(r"[A-Za-z0-9+/=]+", text):
            if len(token) >= 256 and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", token):
                raise ValueError("Query profile appears to contain a base64-like payload")


def require_string_list(value: Any, label: str, *, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{label} must be a list with at least {minimum} item(s)")
    if any(not isinstance(item, str) or len(item.strip()) < 2 for item in value):
        raise ValueError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} must not contain duplicates")
    return value


def validate_profile(profile: Any) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise ValueError("Query profile must be a JSON object")
    if set(profile) != PROFILE_KEYS:
        missing = sorted(PROFILE_KEYS - set(profile))
        extra = sorted(set(profile) - PROFILE_KEYS)
        raise ValueError(f"Query profile fields do not match the contract; missing={missing}, extra={extra}")
    if profile["schema_version"] != VERSION:
        raise ValueError(f"schema_version must be {VERSION}")
    if not isinstance(profile["request_id"], str) or not REQUEST_ID_PATTERN.fullmatch(profile["request_id"]):
        raise ValueError("request_id must match rtn-<lowercase-stable-id>")
    if not isinstance(profile["research_need"], str) or not 10 <= len(profile["research_need"].strip()) <= 2000:
        raise ValueError("research_need must contain 10 to 2000 characters")
    if not isinstance(profile["input_description"], str) or not 2 <= len(profile["input_description"].strip()) <= 1000:
        raise ValueError("input_description must contain 2 to 1000 characters")

    require_string_list(profile["domain"], "domain", minimum=1)
    require_string_list(profile["intended_outputs"], "intended_outputs", minimum=1)
    require_string_list(profile["success_criteria"], "success_criteria", minimum=1)
    require_string_list(profile["non_goals"], "non_goals")

    roles = require_string_list(profile["candidate_roles"], "candidate_roles", minimum=1)
    if not set(roles) <= set(INDEXES):
        raise ValueError(f"candidate_roles must use: {', '.join(INDEXES)}")

    constraints = profile["constraints"]
    if not isinstance(constraints, dict) or set(constraints) != CONSTRAINT_KEYS:
        raise ValueError("constraints fields do not match the contract")
    if constraints["intended_data_classification"] not in {
        "not_applicable", "public", "synthetic", "anonymized", "personal", "special_category", "unknown"
    }:
        raise ValueError("Invalid intended_data_classification")
    for key in ("must_run_locally", "open_source_required", "account_allowed", "paid_services_allowed"):
        if constraints[key] is not None and not isinstance(constraints[key], bool):
            raise ValueError(f"constraints.{key} must be true, false, or null")
    compute = require_string_list(constraints["available_compute"], "constraints.available_compute")
    if not set(compute) <= {"local_cpu", "local_gpu", "institutional_hpc", "institutional_cloud", "hosted_service", "unknown"}:
        raise ValueError("Invalid available_compute value")
    if constraints["max_cost_eur"] is not None and (
        not isinstance(constraints["max_cost_eur"], (int, float))
        or isinstance(constraints["max_cost_eur"], bool)
        or constraints["max_cost_eur"] < 0
    ):
        raise ValueError("constraints.max_cost_eur must be a non-negative number or null")

    search = profile["search"]
    if not isinstance(search, dict) or set(search) != SEARCH_KEYS:
        raise ValueError("search fields do not match the contract")
    indexes = require_string_list(search["indexes"], "search.indexes", minimum=1)
    if not set(indexes) <= set(INDEXES):
        raise ValueError(f"search.indexes must use: {', '.join(INDEXES)}")
    if set(indexes) != set(roles):
        raise ValueError("candidate_roles and search.indexes must contain the same indexes")
    require_string_list(search["domain_terms"], "search.domain_terms", minimum=1)
    require_string_list(search["outcome_terms"], "search.outcome_terms", minimum=1)
    require_string_list(search["synonyms"], "search.synonyms")
    require_string_list(search["required_terms"], "search.required_terms")
    require_string_list(search["excluded_terms"], "search.excluded_terms")
    explicit = require_string_list(search["explicit_candidate_ids"], "search.explicit_candidate_ids")
    allowed_prefixes = {ID_PREFIX[index] for index in indexes}
    if any(not any(candidate_id.startswith(prefix) for prefix in allowed_prefixes) for candidate_id in explicit):
        raise ValueError("An explicit candidate ID does not belong to a selected index")

    if profile["contains_real_data"] is not False:
        raise ValueError("contains_real_data must be false; provide metadata descriptions only")
    if profile["contains_secrets"] is not False:
        raise ValueError("contains_secrets must be false")
    if profile["researcher_confirmed"] is not True:
        raise ValueError("researcher_confirmed must be true before catalogue search")

    assert_metadata_only(profile)
    return profile


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def scalar_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, bool):
        return ["true" if value else "false"]
    if isinstance(value, (str, int, float)):
        return [str(value)]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(scalar_text(item))
        return result
    if isinstance(value, dict):
        result = []
        for key, item in value.items():
            result.append(str(key).replace("_", " "))
            result.extend(scalar_text(item))
        return result
    return []


def searchable_fields(index: str, record: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for field in FIELD_WEIGHTS[index]:
        values = scalar_text(record.get(field))
        if values:
            result[field] = " ".join(values)
    return result


def term_match(term: str, text: str) -> float:
    normalized_term = normalize_text(term)
    normalized_text = normalize_text(text)
    if not normalized_term or not normalized_text:
        return 0.0
    term_tokens = normalized_term.split()
    text_tokens = set(normalized_text.split())
    if f" {normalized_term} " in f" {normalized_text} ":
        return 1.5
    if all(token in text_tokens for token in term_tokens):
        return 1.0
    return 0.0


def raw_query_terms(research_need: str) -> list[str]:
    terms: list[str] = []
    for token in normalize_text(research_need).split():
        if len(token) < 3 or token in STOPWORDS or token.isdigit():
            continue
        if token not in terms:
            terms.append(token)
    return terms[:40]


def compile_query_terms(profile: dict[str, Any]) -> list[dict[str, Any]]:
    sources = {
        "required": profile["search"]["required_terms"],
        "outcome": profile["search"]["outcome_terms"],
        "domain": profile["search"]["domain_terms"],
        "synonym": profile["search"]["synonyms"],
        "research_need": raw_query_terms(profile["research_need"]),
    }
    merged: dict[str, dict[str, Any]] = {}
    for category, terms in sources.items():
        for term in terms:
            normalized = normalize_text(term)
            if not normalized:
                continue
            item = merged.setdefault(normalized, {"term": term, "normalized": normalized, "categories": [], "weight": 0.0})
            item["categories"].append(category)
            if QUERY_WEIGHTS[category] > item["weight"]:
                item["term"] = term
                item["weight"] = QUERY_WEIGHTS[category]
    return sorted(merged.values(), key=lambda item: (-item["weight"], item["normalized"]))


def record_match(index: str, record: dict[str, Any], query_terms: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    fields = searchable_fields(index, record)
    matched: list[dict[str, Any]] = []
    score = 0.0
    for query in query_terms:
        best_contribution = 0.0
        best_fields: list[str] = []
        for field, text in fields.items():
            match_strength = term_match(query["term"], text)
            if not match_strength:
                continue
            contribution = query["weight"] * FIELD_WEIGHTS[index][field] * match_strength
            if contribution > best_contribution:
                best_contribution = contribution
                best_fields = [field]
            elif contribution == best_contribution:
                best_fields.append(field)
        if best_contribution:
            score += best_contribution
            matched.append({
                "term": query["term"],
                "categories": sorted(query["categories"]),
                "fields": sorted(best_fields),
                "contribution": round(best_contribution, 3),
            })
    return round(score, 3), matched


def record_contains_term(index: str, record: dict[str, Any], term: str) -> bool:
    return any(term_match(term, text) for text in searchable_fields(index, record).values())


def collect_urls(value: Any) -> list[str]:
    urls: list[str] = []
    for text in iter_strings(value):
        if text.startswith(("https://", "http://")) and text not in urls:
            urls.append(text)
    return urls[:30]


def constraint_observations(index: str, record: dict[str, Any], constraints: dict[str, Any]) -> list[dict[str, str]]:
    observations: list[dict[str, str]] = []

    if constraints["open_source_required"] is True:
        if index == "foundation_models":
            status = str(record.get("status", ""))
            state = "supportive" if "open" in status.casefold() else "unknown"
            basis = f"Catalogue status: {status or 'not recorded'}"
        elif index == "autonomous_agents":
            access = str(record.get("access", ""))
            state = "supportive" if "open" in access.casefold() else "unknown"
            basis = f"Catalogue access: {access or 'not recorded'}"
        else:
            openness = str(record.get("openness", ""))
            license_name = record.get("software_license")
            if "open" in openness.casefold() or license_name:
                state = "supportive"
            elif "commercial" in openness.casefold() or "proprietary" in openness.casefold():
                state = "conflicting"
            else:
                state = "unknown"
            basis = f"Catalogue openness: {openness or 'not recorded'}; software licence: {license_name or 'not recorded'}"
        observations.append({"criterion": "open_source_required", "state": state, "basis": basis})

    if constraints["must_run_locally"] is True:
        if index == "coding_agents" and isinstance(record.get("runs_locally"), bool):
            state = "supportive" if record["runs_locally"] else "conflicting"
            basis = f"Catalogue runs_locally: {str(record['runs_locally']).lower()}"
        else:
            state = "unknown"
            basis = "The catalogue record does not establish an executable local route."
        observations.append({"criterion": "must_run_locally", "state": state, "basis": basis})

    if constraints["account_allowed"] is False:
        combined = " ".join(scalar_text(record)).casefold()
        if "api key" in combined or "account" in combined or "login" in combined:
            state = "possibly_conflicting"
            basis = "Catalogue prose mentions an account, login, or API key; current documentation must be checked."
        else:
            state = "unknown"
            basis = "Absence of account language in the catalogue does not prove account-free access."
        observations.append({"criterion": "account_allowed", "state": state, "basis": basis})

    if constraints["paid_services_allowed"] is False and index == "coding_agents":
        pricing = str(record.get("pricing", ""))
        state = "unknown"
        if pricing and "free" not in pricing.casefold():
            state = "possibly_conflicting"
        observations.append({
            "criterion": "paid_services_allowed",
            "state": state,
            "basis": f"Catalogue pricing: {pricing or 'not recorded'}",
        })

    return observations


def display_path(path: Path) -> str:
    resolved = path.resolve()
    for root in (WORKSPACE_ROOT, PROJECT_ROOT):
        try:
            return resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
    return resolved.name


def load_catalogue(path: Path, index: str) -> list[dict[str, Any]]:
    records = load_json(path)
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise ValueError(f"{index} catalogue must contain a JSON array of objects")
    seen: set[str] = set()
    for record in records:
        candidate_id = record.get("id")
        if not isinstance(candidate_id, str) or not candidate_id.startswith(ID_PREFIX[index]):
            raise ValueError(f"Invalid {index} catalogue candidate ID: {candidate_id!r}")
        if candidate_id in seen:
            raise ValueError(f"Duplicate catalogue candidate ID: {candidate_id}")
        seen.add(candidate_id)
    return records


def candidate_summary(index: str, record: dict[str, Any]) -> dict[str, Any]:
    fields = {
        field: record[field]
        for field in DISPLAY_FIELDS[index]
        if field in record and record[field] not in (None, "", [], {})
    }
    return {
        "candidate_id": record["id"],
        "name": record.get("name") or record.get("current_name") or record["id"],
        "index": index,
        "role": ROLE_LABEL[index],
        "catalogue_fields": fields,
        "source_urls": collect_urls(record),
    }


def parse_generated_at(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("generated_at must be an ISO-8601 timestamp") from exc
    return value


def search_catalogues(
    profile: dict[str, Any],
    catalogue_paths: dict[str, Path],
    *,
    limit_per_index: int = 10,
    generated_at: str | None = None,
) -> dict[str, Any]:
    validate_profile(profile)
    if not 1 <= limit_per_index <= 50:
        raise ValueError("limit_per_index must be between 1 and 50")

    query_terms = compile_query_terms(profile)
    required_terms = profile["search"]["required_terms"]
    excluded_terms = profile["search"]["excluded_terms"]
    explicit_ids = set(profile["search"]["explicit_candidate_ids"])
    all_ids: set[str] = set()
    results_by_index: dict[str, list[dict[str, Any]]] = {}
    snapshots: list[dict[str, Any]] = []
    total_matching = 0

    for index in profile["search"]["indexes"]:
        path = catalogue_paths[index]
        records = load_catalogue(path, index)
        all_ids.update(record["id"] for record in records)
        candidates: list[dict[str, Any]] = []

        for record in records:
            required_missing = [term for term in required_terms if not record_contains_term(index, record, term)]
            excluded_hits = [term for term in excluded_terms if record_contains_term(index, record, term)]
            if required_missing or excluded_hits:
                continue

            score, matched_terms = record_match(index, record, query_terms)
            explicitly_named = record["id"] in explicit_ids
            if explicitly_named:
                score += 1000.0
                matched_terms.insert(0, {
                    "term": record["id"],
                    "categories": ["explicit_candidate_id"],
                    "fields": ["id"],
                    "contribution": 1000.0,
                })
            if score <= 0:
                continue

            candidate = candidate_summary(index, record)
            candidate.update({
                "retrieval_score": round(score, 3),
                "matched_terms": matched_terms,
                "constraint_observations": constraint_observations(index, record, profile["constraints"]),
            })
            candidates.append(candidate)

        candidates.sort(key=lambda item: (-item["retrieval_score"], item["candidate_id"]))
        total_matching += len(candidates)
        selected = candidates[:limit_per_index]
        for position, candidate in enumerate(selected, start=1):
            candidate["retrieval_position_within_index"] = position
        results_by_index[index] = selected
        snapshots.append({
            "index": index,
            "source_file": display_path(path),
            "sha256": sha256_path(path),
            "record_count": len(records),
            "matching_record_count_before_limit": len(candidates),
            "returned_record_count": len(selected),
        })

    unknown_explicit = sorted(explicit_ids - all_ids)
    if unknown_explicit:
        raise ValueError(f"Explicit candidate ID not found in selected catalogues: {unknown_explicit[0]}")

    returned = sum(len(items) for items in results_by_index.values())
    return {
        "schema_version": VERSION,
        "generated_at": parse_generated_at(generated_at),
        "request_id": profile["request_id"],
        "query_profile_sha256": sha256_bytes(canonical_json_bytes(profile)),
        "method": {
            "name": "transparent_weighted_lexical_retrieval",
            "retrieval_ordering_performed": True,
            "suitability_ranking_performed": False,
            "winner_selected": False,
            "query_term_weights": QUERY_WEIGHTS,
            "field_weights": {index: FIELD_WEIGHTS[index] for index in profile["search"]["indexes"]},
            "compiled_terms": query_terms,
        },
        "catalogue_snapshots": snapshots,
        "results_by_index": results_by_index,
        "summary": {
            "matching_records_before_limit": total_matching,
            "returned_records": returned,
            "zero_results": returned == 0,
        },
        "limitations": [
            "Retrieval is lexical and depends on the confirmed terms and catalogue wording.",
            "The retrieval score orders discovery results only; it is not a suitability or evidence score.",
            "Catalogue constraint observations are leads for verification, not current evidence conclusions.",
            "The three catalogues may be incomplete or stale; important public leads may be absent.",
            "Candidate comparison requires current public evidence and researcher-defined criteria.",
        ],
    }


def catalogue_paths_from_args(args: argparse.Namespace) -> dict[str, Path]:
    return {
        "foundation_models": Path(args.foundation_catalogue),
        "autonomous_agents": Path(args.autonomous_catalogue),
        "coding_agents": Path(args.coding_catalogue),
    }


def write_json(path: Path, value: Any, *, force: bool = False) -> None:
    if path.exists() and not force:
        raise ValueError(f"Output already exists; use --force to replace it: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def add_catalogue_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--foundation-catalogue", default=str(DEFAULT_CATALOGUES["foundation_models"]))
    parser.add_argument("--autonomous-catalogue", default=str(DEFAULT_CATALOGUES["autonomous_agents"]))
    parser.add_argument("--coding-catalogue", default=str(DEFAULT_CATALOGUES["coding_agents"]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    stats_parser = subparsers.add_parser("stats", help="Show catalogue counts and hashes")
    add_catalogue_arguments(stats_parser)

    validate_parser = subparsers.add_parser("validate-profile", help="Validate a confirmed query profile")
    validate_parser.add_argument("profile")

    search_parser = subparsers.add_parser("search", help="Search catalogues using a confirmed query profile")
    search_parser.add_argument("--profile", required=True)
    search_parser.add_argument("--limit-per-index", type=int, default=10)
    search_parser.add_argument("--generated-at")
    search_parser.add_argument("--output")
    search_parser.add_argument("--force", action="store_true")
    add_catalogue_arguments(search_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-profile":
            profile = load_json(Path(args.profile), max_bytes=512 * 1024)
            validate_profile(profile)
            print(json.dumps({"status": "valid", "request_id": profile["request_id"], "schema_version": VERSION}))
            return 0

        paths = catalogue_paths_from_args(args)
        if args.command == "stats":
            snapshots = []
            for index in INDEXES:
                records = load_catalogue(paths[index], index)
                snapshots.append({
                    "index": index,
                    "source_file": display_path(paths[index]),
                    "sha256": sha256_path(paths[index]),
                    "record_count": len(records),
                })
            print(json.dumps({"schema_version": VERSION, "catalogues": snapshots}, indent=2, sort_keys=True))
            return 0

        if args.command == "search":
            profile = load_json(Path(args.profile), max_bytes=512 * 1024)
            result = search_catalogues(
                profile,
                paths,
                limit_per_index=args.limit_per_index,
                generated_at=args.generated_at,
            )
            if args.output:
                write_json(Path(args.output), result, force=args.force)
                print(json.dumps({
                    "status": "written",
                    "output": str(Path(args.output)),
                    "returned_records": result["summary"]["returned_records"],
                }))
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
            return 0


        parser.error("Unknown command")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
