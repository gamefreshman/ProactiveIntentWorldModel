# Equation and Layout Fix Suggestions

Source basis: `tmp/overleaf_edit/acl_latex_after.tex` (latest local Overleaf mirror) and `paper/main.tex` (older local draft). No source file was modified.

## 1. Equation (8) Clipping / Wide PIWM Pipeline Equation

In the latest mirror, the older Equation (8) from `paper/main.tex` is no longer present as a numbered equation. The closest wide displayed formula is the PIWM pipeline in `tmp/overleaf_edit/acl_latex_after.tex:191-196`:

```tex
\begin{align}
    \hat{s}_t &= f_{\theta}(V_t), \\
    \hat{o}_t(a_i) &= h_{\phi}(\hat{s}_t,a_i), \quad a_i\in\mathcal{A}(\hat{s}_t),\\
    a_t^* &= \pi(\{\hat{o}_t(a_i)\}_{a_i\in\mathcal{A}(\hat{s}_t)}).
\end{align}
```

Suggested reflow:

```tex
\begin{align}
    \hat{s}_t &= f_{\theta}(V_t), \\
    \hat{o}_t(a_i) &= h_{\phi}(\hat{s}_t, a_i),
        \quad a_i \in \mathcal{A}(\hat{s}_t), \\
    a_t^* &= \pi\!\left(
        \left\{\hat{o}_t(a_i)\right\}_{a_i \in \mathcal{A}(\hat{s}_t)}
    \right).
\end{align}
```

This keeps the same math but makes the final policy line breakable.

## 2. Table 1 Layout

Current Table 1 source at `tmp/overleaf_edit/acl_latex_after.tex:228-252` uses:

```tex
\begin{tabularx}{\columnwidth}{llX}
...
\end{tabularx}
```

The first two columns can become cramped in ACL two-column layout because candidate rows contain `attention`, `interest`, `desire`, and `action` labels plus multiple `\textsc{...}` entries.

Suggested source adjustment:

```tex
\begin{tabularx}{\columnwidth}{p{0.18\columnwidth}p{0.20\columnwidth}X}
\toprule
Type & Item & Description or values \\
\midrule
...
\bottomrule
\end{tabularx}
```

If this still overflows in Overleaf, wrap only this table with:

```tex
\resizebox{\columnwidth}{!}{%
  \begin{tabular}{lll}
  ...
  \end{tabular}
}
```

Do not delete candidate rows to solve width.

## 3. Lines 226--229 Formula/Subscript Issue

In the latest mirror, `tmp/overleaf_edit/acl_latex_after.tex:226-229` contains prose plus the beginning of Table 1, not a formula:

```tex
Here, $f_{\theta}$ estimates customer state, $h_{\phi}$ predicts action-conditioned outcomes, and $\pi$ selects the candidate with the highest predicted score. ...

\begin{table}[t]
```

The older local draft has a dense inline action-space paragraph at `paper/main.tex:226-229`:

```tex
The action space $\mathcal{A}$ is finite. Each $a \in \mathcal{A}$ is a high-level strategy label ...
The set of \emph{candidate actions} at $t$, denoted $\mathcal{C}_t \subseteq \mathcal{A}$, is filtered by $\sigma_t$...
```

Suggested display rewrite if this paragraph is still present in Overleaf:

```tex
The action space is a finite set $\mathcal{A}$ of high-level strategy labels.
At time $t$, the candidate set is
\[
    \mathcal{C}_t \subseteq \mathcal{A},
    \qquad
    \mathcal{C}_t = F(\sigma_t),
\]
where $F$ is the pedagogy-derived AIDA candidate filter.
```

This avoids dense inline subscripts and improves line breaking.

