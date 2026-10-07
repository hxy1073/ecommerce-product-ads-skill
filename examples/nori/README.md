# NORI 示例

本示例包含固定的三项输入，以及由 `text.pdf` 事实生成的 Stage 0 文件和 Stage 1 策略/布局。

示例停在 ImageGen 前，便于测试者观察 Codex 是否会：

1. 保持 PDF 中未给出的像素宽高为 `null`；
2. 正确区分中英文文案；
3. 保护保温杯外形、颜色、杯身标志与品牌 Logo；
4. 采用 ImageGen-first，而不是默认拼 SVG 海报。

测试时可在本目录执行：

```powershell
python ../../scripts/validate.py --project . --stage input
python ../../scripts/validate.py --project . --stage work
```

