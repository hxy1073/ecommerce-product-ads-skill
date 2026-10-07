# ecommerce-product-ads-skill

一个简化、可复用的 Codex Skill：只需 `text.pdf`、`product.png`、`logo.svg`，即可完成任务解析、视觉策略、ImageGen 主视觉、自动检查、A/B/C 人工确认和 PNG 导出。

## 只需准备三个文件

把文件放到项目根目录的 `input/`：

```text
input/
├── text.pdf
├── product.png
└── logo.svg
```

文件名固定。`text.pdf` 是事实与设计任务来源；`product.png` 和 `logo.svg` 是受保护资产。

## 启动

在 Codex 中打开本项目并输入：

```text
使用 $ecommerce-product-ads-skill 处理当前项目，从 Stage 0 开始。
```

无需 API key。Skill 使用当前 Codex 会话的内置 ImageGen；Python 只做文件、YAML/JSON 和图片尺寸验证。

## 完整流程

1. **Stage 0 任务解析**：读取三项输入，从模板生成 `work/brief.yaml`、`work/layout.json`、`work/state.yaml`、`work/visual_strategy.yaml`。PDF 未提供的事实写为 `null`。
2. **Stage 1 视觉策略与布局**：确定一个清晰的营销概念、商品主视觉位置、价格/标题层级和 feature callout 方式。
3. **Stage 2 ImageGen 完整生成**：使用内置 ImageGen 生成完整商业主视觉，不默认使用简单 SVG/CairoSVG 拼海报。
4. **Stage 3 自动检查**：检查商品、Logo、文案、层级、版式、画布尺寸与品牌调性。
5. **Stage 4 人工确认**：只提供 A 接受并导出、B 重新生成、C 使用原始商品/Logo 修复。
6. **Stage 5 导出**：输出到 `output/hero_<lang>.png`，QA 报告位于 `output/qa_report.md`。

## A/B/C 的含义

- **A. 接受并导出**：当前版本进入 `output/`。
- **B. 重新生成**：依据 QA 问题重新调用 ImageGen，并保留旧版本。
- **C. 商品或 Logo 失真**：保留 ImageGen 的创意画面，用原始 `product.png` / `logo.svg` 修复受保护资产，再次检查。

## 目录

```text
SKILL.md
README.md
agents/openai.yaml
input/
templates/
work/
output/
references/
scripts/
examples/nori/
```

`references/` 当前只含使用说明，后续可按商品品类加入参考海报。参考图只影响构图、层级、光色和视觉节奏，不能成为商品事实或品牌资产来源。

## 验证命令

```powershell
python -m pip install -r requirements.txt
python scripts/validate.py --project . --stage input
python scripts/validate.py --project . --stage work
python scripts/validate.py --project examples/nori --stage input
python scripts/validate.py --project examples/nori --stage work
```

完成主视觉后：

```powershell
python scripts/validate.py --project . --stage output
```

## Nori 示例

`examples/nori/` 包含完整三项输入和已完成的 Stage 0/1 文件。它用于验证解析结构与流程；不会预先放入最终主视觉，以免把某一种设计当成所有商品的固定模板。

