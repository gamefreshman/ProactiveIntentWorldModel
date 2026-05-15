from pathlib import Path

from piwm_data.tests.test_exporters import make_record
from scripts import compatibility_report


def test_compatibility_report_includes_extended_rederivation_audit():
    report = compatibility_report.build_report([make_record()], Path("main_schema.jsonl"))

    assert "## Basic Schema Compatibility Tiers" in report
    assert "## Extended V2 Re-derivation Audit" in report
    assert "## Official 543 Re-derived V2 Policy Best Distribution" in report
    assert "Basic `yellow=0` is a detector-scope result" in report
