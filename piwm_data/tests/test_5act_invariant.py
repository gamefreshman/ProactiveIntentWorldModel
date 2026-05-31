from __future__ import annotations

import json
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from piwm_data.annotation_act_terms import (
    CN_ACT_OPTIONS,
    CN_TO_EN_ACT,
    EN_TO_CN_ACT,
    HOLD_CN,
    OPERATIONAL_5ACTS as OPERATIONAL_5ACT_ORDER,
)
from piwm_data import rules
from scripts import build_salesperson_annotation_pack_v2 as annotation_pack
from scripts import convert_salesperson_annotation_export as annotation_converter


ROOT = Path(__file__).resolve().parents[2]
GENERAL_V2_DIR = ROOT / "data/official/piwm_train_synth_v2"
MS_SWIFT_DIR = ROOT / "data/official/ms_swift"
DOMAIN_EVAL_DIR = ROOT / "data/official/domain_specialization_eval_v2"

OPERATIONAL_5ACTS = {"Greet", "Elicit", "Inform", "Recommend", "Hold"}
ANNOTATION_PACK_DIR = ROOT / "data/official/annotation_pack_v2"


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _act_from_action_payload(payload: dict) -> str | None:
    spec = payload.get("action_spec") or payload.get("dialogue_act") or {}
    return spec.get("act")


def test_general_v2_operational_policy_has_no_reassure_candidates_or_best() -> None:
    rows = _read_jsonl(GENERAL_V2_DIR / "main_schema.jsonl")
    assert rows

    leaks: list[tuple[str, str]] = []
    for row in rows:
        state_id = row["state_id"]
        if (row.get("best_action_spec") or {}).get("act") == "Reassure":
            leaks.append((state_id, "best_action_spec"))
        if row.get("dialogue_act") == "Reassure":
            leaks.append((state_id, "dialogue_act"))
        for spec in row.get("candidate_action_specs") or []:
            if spec.get("act") == "Reassure":
                leaks.append((state_id, "candidate_action_specs"))
        for key, outcome in (row.get("next_state_by_action_v2") or {}).items():
            if outcome.get("dialogue_act") == "Reassure":
                leaks.append((state_id, f"next_state_by_action_v2.{key}"))

    assert leaks == []


def test_general_v2_policy_preference_has_no_reassure_and_uses_operational_acts() -> None:
    rows = _read_jsonl(GENERAL_V2_DIR / "policy_preference.jsonl")
    assert rows

    leaks: list[tuple[str, str, str | None]] = []
    for row in rows:
        for side in ("chosen_json", "rejected_json"):
            act = _act_from_action_payload(row.get(side, {}))
            if act == "Reassure" or act not in OPERATIONAL_5ACTS:
                leaks.append((row["state_id"], side, act))
        for item in (row.get("meta") or {}).get("candidate_block", []):
            act = _act_from_action_payload(item)
            if act == "Reassure" or act not in OPERATIONAL_5ACTS:
                leaks.append((row["state_id"], "candidate_block", act))

    assert leaks == []


def test_runtime_policy_candidate_export_has_no_reassure() -> None:
    rows = _read_jsonl(GENERAL_V2_DIR / "main_schema.jsonl")
    leaks: list[tuple[str, list[str]]] = []
    for row in rows:
        specs = rules.derive_policy_candidate_specs(
            row["latent_state"],
            row["aida_stage"],
            (row.get("persona") or {}).get("intent_tier"),
        )
        acts = [spec["act"] for spec in specs]
        if "Reassure" in acts:
            leaks.append((row["state_id"], acts))
    assert leaks == []


def test_generated_operational_training_and_eval_jsonl_have_no_reassure() -> None:
    paths = [
        MS_SWIFT_DIR / "piwm_train_synth_v2.jsonl",
        MS_SWIFT_DIR / "piwm_train_stage1_user_intent_v1.jsonl",
        MS_SWIFT_DIR / "piwm_train_stage2_target_5act_v1.jsonl",
        MS_SWIFT_DIR / "piwm_train_stage1_plus_stage2_target_5act_v1.jsonl",
        DOMAIN_EVAL_DIR / "target_frontcam_5act_test_action_selection.jsonl",
        DOMAIN_EVAL_DIR / "target_frontcam_5act_test_all.jsonl",
        DOMAIN_EVAL_DIR / "general_qa_stage1_all.jsonl",
    ]
    leaks: list[tuple[str, str]] = []
    for path in paths:
        for row in _read_jsonl(path):
            if row.get("task") != "action_selection_5act":
                continue
            text = json.dumps(row, ensure_ascii=False)
            if "Reassure" in text or "Reassure_" in text:
                leaks.append((path.as_posix(), row.get("source_id", "")))
    assert leaks == []


def test_cn_to_en_act_mapping_round_trip_has_no_missing_or_duplicate_terms() -> None:
    assert tuple(CN_TO_EN_ACT.values()) == OPERATIONAL_5ACT_ORDER
    assert set(CN_TO_EN_ACT.values()) == OPERATIONAL_5ACTS
    assert len(CN_TO_EN_ACT) == len(OPERATIONAL_5ACTS)
    assert len(set(CN_TO_EN_ACT.keys())) == len(OPERATIONAL_5ACTS)
    assert len(set(CN_TO_EN_ACT.values())) == len(OPERATIONAL_5ACTS)

    for chinese, english in CN_TO_EN_ACT.items():
        assert EN_TO_CN_ACT[english] == chinese

    assert HOLD_CN == "继续观察等待"
    assert CN_TO_EN_ACT[HOLD_CN] == "Hold"


def test_annotation_template_dropdown_terms_match_converter_mapping() -> None:
    assert tuple(annotation_pack.ACT_DROPDOWN_OPTIONS) == tuple(annotation_converter.CN_TO_EN_ACT.keys())
    assert annotation_converter.ACT_ZH_TO_EN == annotation_converter.CN_TO_EN_ACT
    assert tuple(annotation_pack.ACT_DROPDOWN_OPTIONS) == CN_ACT_OPTIONS

    score_column_terms = {
        score_column.removesuffix("适合度(1-5)")
        for score_column, _ in annotation_converter.ACT_SCORE_COLUMNS.values()
    }
    assert score_column_terms == set(CN_TO_EN_ACT.keys())


def test_generated_annotation_excel_act_dropdowns_match_converter_mapping() -> None:
    workbook_path = ANNOTATION_PACK_DIR / "annotation_template_three_annotators.xlsx"
    if not workbook_path.exists():
        pytest.skip("annotation xlsx is a generated local artifact; build annotation_pack_v2 first")

    action_formula = '"' + ",".join(CN_TO_EN_ACT.keys()) + '"'
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    with ZipFile(workbook_path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels_xml = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rels = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_xml}
        sheet_targets: dict[str, str] = {}
        for sheet in workbook.find("x:sheets", ns):
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rels[rid]
            if target.startswith("/"):
                target = target.lstrip("/")
            elif not target.startswith("xl/"):
                target = "xl/" + target
            sheet_targets[sheet.attrib["name"]] = target

        assert {"售货员A", "售货员B", "售货员C"} <= set(sheet_targets)

        for sheet_name in ("售货员A", "售货员B", "售货员C"):
            worksheet = ET.fromstring(archive.read(sheet_targets[sheet_name]))
            formulas = [
                formula.text
                for validation in worksheet.findall(".//x:dataValidation", ns)
                for formula in validation.findall("x:formula1", ns)
            ]
            assert formulas.count(action_formula) == 4
