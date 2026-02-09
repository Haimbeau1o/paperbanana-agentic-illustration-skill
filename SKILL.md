---
name: paperbanana-agentic-illustration
description: Use when Codex needs to run PaperBanana-style multi-agent academic illustration workflows from method context and figure caption, especially for reference retrieval, planning, style refinement, visualization, iterative critic loops, and scorecard evaluation across faithfulness, conciseness, readability, and aesthetics.
---

# PaperBanana Agentic Illustration

## Overview

Use this skill to execute a PaperBanana-style five-agent workflow for academic diagrams and statistical plots.

本技能用于将“方法文本 + 图注”转换为可审查、可迭代、可评分的多代理图示生成流程。

Core principle / 核心原则:
- Separate reasoning from rendering.
- Keep every stage contract-first with JSON outputs.
- Improve quality through iterative critique, not prompt guesswork.

## Workflow Decision

Choose one mode before running agents:

| Mode | Use When | Visualizer Output |
| --- | --- | --- |
| `diagram_image` | You need methodology diagram or conceptual figure generation | Image artifact prompt/result |
| `plot_code` | You need numerically faithful statistical plots | Executable plotting code artifact |

Routing rule / 路由规则:
- If numerical precision is primary, prefer `plot_code`.
- If visual narrative is primary, prefer `diagram_image`.

## Required Inputs

Minimum required fields:
- `source_context`: core method text or structured notes
- `communicative_intent`: what the figure should communicate
- `caption`: target figure caption
- `candidate_pool`: reference candidates for Retriever

See detailed contracts in `references/agent-contracts.md`.

## Five-Agent Execution Protocol

Run agents in this strict order:
1. Retriever -> select top references
2. Planner -> produce `initial_description`
3. Stylist -> produce `optimized_description`
4. Visualizer -> produce round artifact (`diagram_image` or `plot_code`)
5. Critic -> produce targeted revision and `stop_flag`

Do not skip Planner or Critic. If either fails, stop and repair inputs.

## Iterative Refinement Loop

Default rounds: `T=3`

Loop structure:
1. Start with `description_0 = optimized_description`
2. For round `t`:
   - Visualizer generates `artifact_t`
   - Critic returns `critic_suggestions`, `revised_description`, `stop_flag`
   - Set `description_{t+1} = revised_description`
3. Exit when:
   - `t == T-1`, or
   - `stop_flag == true` and quality threshold is met

Quality threshold suggestion:
- No critical factual mismatch
- No major layout readability defect
- No unresolved caption conflict

## Failure Handling

### Candidate pool too small (<5)
- Continue with available references.
- Mark risk: `retrieval_confidence = low`.
- Force Planner to include explicit uncertainty notes.

### Caption ambiguous or conflicting
- Planner must output a short `assumption_block` before diagram description.
- Critic checks whether assumptions violate source context.

### Critic gives no effective suggestions for 2 rounds
- Trigger early-stop recommendation.
- Produce `manual_review_required = true` with unresolved issues list.

### Visualizer unavailable
- `diagram_image` unavailable -> fallback to `plot_code` or structured textual storyboard.
- `plot_code` unavailable -> fallback to pseudo-code plus chart specification table.

## Quick Commands

Run from skill root:

```bash
python3 scripts/validate_agent_io.py --role retriever --input /path/in.json --output /path/out.json
python3 scripts/validate_round_loop.py --log /path/round-log.json
python3 scripts/build_scorecard_template.py --output-dir /tmp/paperbanana-scorecard --case-id demo-001
```

## Expected Outputs

The workflow should always produce:
- Agent outputs that pass schema checks
- Round log with valid continuity
- Scorecard template for evaluation dimensions:
  - Faithfulness
  - Conciseness
  - Readability
  - Aesthetics

## Common Mistakes

- Using free-form prose instead of JSON contracts
- Letting Stylist alter semantic content
- Ending loop without checking `stop_flag` legality
- Mixing caption text into image body requirements
- Treating aesthetics gains as a substitute for factual fidelity

## Red Flags (Stop and Fix)

- Retriever outputs more than 10 references
- Critic output misses `revised_description`
- Round index skips (`0, 1, 3`)
- `terminated_early = true` while last `stop_flag = false`
- Scorecard generated without source context reference

## Supporting References

- `references/paperbanana-theory-mapping.md`
- `references/agent-contracts.md`
- `references/prompt-templates-zh-en.md`
- `references/model-adapter-map.md`
- `references/install-and-compat.md`
- `references/demo-scenario.md`
