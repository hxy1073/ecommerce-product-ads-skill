# ecommerce-product-ads-skill V2.3

这是一个全局可复用的电商商品 Key Visual Skill。新建任意任务文件夹，只需放入：

```text
text.pdf
product.png
logo.svg
```

然后在该目录调用：

```text
使用 $ecommerce-product-ads-skill 处理当前任务，从 Stage 0 开始。
```

Skill 保留根目录源文件，自动创建 `input/`、`work/`、`output/`；也支持预先建立完整 `input/`。`text.pdf` 是事实与锁定文案来源，商品与 Logo 是受保护资产，PDF 未提供的信息保持 `null`。

## 工作区与 Skill 资源

- 任务目录只保存输入、工作版本和最终输出。
- 已安装 Skill 保存 templates、Design Knowledge、真实案例、字体资源和验证脚本。
- 所有任务产物只写入当前任务目录；已有 `state.yaml` 时继续任务，不无条件覆盖。
- 输入不完整时列出缺失文件并停止。
- 开发仓库模式、`examples/nori/` 和 Workspace Bootstrap 保持可用。

无需 API key。主视觉使用 Codex 内置 ImageGen；Python 只负责初始化和确定性验证。

## V2.3 流程

```text
Stage 0  需求与商品分析
   ↓
Stage 1  Pattern + 可选案例启发 → 3 个 Key Visual Concept
   ↓
Checkpoint A  A / B / C / AUTO，选择创意讲什么
   ↓
Stage 2  Style + Composition + Typography + Reference + Art Direction
   ↓
Checkpoint B  确认或调整生成前 Visual Direction
   ↓
Stage 3  ImageGen 完整 Key Visual
   ↓
Stage 4  Design QA
   ↓
Stage 5  Final Human Check：A 接受 / B 迭代 / C 原始资产恢复
   ↓
Stage 6  导出正式 PNG
```

Checkpoint A、Checkpoint B、Stage 5 分别负责 Concept Decision、Visual Direction Decision、Final Delivery Decision；Checkpoint B 不替代最终 A/B/C 检查。

## Visual Direction

Stage 2 依据商品与品牌、已选 Concept、Campaign 与受众、最后才是 Reference，决定整体 Style；再从构图知识中选择关系式 Composition Archetype，避免无理由的“Logo → 标题 → 居中商品 → 卖点 → 价格 → CTA”默认堆叠。

Typography 是生成前决策：先写语义化的标题方向和 ImageGen 指令。手写字体库只在适合时用于内部分析，默认不把预览图输入 ImageGen，不安装或精确渲染 TTF。

真实案例仍采用 `same_category / cross_category / none`，最多 2 张，也可以 0 张。跨品类依据设计问题相似，而不是商品名相似；只学习焦点、密度、场景、光影与视觉机制，不复制。

## QA 与迭代

Stage 4 保留商品、Logo、文案、品牌、画布和 artifact 检查，并包含：

- `key_visual_integrity`
- `typography_fit`
- `style_alignment`
- `composition_distinctiveness`

Stage 5 的 B 按问题回 Stage 1、2 或 3；Style/Composition 失败优先回 Stage 2。C 只恢复失真的原始商品或 Logo，保留整体创意与构图。

## 关键文件

- `work/brief.yaml`：事实、锁定文案与商品视觉分析。
- `work/concepts.yaml`：三个 Key Visual Concept、推荐与选择。
- `work/visual_strategy.yaml`：Key Visual、Style、Typography、Reference 与 Art Direction。
- `work/layout.json`：Composition、层级、宽松空间关系与资产保护。
- `work/state.yaml`：Stage 0～6、Checkpoint A/B 和最终决定。
- `work/qa_report.md`：Design QA。
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

`examples/nori/` 展示完整的 Stage 0～2 数据结构与两个 Checkpoint；示例不强制选择真实案例或手写字体，也不重新生成正式 PNG。
