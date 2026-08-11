from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.navigator import load_json, search_catalogues, validate_profile


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
CATALOGUES = {
    "foundation_models": FIXTURES / "foundation.json",
    "autonomous_agents": FIXTURES / "autonomous.json",
    "coding_agents": FIXTURES / "coding.json",
}


def fixture_profile() -> dict:
    return load_json(FIXTURES / "query-profile.json")


class QueryProfileTests(unittest.TestCase):
    def test_valid_profile_is_accepted(self) -> None:
        profile = fixture_profile()
        self.assertIs(validate_profile(profile), profile)

    def test_unconfirmed_profile_is_rejected(self) -> None:
        profile = fixture_profile()
        profile["researcher_confirmed"] = False
        with self.assertRaisesRegex(ValueError, "researcher_confirmed"):
            validate_profile(profile)

    def test_real_data_flag_is_rejected(self) -> None:
        profile = fixture_profile()
        profile["contains_real_data"] = True
        with self.assertRaisesRegex(ValueError, "contains_real_data"):
            validate_profile(profile)

    def test_sequence_like_payload_is_rejected(self) -> None:
        profile = fixture_profile()
        profile["input_description"] = "MELK" * 30
        with self.assertRaisesRegex(ValueError, "amino-acid sequence"):
            validate_profile(profile)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "duplicate.json"
            path.write_text('{"schema_version":"0.1.0","schema_version":"0.1.0"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_json(path)

    def test_symbolic_link_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "profile.json"
            link = Path(temp_dir) / "profile-link.json"
            target.write_text("{}", encoding="utf-8")
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                load_json(link)


class SearchTests(unittest.TestCase):
    def test_retrieves_relevant_candidate_from_each_index(self) -> None:
        result = search_catalogues(
            fixture_profile(),
            CATALOGUES,
            limit_per_index=1,
            generated_at="2026-08-11T06:30:00Z",
        )
        self.assertEqual(result["results_by_index"]["foundation_models"][0]["candidate_id"], "bfm-cell-encoder")
        self.assertEqual(result["results_by_index"]["autonomous_agents"][0]["candidate_id"], "asa-cell-workflow")
        self.assertEqual(result["results_by_index"]["coding_agents"][0]["candidate_id"], "rca-local-cell-analysis")
        self.assertEqual(result["summary"]["returned_records"], 3)
        self.assertFalse(result["method"]["suitability_ranking_performed"])

    def test_required_and_excluded_terms_are_hard_filters(self) -> None:
        profile = fixture_profile()
        profile["candidate_roles"] = ["coding_agents"]
        profile["search"]["indexes"] = ["coding_agents"]
        profile["search"]["required_terms"] = ["local"]
        profile["search"]["excluded_terms"] = ["cloud"]
        result = search_catalogues(
            profile,
            CATALOGUES,
            limit_per_index=10,
            generated_at="2026-08-11T06:30:00Z",
        )
        ids = [item["candidate_id"] for item in result["results_by_index"]["coding_agents"]]
        self.assertEqual(ids, ["rca-local-cell-analysis"])

    def test_explicit_candidate_enters_retrieval(self) -> None:
        profile = fixture_profile()
        profile["candidate_roles"] = ["foundation_models"]
        profile["search"]["indexes"] = ["foundation_models"]
        profile["search"]["explicit_candidate_ids"] = ["bfm-molecule-generator"]
        result = search_catalogues(
            profile,
            CATALOGUES,
            limit_per_index=2,
            generated_at="2026-08-11T06:30:00Z",
        )
        self.assertEqual(result["results_by_index"]["foundation_models"][0]["candidate_id"], "bfm-molecule-generator")

    def test_unknown_explicit_candidate_is_rejected(self) -> None:
        profile = fixture_profile()
        profile["candidate_roles"] = ["foundation_models"]
        profile["search"]["indexes"] = ["foundation_models"]
        profile["search"]["explicit_candidate_ids"] = ["bfm-not-present"]
        with self.assertRaisesRegex(ValueError, "not found"):
            search_catalogues(profile, CATALOGUES, generated_at="2026-08-11T06:30:00Z")

    def test_output_is_deterministic_with_fixed_timestamp(self) -> None:
        first = search_catalogues(
            fixture_profile(),
            CATALOGUES,
            limit_per_index=2,
            generated_at="2026-08-11T06:30:00Z",
        )
        second = search_catalogues(
            fixture_profile(),
            CATALOGUES,
            limit_per_index=2,
            generated_at="2026-08-11T06:30:00Z",
        )
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
