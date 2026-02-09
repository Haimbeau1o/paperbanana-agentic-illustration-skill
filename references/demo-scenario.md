# Demo Scenario and Acceptance Checklist

Use this file to verify "callable + demo-ready" v0.1 quality.

## Demo Input

```json
{
  "source_context": "We propose a dual-stream forecasting model with temporal branch, variable branch, and cross-branch distillation.",
  "communicative_intent": "Show data flow, distillation direction, and final prediction head clearly.",
  "caption": "Overall architecture of the dual-stream forecasting framework.",
  "candidate_pool": [
    {"id": "ref_001", "summary": "Two-stage pipeline with feedback loop", "domain": "forecasting", "diagram_type": "framework"},
    {"id": "ref_002", "summary": "Teacher-student training diagram", "domain": "representation learning", "diagram_type": "architecture"},
    {"id": "ref_003", "summary": "Ablation result layout", "domain": "evaluation", "diagram_type": "chart"}
  ]
}
```

## Expected Stage Outputs

- Retriever: `top_refs` (<=10), rationale present
- Planner: complete `initial_description` with module relations
- Stylist: `optimized_description` preserving planner semantics
- Visualizer: one valid `artifact`
- Critic: `critic_suggestions` and `revised_description`

## Minimal Round Log Expectation

- At least one round exists
- Round index starts at 0
- Each round has `description_t -> artifact -> critique.revised_description`

## Scorecard Expectation

Scorecard template exists for:
- Faithfulness
- Conciseness
- Readability
- Aesthetics

## Pressure Scenarios

### Scenario 1: Reference scarcity (<5)
- Expected: mark low retrieval confidence and continue with explicit risk note.

### Scenario 2: Caption ambiguity/conflict
- Expected: Planner emits `assumption_block`; Critic validates assumption against source context.

### Scenario 3: Two consecutive non-actionable critic rounds
- Expected: early-stop recommendation and `manual_review_required=true` in report.

## Pass/Fail Checklist

- [ ] `SKILL.md` passes quick validation
- [ ] `agents/openai.yaml` is parseable
- [ ] `validate_agent_io.py` catches malformed payloads
- [ ] `validate_round_loop.py` catches illegal early-stop logic
- [ ] `build_scorecard_template.py` outputs markdown and json templates
