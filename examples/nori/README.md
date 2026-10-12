# NORI V2.3 示例

该示例真实展示：

1. Stage 0：从 PDF 提取任务事实，并从商品图记录可见的 `product_visual`；
2. Stage 1：生成三个具有不同核心画面关系的 Key Visual Concept；
3. Checkpoint A：依据 brief 使用 AUTO 选择 Concept A；
4. Stage 2：只深化已选择的 Concept，形成 `Organic Lifestyle` Style Direction、`Asymmetric Editorial + Diagonal Dynamic` Composition 与语义化 Typography Direction；
5. Checkpoint B：确认 Visual Direction 后才允许进入 Stage 3；本例没有充分理由绑定真实案例或手写字体，因此使用 `reference_guidance.mode: none`、`selected_source: null` 和 `use_preview_as_image_reference: false`。

示例停在 Stage 3 ImageGen 前；`work/qa_report.md` 只展示 V2.3 QA 字段结构，不代表已执行 Stage 4。秋季、通勤、绿色和保温杯只属于 NORI，不是 Skill 的硬编码规则。

```powershell
python ../../scripts/validate.py --project . --stage input
python ../../scripts/validate.py --project . --stage work
```
