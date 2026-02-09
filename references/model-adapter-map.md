# Model Adapter Map

This skill is provider-agnostic. Bind concrete models by role.

## Role Keys

- `vlm_reasoner`: Retriever, Planner, Stylist, Critic, Judge
- `img_generator`: Visualizer in `diagram_image` mode
- `code_generator`: Visualizer in `plot_code` mode

## Default Capability Targets

- `vlm_reasoner`: Gemini-Pro-class reasoning and multimodal understanding
- `img_generator`: Nano-Banana-class image generation
- `code_generator`: high-quality code LLM with plotting reliability

## Example Mapping (Config-Level)

```yaml
model_adapter:
  vlm_reasoner:
    primary: google/gemini-3-pro-preview
    fallbacks:
      - openai/gpt-5.2
      - anthropic/claude-opus-4-5
  img_generator:
    primary: google/nano-banana-pro
    fallbacks:
      - openai/gpt-image-1.5
  code_generator:
    primary: openai/gpt-5.2
    fallbacks:
      - google/gemini-3-pro-preview
```

## Fallback Policy

1. `img_generator` unavailable:
   - switch to `plot_code`, or
   - output storyboard spec (structured textual artifact)
2. `vlm_reasoner` context overflow:
   - compress candidate pool
   - require Planner to emit concise module table before full description
3. `code_generator` weak plotting output:
   - enforce critic loop with numeric checks
   - include explicit axis/value validation in critic prompt

## Guardrails

- Never hardcode provider-specific APIs inside this skill.
- Keep role names stable; swap only model bindings.
- Log selected provider/model per stage for auditability.
