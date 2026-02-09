# PaperBanana Theory Mapping

This note maps the original PaperBanana conceptual pipeline to a reusable skill workflow.

## 1) Five-Agent Mapping

| PaperBanana role | Skill role | Primary responsibility |
| --- | --- | --- |
| Retriever | Retriever | Select structurally relevant references from candidate pool |
| Planner | Planner | Translate source context and caption into a complete diagram/plot description |
| Stylist | Stylist | Refine presentation style while preserving semantics |
| Visualizer | Visualizer | Render image or generate plot code from current description |
| Critic | Critic | Compare artifact with source intent and provide actionable revision |

## 2) Loop Mapping

Conceptual loop in this skill:
- `description_0 = optimized_description`
- `artifact_t = Visualizer(description_t)`
- `revision_t = Critic(artifact_t, source_context, caption, description_t)`
- `description_{t+1} = revision_t.revised_description`
- Stop when `t == T-1` (default `T=3`) or `revision_t.stop_flag == true` with quality threshold met.

## 3) Diagram vs Plot Modes

- `diagram_image` mode: Visualizer emits image artifact prompt/result.
- `plot_code` mode: Visualizer emits executable plotting code for higher numeric fidelity.

## 4) Evaluation Dimensions

Use the same four dimensions in scorecard review:
1. Faithfulness
2. Conciseness
3. Readability
4. Aesthetics

Suggested interpretation:
- Faithfulness and Readability are primary guards.
- Conciseness and Aesthetics are quality multipliers.

## 5) Practical Skill-Level Constraints

Because this skill is provider-agnostic and does not ship a rendering engine:
- Keep all stage outputs machine-parseable JSON.
- Treat model binding as configuration, not hardcoded logic.
- Preserve explicit fallback behavior for missing model capabilities.

## 6) Why This Mapping Works

The mapping preserves the most reusable PaperBanana properties:
- multi-agent decomposition
- retrieval-augmented planning
- iterative self-critique
- explicit quality rubric

This keeps the skill useful across Codex, antigravity-style environments, and general agent stacks.
