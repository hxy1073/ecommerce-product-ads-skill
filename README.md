# ecommerce-product-ads-skill V2.1

这是一个全局可复用 Skill。新建任意任务文件夹，只需放入：

```text
text.pdf
product.png
logo.svg
```

然后在该目录调用：

```text
使用 $ecommerce-product-ads-skill 处理当前任务，从 Stage 0 开始。
```

Skill 会保留根目录源文件，并自动创建：

```text
input/
├── text.pdf
├── product.png
└── logo.svg
work/
output/
```

也支持用户预先建立完整的 `input/`。`text.pdf` 是事实与锁定文案来源；商品图和 Logo 是受保护资产。PDF 未提供的信息保持 `null`。

## 工作区与 Skill 资源

- 任务目录只保存 `input/`、`work/`、`output/` 及用户原始输入。
- 已安装 Skill 保存 `templates/`、`references/patterns/`、`scripts/`、说明和示例。
- 模板、Pattern 和验证器从已安装 Skill 读取；所有任务产物只写入当前任务目录。
- 已有 `work/state.yaml` 时按状态继续；Stage 6 已完成时保留结果，不自动重启或覆盖。
- 输入不完整时列出缺失文件并停止。

无需为每个任务复制整个仓库，也无需 API key。正常流程使用 Codex 内置 ImageGen；Python 只做工作区初始化和确定性校验。

## 开发仓库模式

本仓库仍可直接作为开发项目使用，保留自身的 `input/`、`templates/`、`references/`、`scripts/`、`work/`、`output/` 和 `examples/nori/`。开发验证命令保持不变。

## V2 流程

```text
Stage 0  需求解析 + 商品视觉分析
   ↓
Stage 1  生成 3 个 Concept
   ↓
Checkpoint A  选择 A / B / C / AUTO
   ↓
Stage 2  Art Direction + 宽松 Layout
   ↓
Stage 3  ImageGen 完整主视觉
   ↓
Stage 4  自动 + 视觉 QA
   ↓
Stage 5  接受 / 迭代 / 原始资产恢复
   ↓
Stage 6  导出正式 PNG
```

Checkpoint A 的 A/B/C 是三个营销概念；Stage 5 的 A/B/C 是最终结果处理：

- A：接受当前结果并进入导出。
- B：按问题层级回到 Concept、Art Direction 或 ImageGen。
- C：保留设计，用原始商品图和/或 Logo 恢复失真资产。

AUTO 会依据营销目标、目标用户、品牌调性、可用产品事实和商品视觉特征选择综合匹配度最高的 Concept，不按“最好看”主观选择。

## Design Pattern

`references/patterns/` 包含 6 个轻量设计知识 Pattern，用于启发 Concept 与 Art Direction。它们不是固定模板、商品事实或 ImageGen Prompt。一个 Concept 最多使用 1 个 primary Pattern 和 2 个 secondary Pattern。

## 关键工作文件

- `work/brief.yaml`：需求、事实、锁定文案与商品视觉分析。
- `work/concepts.yaml`：三个轻量 Concept、推荐与选择结果。
- `work/visual_strategy.yaml`：选中 Concept 的 Art Direction。
- `work/layout.json`：信息层级与宽松空间关系。
- `work/state.yaml`：Stage 0～6 的简单状态记录。
- `work/qa_report.md`：设计 QA。
- `output/hero_<lang>.png`：正式交付。

## 验证

```powershell
python -m pip install -r requirements.txt
python scripts/validate.py --project . --stage input
python scripts/validate.py --project . --stage work
python scripts/validate.py --project examples/nori --stage input
python scripts/validate.py --project examples/nori --stage work
python scripts/validate.py --project . --stage output
```

`examples/nori/` 展示了需求分析、三个明显不同的 Concept、AUTO 选择和选定方案的 Art Direction；其中的秋季、通勤、绿色和保温杯内容只属于该示例。
