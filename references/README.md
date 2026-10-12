# Design References 使用说明

`references/` 中五类资源职责固定：

- `patterns/`：结构化设计方法知识，用于 Stage 1 发散与 Stage 2 深化。
- `style_guide.md`：整体视觉语言知识，用于 Stage 2 的 Style Decision。
- `composition_guide.md`：商品、标题、信息与空间关系知识，用于 Stage 2 的 Composition Decision。
- `风格案例图/`：真实优秀主视觉案例，只用于提炼视觉焦点、信息密度、场景逻辑、光影材质与 Key Visual 机制。
- `手写合集字体/`：可选的大标题字形与气质分析资源；只查看总览和预览图，不自动安装或精确调用 TTF，默认也不把预览图交给 ImageGen。

六个 Pattern 为：

- `01_hero_product.json`
- `02_lifestyle_scene.json`
- `03_promotional_poster.json`
- `04_feature_callout.json`
- `05_seasonal_campaign.json`
- `06_premium_minimal.json`

Pattern 是设计启发，不是固定模板、商品事实来源、完整布局或 ImageGen Prompt。选择是 advisory：一个优秀 Concept 可以只使用一个 Pattern；需要组合时，最多 1 个 primary + 2 个 secondary，列表第一项视为 primary。

Pattern 禁止规定固定坐标、Logo 位置、HEX 色、字体、卡片形状、像素占比或具体品牌海报复刻。Stage 3 不把 raw Pattern 直接拼入 Prompt，而是使用 Stage 2 已形成的 Art Direction。

真实案例采用 `same_category / cross_category / none`：优先同品类；没有同品类时按“设计问题相似”跨品类借鉴；没有高价值匹配时使用 `none`。参考图可以为 0 张，Stage 2 最多选择 2 张，且不得复制原构图、品牌、文字或商品形态。

Style 与 Composition 名称不是验证器枚举；知识文档后续可扩展而不需要改代码。Style 优先由商品与品牌决定，Composition 必须落实已选 Key Visual Concept，并避免无理由的标准纵向堆叠。两份 Guide 都只描述设计逻辑，不是 Style Lock 或固定布局。

手写字体不是强制资源。只有与商品、品牌、Key Visual、Style 和 Composition 匹配时，才浏览 `ZYHJ01-字体列表.jpg` 与候选目录的 `C-预览 (1).jpg/.png`，最多记录 1 套 `selected_source` 作为内部设计灵感。Stage 3 默认只消费语义化的 `typography.imagegen_instruction`；TTF 仅作为未来资产保留。
