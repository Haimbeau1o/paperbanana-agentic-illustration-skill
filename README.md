# PaperBanana Agentic Illustration Skill

> 基于 PaperBanana 多代理思想的用户友好型做图技能（Codex 规范优先，兼容多 Agent 工作流）

本技能的目标很明确：**让用户更方便、更稳定地把“论文方法描述 + 图注”转成高质量学术图示**，并且通过可审计的多代理流程提高可控性。

参考来源（理论基线）：
- PaperBanana 项目页：<https://dwzhu-pku.github.io/PaperBanana/>
- PaperBanana 论文（arXiv）：<https://arxiv.org/abs/2601.23265>

---

## 目录

- [0. 五分钟快速上手](#0-五分钟快速上手)
- [1. 项目定位](#1-项目定位)
- [2. 与 PaperBanana 的关系与当前边界](#2-与-paperbanana-的关系与当前边界)
- [3. 你能用它做什么](#3-你能用它做什么)
- [4. 目录结构](#4-目录结构)
- [5. 安装与接入](#5-安装与接入)
- [6. 用户操作手册（详细）](#6-用户操作手册详细)
- [7. 质量控制与验收](#7-质量控制与验收)
- [8. 压力场景处理](#8-压力场景处理)
- [9. 常见问题与排障](#9-常见问题与排障)
- [10. 迭代路线图（重点）](#10-迭代路线图重点)
- [11. 开源后升级实施清单](#11-开源后升级实施清单)
- [12. 发布新仓库建议流程](#12-发布新仓库建议流程)

---

## 0. 五分钟快速上手

如果你想先确认“能不能跑通”，直接按下面做：

1. 在当前目录创建 `runs/demo-001/`，并准备 `01_input.json`。
2. 按 `Retriever -> Planner -> Stylist -> Visualizer -> Critic` 顺序执行一次。
3. 保存轮次日志为 `05_round_log.json`。
4. 执行以下三个命令校验与产出评分卡：

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

5. 打开 `demo-001-scorecard.md` 完成四维人工审查并归档。

---

## 1. 项目定位

`paperbanana-agentic-illustration` 是一个 skill（不是图像引擎本体），用于把多代理生成流程标准化。

它提供：
- 一套可执行的 **5-Agent 协作协议**（Retriever / Planner / Stylist / Visualizer / Critic）
- 标准化 JSON 输入输出契约（便于脚本校验、便于追踪）
- 迭代回路与提前终止规则（默认 T=3）
- 四维质量评分模板（Faithfulness / Conciseness / Readability / Aesthetics）

它不提供：
- 私有模型 API key 管理
- 端到端图像生成服务
- PaperBanana 官方未公开代码中的内部实现细节

---

## 2. 与 PaperBanana 的关系与当前边界

### 2.1 我们的定位

本项目是 **PaperBanana 思想的工程化工作流复现与实用化封装**，重点是让用户“可操作、可验证、可迭代”地做图。

### 2.2 当前边界（非常重要）

由于 PaperBanana 官方代码尚未完整开源，本技能当前属于：
- **概念对齐**：对齐论文公开方法范式
- **契约先行**：先把代理接口、流程和质检固化
- **实现可迁移**：后续可无缝映射到官方代码结构

换句话说：
- 现在是 **可用的 workflow skill**
- 未来可升级为 **与官方实现强一致的 workflow+runtime 适配层**

---

## 3. 你能用它做什么

适用任务：
1. 方法图自动化生成（`diagram_image`）
2. 统计图代码生成（`plot_code`）
3. 图示迭代修订（Critic 闭环）
4. 输出质量评分和交付前审查

适用人群：
- 研究者：希望快速从方法段落生成图示
- 工程师：希望把做图流程接进 Agent 系统
- 团队负责人：希望有可审计、可复盘的流程

---

## 4. 目录结构

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

## 5. 安装与接入

### 5.1 Codex 全局安装

```bash
mkdir -p ~/.codex/skills
cp -R paperbanana-agentic-illustration ~/.codex/skills/
```

### 5.2 antigravity 项目级安装

```bash
mkdir -p .agent/skills
cp -R paperbanana-agentic-illustration .agent/skills/
```

### 5.3 antigravity 全局安装

```bash
mkdir -p ~/.gemini/antigravity/skills
cp -R paperbanana-agentic-illustration ~/.gemini/antigravity/skills/
```

> 说明：不同版本的宿主加载路径可能有差异。若未自动识别，请仅调整安装路径，不要破坏 skill 内部结构。

---

## 6. 用户操作手册（详细）

下面给出一套从 0 到 1 的完整用户操作流程。**你不需要一次性自动化，手动执行也能稳定跑通。**

### 6.1 推荐运行工作目录

为每次任务创建独立 run：

```text
runs/<case-id>/
├── 01_input.json
├── 02_retriever_output.json
├── 03_planner_output.json
├── 04_stylist_output.json
├── 05_round_log.json
├── 06_scorecard.json
└── 06_scorecard.md
```

### 6.2 第一步：准备输入

创建 `01_input.json`（最小输入）：

```json
{
  "source_context": "Your method section text or structured notes.",
  "communicative_intent": "What the figure should communicate.",
  "caption": "Target figure caption.",
  "candidate_pool": [
    {
      "id": "ref_001",
      "summary": "Reference summary",
      "domain": "forecasting",
      "diagram_type": "framework"
    }
  ]
}
```

建议：
- `source_context` 尽量保留原术语
- `communicative_intent` 用一句话说清“图要表达什么”
- `candidate_pool` 至少 5 条更稳（少于 5 条要走降级策略）

### 6.3 第二步：选择模式

- 做方法框架图：`diagram_image`
- 做数值精确统计图：`plot_code`

你可以在 run 的配置里显式记录：

```json
{"mode": "diagram_image", "max_rounds": 3}
```

### 6.4 第三步：执行 Retriever

1. 打开 `references/prompt-templates-zh-en.md`
2. 使用 `Retriever Agent` 模板作为系统提示
3. 喂入 `01_input.json` 的字段
4. 保存输出到 `02_retriever_output.json`

然后校验：

```bash
python3 scripts/validate_agent_io.py \
  --role retriever \
  --input runs/<case-id>/01_input.json \
  --output runs/<case-id>/02_retriever_output.json
```

### 6.5 第四步：执行 Planner

输入包含：
- `source_context`
- `communicative_intent`
- `caption`
- `retrieved_examples`（由 retriever 输出映射）

输出保存到：`03_planner_output.json`

关键检查：
- `initial_description` 是否覆盖核心模块、连接关系、信息流
- 如有歧义是否有 `assumption_block`

### 6.6 第五步：执行 Stylist

输入：
- `initial_description`
- `style_guidelines`
- `source_context`
- `caption`

输出保存到：`04_stylist_output.json`

关键原则：
- **Stylist 只能优化风格，不得改语义事实**

### 6.7 第六步：执行 Visualizer + Critic 回路（T=3）

初始化：
- `description_0 = optimized_description`

每轮：
1. Visualizer 产出 `artifact_t`
2. Critic 产出 `critic_suggestions`, `revised_description`, `stop_flag`
3. 下一轮 `description_{t+1} = revised_description`

将全流程写入 `05_round_log.json`，再运行：

```bash
python3 scripts/validate_round_loop.py \
  --log runs/<case-id>/05_round_log.json
```

提前终止条件：
- `stop_flag=true`
- 并满足质量阈值
- 且在日志里写明 `terminated_early=true` 和 `termination_reason`

### 6.8 第七步：生成评分模板并填写

```bash
python3 scripts/build_scorecard_template.py \
  --output-dir runs/<case-id> \
  --case-id <case-id>
```

会生成：
- `<case-id>-scorecard.json`
- `<case-id>-scorecard.md`

按四维打分并记录证据：
- Faithfulness（事实一致）
- Conciseness（信息精炼）
- Readability（可读性）
- Aesthetics（审美）

### 6.9 第八步：交付建议

建议打包以下文件给团队或审稿协作方：
- `01_input.json`
- `05_round_log.json`
- `06_scorecard.{json,md}`
- 最终图像或代码 artifact

这能保证“结果可追溯、问题可复盘”。

---

## 7. 质量控制与验收

最低验收（v0.1）标准：
- [ ] `SKILL.md` 结构合法
- [ ] `agents/openai.yaml` 可解析
- [ ] 各阶段输出能通过 I/O 校验
- [ ] 迭代日志能通过回路校验
- [ ] 评分模板可生成且可填写

建议加分项：
- [ ] 至少 1 个 demo case 完整跑通
- [ ] 至少 1 个提前终止 case
- [ ] 至少 1 个失败回滚 case

---

## 8. 压力场景处理

### 场景 A：候选参考不足（<5）

处理：
- 继续执行
- 在 retriever 输出中标记 `retrieval_confidence=low`
- 要求 planner 显式写假设和不确定项

### 场景 B：caption 模糊或冲突

处理：
- planner 必须输出 `assumption_block`
- critic 必须逐条核对 assumptions 与 source_context 是否冲突

### 场景 C：critic 连续两轮无有效建议

处理：
- 允许提前终止
- 在 scorecard 标注 `manual_review_required=true`
- 输出人工复核建议清单

---

## 9. 常见问题与排障

### Q1: 为什么已经“看起来很好”还要走 Critic？
A: 因为学术图最怕“看起来对但事实错”。Critic 是事实对齐的最后保险。

### Q2: 为什么要求 JSON 而不是自由文本？
A: JSON 让流程可验证、可重放、可自动检查；自由文本难以规模化质量管理。

### Q3: Visualizer 生成效果不稳定怎么办？
A:
1. 增强 planner 描述颗粒度
2. 缩短 stylist 的自由度
3. 提高 critic 的“可执行修改”比例
4. 必要时切到 `plot_code` 分支

### Q4: 如果宿主不识别 `openai.yaml` 怎么办？
A: 不影响主流程；`SKILL.md` 是行为规范核心。

---

## 10. 迭代路线图（重点）

> 由于 PaperBanana 官方代码尚未完整开源，当前版本为“概念对齐 + 工程契约”阶段。下面给出明确迭代策略。

### v0.1（当前）

- 已交付：
  - 5-agent 协议
  - 双模式路由
  - 迭代回路校验
  - 评分模板

### v0.2（官方代码开放后第一阶段）

- 目标：与官方实现字段、提示词、回路策略对齐
- 动作：
  1. 对比官方 agent 输入输出
  2. 更新 `references/agent-contracts.md`
  3. 更新 `references/prompt-templates-zh-en.md`
  4. 为脚本补官方字段兼容分支

### v0.3（可运行增强）

- 目标：接入可配置执行器（非绑定单一厂商）
- 动作：
  1. 新增 runner（可选）
  2. 新增 provider 适配层配置
  3. 输出统一日志与成本统计

### v1.0（稳定版）

- 条件：
  - 与官方公开流程基本一致
  - 至少 20 个真实案例回归通过
  - 文档、脚本、示例全部闭环

---

## 11. 开源后升级实施清单

当 PaperBanana 官方代码发布后，请按以下顺序升级：

1. **接口对齐**
   - 比较官方字段与本 skill 契约
   - 标记 `新增字段/废弃字段/语义变化`

2. **提示词对齐**
   - 逐 Agent 对齐系统提示
   - 标记“必须同步”和“可选增强”

3. **流程对齐**
   - 检查回路轮数、提前终止规则
   - 检查评分维度和聚合策略

4. **脚本升级**
   - `validate_agent_io.py` 增加官方 schema profile
   - `validate_round_loop.py` 增加官方终止策略 profile

5. **回归测试**
   - 至少 10 个官方样例
   - 至少 10 个你们业务样例

6. **版本发布**
   - 升级次版本号（例如 `0.1.x -> 0.2.0`）
   - 发布变更说明（含不兼容项）

---

## 12. 发布新仓库建议流程

当前目录已经是独立 Git 仓库，可以直接创建远程并推送。

推荐默认：
- 仓库名：`paperbanana-agentic-illustration-skill`
- 可见性：`private`（后续可切公开）

```bash
# 1) 进入仓库目录
cd paperbanana-agentic-illustration

# 2) 检查本地状态
git status

# 3) GitHub CLI 登录（若尚未登录或 token 失效）
gh auth login

# 4) 创建远程仓库并推送
gh repo create paperbanana-agentic-illustration-skill \
  --private \
  --source=. \
  --remote=origin \
  --push

# 5) 验证远程
git remote -v
gh repo view --web
```

如果你要公开发布，把 `--private` 改成 `--public` 即可。

发布前建议自检：
- [ ] README 与 SKILL.md 一致
- [ ] 所有脚本可运行
- [ ] demo 场景可复现
- [ ] 迭代路线清晰可执行
- [ ] `references/install-and-compat.md` 与实际安装路径一致
