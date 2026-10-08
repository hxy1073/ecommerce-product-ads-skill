# NORI V2 示例

该示例真实展示：

1. Stage 0：从 PDF 提取任务事实，并从商品图记录可见的 `product_visual`；
2. Stage 1：生成三个在营销叙事与场景上明显不同的 Concept；
3. Checkpoint A：依据 brief 使用 AUTO 选择 Concept A；
4. Stage 2：只深化已选择的 Concept，形成高自由度 Art Direction 与非坐标式 layout。

示例停在 Stage 3 ImageGen 前。秋季、通勤、绿色和保温杯只属于 NORI，不是 Skill 的硬编码规则。

```powershell
python ../../scripts/validate.py --project . --stage input
python ../../scripts/validate.py --project . --stage work
```

