"""Chinese annotation terms for the operational 5-act salesperson workflow."""

from __future__ import annotations


OPERATIONAL_5ACTS = ("Greet", "Elicit", "Inform", "Recommend", "Hold")

HOLD_CN = "继续观察等待"

CN_TO_EN_ACT = {
    "问候": "Greet",
    "询问需求": "Elicit",
    "介绍信息": "Inform",
    "推荐商品": "Recommend",
    HOLD_CN: "Hold",
}

EN_TO_CN_ACT = {english: chinese for chinese, english in CN_TO_EN_ACT.items()}

CN_ACT_OPTIONS = tuple(CN_TO_EN_ACT.keys())
