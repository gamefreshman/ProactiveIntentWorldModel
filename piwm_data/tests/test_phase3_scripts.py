import json

from scripts import prompt_builder, scenario_sampler


def test_scenario_sampler_builds_full_rule_space_counts():
    scenarios = scenario_sampler.build_all_scenarios(seed=42)
    stats = scenario_sampler.scenario_stats(scenarios)
    assert stats["n_scenarios"] == 1920
    assert stats["split_counts"]["ood_product"] == 240
    assert stats["split_counts"]["ood_persona"] == 280
    assert sum(stats["split_counts"].values()) == 1920
    assert stats["viewpoint_counts"] == {
        "salesperson_observable": 1536,
        "surveillance_oblique": 384,
    }
    assert all(item["source_rule_ids"] for item in scenarios)
    assert all(item["viewpoint"] in scenario_sampler.rules.VIEWPOINTS for item in scenarios)
    assert stats["intent_tier_counts"] == {
        "exploring": 960,
        "low_intent_browsing": 320,
        "ready_to_buy": 640,
    }
    assert stats["candidate_rule_coverage_counts"] == {
        "default_fallback": 1056,
        "explicit": 864,
    }
    assert stats["n_explicit_candidate_rule_scenarios"] == 864
    assert set(stats["best_dialogue_act_counts"]).issubset(set(scenario_sampler.rules.DIALOGUE_ACTS))
    assert stats["policy_best_dialogue_act_counts"]["Recommend"] > 0
    assert stats["explicit_policy_best_dialogue_act_counts"] == {
        "Elicit": 272,
        "Hold": 96,
        "Inform": 136,
        "Recommend": 360,
    }
    assert "Reassure" not in stats["explicit_policy_best_dialogue_act_counts"]


def test_scenario_sampler_writes_v2_action_specs_and_intent_tier_filter():
    scenario = next(
        item
        for item in scenario_sampler.build_all_scenarios(seed=42)
        if item["persona_type"] == "browser_low_intent"
        and item["target_cue"] == "brief_glance_walking_past"
        and item["aida_stage"] == "attention"
    )

    assert scenario["derived"]["intent_tier"] == "low_intent_browsing"
    assert scenario["derived"]["candidate_rule_coverage"] == "explicit"
    assert scenario["derived"]["candidate_actions"] == ["A1_silent_observe", "A6_acknowledge_and_wait"]
    assert scenario["derived"]["candidate_action_specs"][0] == {"act": "Hold", "params": {"mode": "silent"}}
    assert all(spec["act"] != "Recommend" for spec in scenario["derived"]["policy_candidate_specs"])
    assert scenario["derived"]["best_action_spec"]["act"] in scenario_sampler.rules.DIALOGUE_ACTS
    assert scenario["derived"]["policy_best_action_spec"]["act"] in scenario_sampler.rules.DIALOGUE_ACTS
    assert any(item.startswith("PIT_") for item in scenario["source_rule_ids"])
    assert any("intent_tier_filter_removed:A3_strong_recommend" in item for item in scenario["runtime_fallbacks"])


def test_scenario_sampler_policy_path_can_select_soft_recommend():
    scenario = next(
        item
        for item in scenario_sampler.build_all_scenarios(seed=42)
        if item["persona_type"] == "price_insensitive_decisive"
        and item["target_cue"] == "approaching_counter"
        and item["aida_stage"] == "action"
    )

    assert {"act": "Recommend", "params": {"target": "item", "pressure": "soft"}} in scenario["derived"]["policy_candidate_specs"]
    assert scenario["derived"]["policy_best_action_spec"] == {"act": "Recommend", "params": {"target": "item", "pressure": "soft"}}


def test_scenario_sampler_balanced_limit_covers_all_cues():
    scenarios = scenario_sampler.build_all_scenarios(seed=42)
    selected = scenario_sampler.select_scenarios(scenarios, limit=10, seed=42, balanced_cues=True)
    assert len(selected) == 10
    assert {item["target_cue"] for item in selected} == set(scenario_sampler.rules.CUES)
    assert {item["viewpoint"] for item in selected} == {"salesperson_observable", "surveillance_oblique"}
    assert sum(item["viewpoint"] == "salesperson_observable" for item in selected) == 8
    assert sum(item["viewpoint"] == "surveillance_oblique" for item in selected) == 2


def test_scenario_sampler_cli_writes_manifest_and_stats(tmp_path):
    out = tmp_path / "scenario_manifest.jsonl"
    exit_code = scenario_sampler.main(["--out", str(out), "--limit", "10", "--balanced-cues"])
    assert exit_code == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 10
    assert (tmp_path / "_scenario_stats.json").exists()
    assert rows[0]["session_id"].startswith("piwm_")
    assert "viewpoint" in rows[0]


def test_scenario_sampler_candidate_rule_only_filters_default_fallbacks(tmp_path):
    out = tmp_path / "scenario_manifest.jsonl"
    exit_code = scenario_sampler.main(["--out", str(out), "--candidate-rule-only"])
    assert exit_code == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    stats = json.loads((tmp_path / "_scenario_stats.json").read_text(encoding="utf-8"))
    assert len(rows) == 864
    assert stats["candidate_rule_coverage_counts"] == {"explicit": 864}
    assert {row["derived"]["candidate_rule_coverage"] for row in rows} == {"explicit"}


def test_prompt_builder_outputs_four_layer_prompt_without_internal_labels():
    scenario = scenario_sampler.select_scenarios(
        scenario_sampler.build_all_scenarios(seed=42),
        limit=1,
        seed=42,
        balanced_cues=True,
    )[0]
    prompt_json = prompt_builder.build_prompt_json(scenario)
    assert prompt_json["viewpoint"] in prompt_builder.rules.VIEWPOINTS
    assert prompt_json["sampler"]["version"] == "phase3_viewpoint_v1"
    assert prompt_json["kling_prompt_sections"]["camera"]
    assert prompt_json["kling_prompt_sections"]["scene"]
    assert prompt_json["kling_prompt_sections"]["behavior_timeline"]
    assert prompt_json["kling_prompt_sections"]["negative"]
    assert len(prompt_json["frame_sampling_plan"]) == 3
    assert prompt_builder.forbidden_label_hits(prompt_json["kling_prompt"]) == []


def test_brief_glance_prompt_prevents_stopping_at_display():
    scenario = next(
        item
        for item in scenario_sampler.build_all_scenarios(seed=42)
        if item["target_cue"] == "brief_glance_walking_past"
        and item["viewpoint"] == "surveillance_oblique"
    )
    prompt_json = prompt_builder.build_prompt_json(scenario)
    prompt = prompt_json["kling_prompt"]
    assert "clear walking path" in prompt
    assert "no stopping at the display" in prompt
    assert "no close product inspection" in prompt
    assert "feet keep moving" in prompt
    assert "full body and head direction visible" in prompt


def test_prompt_builder_cli_writes_prompt_jsons(tmp_path):
    manifest = tmp_path / "scenario_manifest.jsonl"
    scenarios = scenario_sampler.select_scenarios(
        scenario_sampler.build_all_scenarios(seed=42),
        limit=2,
        seed=42,
        balanced_cues=True,
    )
    scenario_sampler.write_jsonl(scenarios, manifest)
    out_root = tmp_path / "Archive_prompts"
    exit_code = prompt_builder.main(["--manifest", str(manifest), "--out-root", str(out_root)])
    assert exit_code == 0
    prompt_paths = sorted(out_root.glob("*/prompt.json"))
    assert len(prompt_paths) == 2
    prompt = json.loads(prompt_paths[0].read_text(encoding="utf-8"))
    assert "kling_prompt" in prompt
    assert prompt["product_category"]
    assert prompt["sampler"]["version"] == "phase3_viewpoint_v1"
    assert prompt["persona"]["type"]
    assert prompt["viewpoint"]
