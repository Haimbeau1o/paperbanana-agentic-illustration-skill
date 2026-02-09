# PaperBanana Agentic Illustration Skill

> 一个面向“用户做图效率”的多代理技能：把论文方法描述和图注，稳定转换成可迭代、可评分、可交付的学术图示流程。

本项目基于 PaperBanana 的公开论文思路做工程化封装，目标不是替代你的模型，而是提供一套**用户友好、流程清晰、结果可追溯**的做图工作流。

理论基线：
- [PaperBanana 项目页](https://dwzhu-pku.github.io/PaperBanana/)
- [PaperBanana 论文（arXiv:2601.23265）](https://arxiv.org/abs/2601.23265)

---

## 目录

- [1. 这个技能能帮你什么](#1-这个技能能帮你什么)
- [2. 适合谁使用](#2-适合谁使用)
- [3. 两分钟快速开始](#3-两分钟快速开始)
- [4. 完整用户操作指南](#4-完整用户操作指南)
- [5. 两种模式怎么选](#5-两种模式怎么选)
- [6. 输出与交付建议](#6-输出与交付建议)
- [7. 质量检查和验收标准](#7-质量检查和验收标准)
- [8. 常见问题（FAQ）](#8-常见问题faq)
- [9. 后续改进专区（重点）](#9-后续改进专区重点)
- [10. 当前边界与透明说明](#10-当前边界与透明说明)
- [11. 目录结构](#11-目录结构)
- [12. 发布仓库与推送](#12-发布仓库与推送)

---

## 1. 这个技能能帮你什么

你可以把它理解为“做图流程总控器”：

- 把输入（方法段落 + 图注 + 参考候选）规范化
- 用 5 个代理角色分工协作（Retriever / Planner / Stylist / Visualizer / Critic）
- 用固定 JSON 契约保证每一步可检查、可复盘
- 用迭代回路（默认 T=3）持续提升图示质量
- 自动生成评分模板（Faithfulness / Conciseness / Readability / Aesthetics）

一句话：**更少猜模型，多靠流程稳定出图。**

---

## 2. 适合谁使用

- 研究者：想快速把方法描述变成图，不想每次重写长 prompt
- 工程师：想把做图流程嵌入 Agent 系统，有标准输入输出可接
- 团队负责人：想要“可追溯、可审核、可迭代”的图示交付流程

如果你关心“能不能复现这张图为什么这么画出来”，这个技能会很合适。

---

## 3. 两分钟快速开始

### Step 1: 进入 skill 目录

```bash
cd paperbanana-agentic-illustration
```

### Step 2: 准备一个 demo 输入

可直接参考 `references/demo-scenario.md`，保存到：

```text
runs/demo-001/01_input.json
```

### Step 3: 依次执行 5-agent 流程

按顺序执行：

```text
Retriever -> Planner -> Stylist -> Visualizer -> Critic
```

把各阶段结果保存到 `runs/demo-001/`。

### Step 4: 运行校验和评分卡生成

```bash
python3 scripts/validate_agent_io.py \
  --role retriever \
  --input runs/demo-001/01_input.json \
  --output runs/demo-001/02_retriever_output.json

python3 scripts/validate_round_loop.py \
  --log runs/demo-001/05_round_log.json

python3 scripts/build_scorecard_template.py \
  --output-dir runs/demo-001 \
  --case-id demo-001
```

完成后，你会得到可填写的评分卡文件，用于交付前审核。

---

## 4. 完整用户操作指南

下面是推荐的完整操作路径，适合实际项目。

### 4.1 准备输入（必须）

最小输入字段：
- `source_context`
- `communicative_intent`
- `caption`
- `candidate_pool[]`

建议：
- `source_context` 使用你的原始方法段落，不要过度压缩
- `communicative_intent` 一句话说清“图要表达什么”
- `candidate_pool` 推荐 >= 5 条，检索更稳定

### 4.2 执行 Retriever

目标：选出最有帮助的参考样例（Top-K，K<=10）

输出关键字段：
- `top_refs[]`
- `selection_rationale`
- `retrieval_confidence`

### 4.3 执行 Planner

目标：把方法信息翻译成完整图示说明

输出关键字段：
- `initial_description`
- `assumption_block`（有歧义时）

### 4.4 执行 Stylist

目标：只优化视觉表达，不改语义事实

输出关键字段：
- `optimized_description`
- `style_actions[]`

### 4.5 执行 Visualizer

目标：根据模式产出图像或绘图代码

输出关键字段：
- `artifact.type` (`image_path` / `image_prompt` / `code_text`)
- `artifact.value`

### 4.6 执行 Critic + 迭代回路

默认轮次：`T=3`

每轮流程：
1. Visualizer 产出 `artifact_t`
2. Critic 产出 `critic_suggestions` 和 `revised_description`
3. 下一轮使用 `description_{t+1} = revised_description`

可以提前结束，但要满足：
- `stop_flag=true`
- 日志写明 `terminated_early=true`
- 给出 `termination_reason`

### 4.7 生成评分卡并交付

生成后填写四维质量评估：
- Faithfulness（事实一致）
- Conciseness（信息精炼）
- Readability（可读性）
- Aesthetics（审美）

建议和以下文件一起交付：
- `01_input.json`
- `05_round_log.json`
- `*-scorecard.json`
- `*-scorecard.md`
- 最终图像或代码产物

---

## 5. 两种模式怎么选

| 模式 | 适用场景 | 优先目标 |
| --- | --- | --- |
| `diagram_image` | 方法框架图、系统流程图、概念图 | 视觉表达和结构清晰 |
| `plot_code` | 统计图、对数值精度要求高的图 | 数值一致性和可复现 |

简单判断：
- 你更在意“图示表达” -> `diagram_image`
- 你更在意“数值准确” -> `plot_code`

---

## 6. 输出与交付建议

建议你按 case 建目录归档：

```text
runs/<case-id>/
├── 01_input.json
├── 02_retriever_output.json
├── 03_planner_output.json
├── 04_stylist_output.json
├── 05_round_log.json
├── <case-id>-scorecard.json
└── <case-id>-scorecard.md
```

这样做的好处：
- 可复盘（知道每一步怎么来的）
- 可评审（团队可以看关键决策链）
- 可迭代（下次从同类 case 快速迁移）

---

## 7. 质量检查和验收标准

最低验收（建议作为 v0.1 合格线）：

- [ ] `SKILL.md` 校验通过
- [ ] `agents/openai.yaml` 可解析
- [ ] `validate_agent_io.py` 通过
- [ ] `validate_round_loop.py` 通过
- [ ] 评分卡模板可生成并可填写

进阶验收（建议团队实践）：

- [ ] 至少 1 个完整 demo 跑通
- [ ] 至少 1 个提前终止 case 跑通
- [ ] 至少 1 个失败回滚 case 有记录

---

## 8. 常见问题（FAQ）

### Q1. 为什么一定要走 Critic？
因为“看起来好看”不等于“事实正确”。Critic 是防止事实偏移的关键环节。

### Q2. 为什么强调 JSON 契约？
因为可验证、可自动检查、可重复运行。自由文本不利于工程协作。

### Q3. 出图不稳定怎么办？
建议按优先级优化：
1. Planner 描述更细
2. Stylist 约束更严格
3. Critic 提示更可执行
4. 必要时切换 `plot_code`

### Q4. 某些平台不识别 `agents/openai.yaml` 怎么办？
不影响主流程。`SKILL.md` 才是行为规范核心。

---

## 9. 后续改进专区（重点）

这是给用户看的“未来承诺区”，告诉你我们会如何持续改进。

### 9.1 为什么需要迭代

目前 PaperBanana 官方代码尚未完整开源。我们现在做的是：
- 先把可用工作流做稳
- 再随着官方实现公开，逐步对齐字段、提示词和回路细节

### 9.2 已完成（当前版本）

- 5-agent 协作协议
- 双模式路由（diagram_image / plot_code）
- 迭代回路校验脚本
- 四维评分模板
- 用户向 README（本文件）

### 9.3 下一阶段（官方代码开放后）

**计划升级点：**
1. 对齐官方 agent I/O schema
2. 对齐官方提示词结构
3. 增加官方 profile 的脚本校验
4. 补充更多真实案例模板

### 9.4 对用户的承诺

我们会保持这三点：
- **兼容优先**：尽量不破坏你已有 case 结构
- **文档同步**：每次升级都更新 README 和 references
- **可迁移**：保留 provider-agnostic 的角色映射，避免锁死单一模型

### 9.5 你可以如何参与改进

如果你是用户/团队维护者，欢迎提供：
- 失败 case（最好含 round log）
- 想要新增的场景模板
- 你们希望接入的模型配置

这些反馈会直接影响下一版优先级。

---

## 10. 当前边界与透明说明

为了避免误解，这里明确说明当前不覆盖内容：
- 不内置具体图像 API 的调用代码
- 不包含私有模型凭据管理
- 不宣称与未开源官方代码“完全一致”

当前定位是：**稳定可用的技能工作流层**。

---

## 11. 目录结构

```text
paperbanana-agentic-illustration/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── paperbanana-theory-mapping.md
│   ├── agent-contracts.md
│   ├── prompt-templates-zh-en.md
│   ├── model-adapter-map.md
│   ├── install-and-compat.md
│   └── demo-scenario.md
└── scripts/
    ├── validate_agent_io.py
    ├── validate_round_loop.py
    └── build_scorecard_template.py
```

---

## 12. 发布仓库与推送

当前推荐仓库：
- 名称：`paperbanana-agentic-illustration-skill`
- 可见性：`private`（可后续改 public）

```bash
cd paperbanana-agentic-illustration

gh auth login
gh repo create paperbanana-agentic-illustration-skill \
  --private \
  --source=. \
  --remote=origin \
  --push
```

验证：

```bash
git remote -v
gh repo view --web
```

---

如果你希望，我下一步可以直接再补：
- `CHANGELOG.md`（版本演进日志）
- `CONTRIBUTING.md`（团队协作规范）
- `examples/`（可复制粘贴的完整样例）
