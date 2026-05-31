from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "figures_batch1"

CLASSES = ["Greet", "Elicit", "Inform", "Recommend", "Hold"]
DATA = {
    "PIWM": [0.800, 0.750, 0.714, 0.600, 0.250],
    "State-Outcome Model": [0.000, 0.286, 0.182, 0.250, 0.417],
    "Qwen2.5-VL-7B (zero-shot)": [0.000, 0.286, 0.000, 0.286, 0.200],
}
COLORS = {
    "PIWM": "#1d4ed8",
    "State-Outcome Model": "#64748b",
    "Qwen2.5-VL-7B (zero-shot)": "#94a3b8",
}


def main():
    angles = np.linspace(0, 2 * np.pi, len(CLASSES), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6.2, 6.0), subplot_kw={"polar": True})
    for model, values in DATA.items():
        vals = values + values[:1]
        is_piwm = model == "PIWM"
        ax.plot(
            angles,
            vals,
            label=model,
            color=COLORS[model],
            linewidth=3.0 if is_piwm else 1.5,
            linestyle="-" if is_piwm else "--",
            alpha=1.0 if is_piwm else 0.75,
        )
        ax.fill(angles, vals, color=COLORS[model], alpha=0.14 if is_piwm else 0.06)

    ax.set_xticks(angles[:-1], CLASSES)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=10)
    ax.set_title("Per-Class F1 on Target-Test (n=30)", pad=18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=1, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "V4_per_class_radar.pdf", bbox_inches="tight")
    fig.savefig(OUT / "V4_per_class_radar.png", dpi=220, bbox_inches="tight")


if __name__ == "__main__":
    main()
