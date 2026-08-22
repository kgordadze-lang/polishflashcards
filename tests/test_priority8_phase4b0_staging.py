import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import validate_priority8_staging as validator  # noqa: E402


STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"
B0_BASELINE_FIXTURE = ROOT / "tests/fixtures/priority8_phase4b0_staging_baseline.json"
BOUNDARY_PATHS = [
    ROOT / "editorial/verb-pattern-candidates.json",
    ROOT / "editorial/priority-7-authoring-context.json",
    ROOT / "priority7_tooling.py",
    ROOT / "pp-verb-patterns.js",
    ROOT / "content/verb-patterns.json",
    ROOT / "index.html",
    ROOT / "sw.js",
    ROOT / "audio-manifest.json",
    ROOT / "generate_audio.py",
    ROOT / "pp_audio_rule.py",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(data, lemma):
    return next(item for item in data["lemmas"]
                if item["canonicalLemma"] == lemma)


class Priority8Phase4B0StagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Frozen pre-authoring B0 baseline, not the live staging file, which
        # advances past B0 once later batches are authored.
        cls.real = json.loads(B0_BASELINE_FIXTURE.read_text(encoding="utf-8"))

    def mutated(self):
        return copy.deepcopy(self.real)

    def assert_invalid(self, data, expected_fragment):
        issues = validator.validate_data(data)
        self.assertTrue(issues, "mutated staging unexpectedly validated")
        self.assertTrue(
            any(expected_fragment in issue for issue in issues),
            f"missing {expected_fragment!r} in issues: {issues}",
        )

    def run_validator(self):
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(ROOT / "validate_priority8_staging.py")],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_real_staging_file_validates(self):
        self.assertEqual([], validator.validate_data(self.real))

    def test_rejects_67_lemmas(self):
        data = self.mutated()
        data["lemmas"].pop()
        self.assert_invalid(data, "exactly 68 records")

    def test_rejects_69_lemmas_extra_reserve(self):
        data = self.mutated()
        extra = copy.deepcopy(data["lemmas"][0])
        extra["verificationOrder"] = 71
        extra["canonicalLemma"] = "unauthorized-reserve"
        extra["phase3Evidence"]["verificationOrder"] = 71
        extra["bindingConstraints"] = []
        data["lemmas"].append(extra)
        self.assert_invalid(data, "exactly 68 records")

    def test_rejects_wrong_order(self):
        data = self.mutated()
        data["lemmas"][0], data["lemmas"][1] = (
            data["lemmas"][1], data["lemmas"][0]
        )
        self.assert_invalid(data, "verification order/membership sequence")

    def test_rejects_duplicate_lemma(self):
        data = self.mutated()
        data["lemmas"][1]["canonicalLemma"] = "pracować"
        self.assert_invalid(data, "duplicate canonicalLemma")

    def test_rejects_zaczynac_as_full_pattern(self):
        data = self.mutated()
        data["lemmas"][0]["canonicalLemma"] = "zaczynać"
        self.assert_invalid(data, "metadata-only identities cannot be full-pattern")

    def test_rejects_przeczytac_as_full_pattern(self):
        data = self.mutated()
        data["lemmas"][0]["canonicalLemma"] = "przeczytać"
        self.assert_invalid(data, "metadata-only identities cannot be full-pattern")

    def test_rejects_missing_metadata_only_partner(self):
        data = self.mutated()
        record(data, "zacząć").pop("metadataAspectPartner")
        self.assert_invalid(data, "metadataAspectPartner occurrences must be exactly")

    def test_rejects_wrong_metadata_only_partner(self):
        data = self.mutated()
        record(data, "zacząć")["metadataAspectPartner"]["canonicalLemma"] = "czytać"
        self.assert_invalid(data, "metadataAspectPartner occurrences must be exactly")

    def test_rejects_metadata_partner_on_wrong_anchor(self):
        data = self.mutated()
        partner = record(data, "zacząć").pop("metadataAspectPartner")
        record(data, "pracować")["metadataAspectPartner"] = partner
        self.assert_invalid(data, "metadataAspectPartner occurrences must be exactly")

    def test_rejects_vp_l_value_recursively(self):
        data = self.mutated()
        record(data, "pracować")["phase3Evidence"]["primarySourceKey"] = "vp-l-test"
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_rejects_vp_m_value_recursively(self):
        data = self.mutated()
        record(data, "pracować")["phase3Evidence"]["primarySourceKey"] = "vp-m-test"
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_rejects_vp_p_value_recursively(self):
        data = self.mutated()
        record(data, "pracować")["phase3Evidence"]["primarySourceKey"] = "vp-p-test"
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_rejects_vp_e_value_recursively(self):
        data = self.mutated()
        record(data, "pracować")["phase3Evidence"]["primarySourceKey"] = "vp-e-test"
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_rejects_vp_x_value_recursively(self):
        data = self.mutated()
        record(data, "pracować")["phase3Evidence"]["primarySourceKey"] = "vp-x-test"
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_rejects_production_id_field_name(self):
        data = self.mutated()
        record(data, "pracować")["meaningId"] = "not-even-a-vp-value"
        self.assert_invalid(data, "production-ID field name is prohibited")

    def test_rejects_missing_one_of_21_constraints(self):
        data = self.mutated()
        record(data, "pracować")["bindingConstraints"] = []
        self.assert_invalid(data, "bindingConstraints does not match")

    def test_rejects_constraint_attached_to_wrong_lemma(self):
        data = self.mutated()
        constraint = copy.deepcopy(record(data, "pracować")["bindingConstraints"])
        record(data, "pracować")["bindingConstraints"] = []
        record(data, "robić")["bindingConstraints"] = constraint
        self.assert_invalid(data, "bindingConstraints does not match")

    def test_rejects_missing_udzial_on_brac(self):
        data = self.mutated()
        record(data, "brać").pop("requiredLexicalItems")
        self.assert_invalid(data, "requiredLexicalItems must equal")

    def test_rejects_missing_udzial_on_wziac(self):
        data = self.mutated()
        record(data, "wziąć").pop("requiredLexicalItems")
        self.assert_invalid(data, "requiredLexicalItems must equal")

    def test_rejects_udzial_on_unrelated_lemma(self):
        data = self.mutated()
        record(data, "pracować")["requiredLexicalItems"] = ["udział"]
        self.assert_invalid(data, "allowed only on brać and wziąć")

    def test_rejects_authored_candidate_meaning(self):
        data = self.mutated()
        record(data, "pracować")["candidateContent"]["meanings"].append({
            "candidateMeaningKey": "production-work"
        })
        self.assert_invalid(data, "meanings must be empty in Phase 4B0")

    def test_rejects_authored_candidate_pattern(self):
        data = self.mutated()
        record(data, "pracować")["candidateContent"]["patterns"].append({
            "candidatePatternKey": "nad-instrumental"
        })
        self.assert_invalid(data, "patterns must be empty in Phase 4B0")

    def test_rejects_authored_candidate_example(self):
        data = self.mutated()
        record(data, "pracować")["candidateContent"]["examples"].append({
            "candidateExampleKey": "work-on-script"
        })
        self.assert_invalid(data, "examples must be empty in Phase 4B0")

    def test_rejects_non_draft_phase4b0_status(self):
        data = self.mutated()
        record(data, "pracować")["stagingReviewStatus"] = "independently-reviewed"
        self.assert_invalid(data, "must be draft in Phase 4B0")

    def test_rejects_bad_staging_envelope_baseline(self):
        data = self.mutated()
        data["startingIntegrationBaseline"]["head"] = "0" * 40
        self.assert_invalid(data, "startingIntegrationBaseline")

    def test_rejects_malformed_future_candidate_key(self):
        data = self.mutated()
        record(data, "pracować")["candidateContent"]["meanings"].append({
            "candidateMeaningKey": "Not Kebab"
        })
        self.assert_invalid(data, "candidate key must use lowercase kebab-case")

    def test_candidate_key_identity_is_not_global(self):
        fixture = {
            "lemmas": [
                {"owner": "pracować", "candidateMeaningKey": "core"},
                {"owner": "iść", "candidateMeaningKey": "core"},
            ]
        }
        issues = []
        validator._check_recursive_prohibitions(fixture, issues)
        self.assertFalse(
            any("duplicate candidateMeaningKey" in issue for issue in issues),
            issues,
        )
        self.assertFalse(
            any("candidate key must use" in issue for issue in issues),
            issues,
        )
        self.assertEqual(
            2,
            sum("candidate keys are prohibited in Phase 4B0" in issue
                for issue in issues),
        )

    def test_validator_does_not_mutate_staging_file(self):
        before = digest(STAGING_PATH)
        result = self.run_validator()
        after = digest(STAGING_PATH)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before, after)

    def test_validation_is_deterministic(self):
        first_issues = validator.validate_data(self.real)
        second_issues = validator.validate_data(self.real)
        self.assertEqual(first_issues, second_issues)
        first = self.run_validator()
        second = self.run_validator()
        self.assertEqual((first.returncode, first.stdout, first.stderr),
                         (second.returncode, second.stdout, second.stderr))

    def test_no_runtime_or_canonical_generation_occurs(self):
        before_hashes = {str(path): digest(path) for path in BOUNDARY_PATHS}
        before_content_files = sorted(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "content").rglob("*") if path.is_file()
        )
        result = self.run_validator()
        after_hashes = {str(path): digest(path) for path in BOUNDARY_PATHS}
        after_content_files = sorted(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "content").rglob("*") if path.is_file()
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before_hashes, after_hashes)
        self.assertEqual(before_content_files, after_content_files)


if __name__ == "__main__":
    unittest.main()
