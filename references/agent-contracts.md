# Agent Contracts (JSON)

Use these contracts as the canonical interface between stages.

## Shared Conventions

- All payloads are UTF-8 JSON objects.
- Unknown fields are allowed but must not replace required fields.
- `source_context` and `caption` must be preserved unchanged across rounds.

## Retriever

### Input

```json
{
  "source_context": "string",
  "communicative_intent": "string",
  "caption": "string",
  "candidate_pool": [
    {
      "id": "ref_001",
      "summary": "string",
      "domain": "string",
      "diagram_type": "string"
    }
  ]
}
```

### Output

```json
{
  "top_refs": ["ref_001", "ref_014"],
  "selection_rationale": "string",
  "retrieval_confidence": "high"
}
```

Constraints:
- `top_refs` length: `1..10`
- each id must exist in `candidate_pool`

## Planner

### Input

```json
{
  "source_context": "string",
  "communicative_intent": "string",
  "caption": "string",
  "retrieved_examples": [
    {
      "id": "ref_001",
      "summary": "string"
    }
  ]
}
```

### Output

```json
{
  "initial_description": "string",
  "assumption_block": "optional string"
}
```

## Stylist

### Input

```json
{
  "initial_description": "string",
  "style_guidelines": "string",
  "source_context": "string",
  "caption": "string"
}
```

### Output

```json
{
  "optimized_description": "string",
  "style_actions": ["color harmonization", "layout cleanup"]
}
```

Constraint:
- `optimized_description` must preserve semantic entities from `initial_description`

## Visualizer

### Input

```json
{
  "description_t": "string",
  "mode": "diagram_image",
  "round": 0
}
```

or

```json
{
  "description_t": "string",
  "mode": "plot_code",
  "round": 0
}
```

### Output

```json
{
  "artifact": {
    "type": "image_path",
    "value": "/tmp/output.png"
  }
}
```

or

```json
{
  "artifact": {
    "type": "code_text",
    "value": "import matplotlib.pyplot as plt\\n..."
  }
}
```

## Critic

### Input

```json
{
  "artifact": {
    "type": "image_path",
    "value": "/tmp/output.png"
  },
  "description_t": "string",
  "source_context": "string",
  "caption": "string",
  "round": 0
}
```

### Output

```json
{
  "critic_suggestions": "string",
  "revised_description": "string",
  "stop_flag": false,
  "quality_gate": {
    "faithfulness_ok": true,
    "readability_ok": true
  }
}
```

## Round Log Contract

Use this for loop validation script:

```json
{
  "max_rounds": 3,
  "mode": "diagram_image",
  "terminated_early": false,
  "termination_reason": "",
  "rounds": [
    {
      "round": 0,
      "description_t": "string",
      "artifact": {"type": "image_path", "value": "/tmp/r0.png"},
      "critique": {
        "critic_suggestions": "string",
        "revised_description": "string",
        "stop_flag": false
      }
    }
  ]
}
```
