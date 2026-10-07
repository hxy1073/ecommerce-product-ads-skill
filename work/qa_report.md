# NORI 主视觉 QA 报告

检查日期：2026-09-30  
当前版本：`hero_zh_v01.png`、`hero_en_v01.png`  
整体状态：`needs_human_review`

## 自动与视觉检查

| 检查项 | 中文版 | 英文版 | 说明 |
|---|---|---|---|
| PNG 可打开 | pass | pass | 文件完整，可正常解码 |
| 画布规格 | pass | pass | 1200 × 1500，严格 4:5 |
| 商品主体突出 | pass | pass | 商品为最大、第一视觉焦点 |
| 商品轮廓与部件 | needs_human_review | needs_human_review | 奶油白杯身、深绿杯盖、环形把手、杯身双叶标识均保留；ImageGen 仍可能产生细微比例或表面差异 |
| 品牌 Logo | needs_human_review | needs_human_review | 双叶方向、颜色和比例视觉上接近原 SVG；需人工判断是否要求原始矢量级完全一致 |
| 标题 | pass | pass | “轻装出行 温度随行” / “Travel Light. Keep It Warm.” 清晰且层级突出 |
| 产品名 | pass | pass | 与 brief 对应语言一致 |
| 卖点 1 | pass | pass | 316 材质以金属徽章呈现 |
| 卖点 2 | pass | pass | 12 小时以仪表式 callout 呈现 |
| 卖点 3 | pass | pass | 防漏锁扣以引线指向杯盖 |
| 价格 | pass | pass | 129 为最大数字信息，价格前缀和币种完整 |
| 活动时间 | pass | pass | 日期完整、可读 |
| CTA | pass | pass | “立即选购” / “Shop now” 完整、突出 |
| 语言纯度 | pass | pass | 中文版无英文营销文案；英文版无中文文案 |
| 版式与安全区 | pass | pass | 无明显溢出、遮挡或低对比文本 |
| 品牌调性 | pass | pass | 简洁、自然、可靠，符合秋日通勤主题 |
| 明显 AI artifact | pass | pass | 未发现影响交付的乱码、畸形道具或重复文字 |

## 结论

两张图已通过文件、尺寸、文案、层级和版式检查，可以进入 Stage 4。由于商品与 Logo 属于受保护资产，最终是否接受当前 ImageGen 保真度必须由人工决定。

- 若当前保真度可接受：选择 **A**。
- 若希望更换整体创意或重新处理文案/场景：选择 **B**。
- 若认为商品或 Logo 有失真：选择 **C**，保留当前环境和营销版式，使用原始 `product.png` / `logo.svg` 修复。

