# PPT 修改意见 — 算法迭代与创新点展示

> 给 Codex：这是一份结构化的 PPT 修改指南。逐页列出每页应该怎么改，用什么图，说什么算法迭代线。

---

## 全局建议

1. **v3 PPT 整体方向对**，但需要增强「算法进化叙事」——让老师看到你不是一次做出来，而是从 v1 粗糙→v2 可行→v3 精品这样迭代过来的。
2. **每页建议增加迭代标注**：底部或侧边加小标签「v1→v2→v3 进化」。
3. **字体方案**：中文标题 36-40pt（思源黑体），英文算法名 28pt（Arial），正文 18-20pt。深色底(`#0f0c29`→`#302b63`) + cyan(`#00d4ff`) + purple(`#7b2ff7`) 强调色。

---

## 模块级算法进化（核心卖点）

### 一、晶体生长 `crystal_growth.py` — 三次代际跳跃

| 阶段 | 时间 | 实现 | 问题 |
|------|------|------|------|
| **v1** | 7/19 | `polyCylinder` 圆柱体堆叠，叠加随机角度 | ❌ 像钉子，不是水晶；❌ 只有1层分支 |
| **v2** | 7/20 | `polyCone` 六边形(sx=6)棱柱 + `aimConstraint` 法线对齐 + 一层球面分支 + 根部嵌入12% | ✅ 形状接近真实；⚠️ aimConstraint 在 ±Z 轴附近 gimbal lock；⚠️ 只有1层分支像杂草 |
| **v3** (hanqian) | 7/22 | 递归 L-system(MAX_DEPTH=2, BRANCH_PROB=0.4) + 六方晶系60°方位角偏置 + axis-angle最短旋转(无aimConstraint) + BSSRDF标注澄清 | ✅ 二级三级分支模拟真实晶簇；✅ 分支沿晶面生长；✅ 无gimbal lock；✅ 无临时locator节点开销 |

**PPT 应该展示的点**：
- 对比截图：v1钉子→v2六棱柱→v3递归分支
- 关键创新：**递归 L-system × 六方晶系方位角偏置 × axis-angle旋转**
- 一句话："从单层杂草分支变为递归重写的晶体枝干——每次重写概率40%、深度上限2层、每层缩放60%"

### 二、种子分布 `crystal_seed.py` — 从贪婪到真算法

| 阶段 | 实现 | 复杂度 | 问题 |
|------|------|:---:|------|
| **v1→v2** | `distribute_seeds_simple`：随机排列顶点，遍历时检查已选种子的距离 | O(n·k) | 标注引用了"Bridson (2007)"但**实际不是 Poisson-disc**——只是普通贪婪 |
| **v3** (hanqian) | `distribute_seeds_poisson`：真正的 Bridson(2007) + 空间哈希(cell=min_dist) + 3×3邻域查找 + Bridson式active列表 + 地面平面测距(x,z) | O(n) | ✅ 真实 Poisson-disc；✅ min_dist 反映表面密度(hills不受影响)；✅ 学术诚信修复（旧版标了 Bridson 但没用） |

**PPT 应该展示的点**：
- 分布图对比：旧版随机簇 vs 新版 Poisson-disc
- 关键创新：**空间哈希加速 + 地面平面测距**
- 一句话："用真正的 Bridson(2007) Poisson-disc 替换了旧版未正确实现的'Bridson简化版'——O(n)空间哈希、地面平面测距保证表面密度"

### 三、地形生成 `cave_terrain.py` — 性能飞跃

| 阶段 | 实现 | 速度 |
|------|------|:---:|
| **v1→v2** | 逐顶点 `cmds.move()`：66,049次 Maya API 调用 | ~60秒 |
| **v3** (hanqian) | OpenMaya2 `MFnMesh.setPoints()`：纯Python预计算 → 批量写入 | ~2秒 |

**PPT 应该展示的点**：
- 速度对比：60s → 2s（30x 提速）
- 关键创新：**MFnMesh.setPoints 批量写入**
- 一句话："处理 66,049 个顶点的地形从 60 秒降到 2 秒——OpenMaya2 批量 API 替代逐顶点 cmds.move"

### 四、灯光/材质 `cave_lighting.py` — 学术澄清

| 阶段 | 理解 | 问题 |
|------|------|------|
| **v1→v2** | 文档说"point lights 模拟 SSS" | ⚠ 老师会问：你的 SSS 到底怎么实现的？点光源不能算 SSS！ |
| **v3** (hanqian) | 文档明确分层：**材质端**=Arnold BSSRDF(Jensen 2001) → 真正的 SSS；**灯光端**=20盏accent点光源 → 外光补光 | ✅ 学术严谨；✅ 不会在答辩时被问到卡壳 |

**PPT 应该展示的点**：
- 一句话："SSS 由材质 BSSRDF 负责，点光是外光补光——论文引用和代码实现对得上"

---

## 逐页 PPT 修改清单

### Slide 1: 标题（不改）

---

### Slide 2: 项目概述
- **增加**：一条时间线
  ```
  7/19 v1 原型  →  7/20 v2 管线  →  7/21 v3 精品
  ```
- **增加**底部小字："3 天内从算法原型迭代到完整交付，4 个核心模块各经历 2-3 轮代际进化"

---

### Slide 3: 实景参考
- **改**：左边的参考图不仅放奈卡水晶洞，也放**同角度生成图对比**——"我们的代码生成的"和"实景"的并排对比
- **图片路径**：
  - 实景：`../水晶实景参考/0cf7cc1349abe3d1248e12b04438b58c~...webp`（或挑最清晰的一张）
  - 生成：`final_output/arnold_render.png` 或 `../生成图/0101.jpg`

---

### Slide 4: 算法创新（四卡片）
- **改**：每张卡片增加「迭代标签」
  - Diamond-Square: 标签「v1→v3：算法不变，v3 新增 OpenMaya2 批量写入」
  - Poisson-disc: 标签「v1❌假Bridson → v3✅真Bridson + 空间哈希」
  - L-System: 标签「v1无 → v2一层分支 → v3递归重写 + 六方晶系」
  - Subsurface: 标签「v3 学术澄清：材质BSSRDF ≠ 点光补光」

---

### Slide 5: 五阶段管线
- **改**：管线图下方增加一条**迭代版本标注条**
  ```
  v1 (7/19)  仅地形+随机散点晶体
  v2 (7/20)  六棱柱 + 一层分支 + 根部嵌入 + aimConstraint
  v3 (7/22)  递归L-system + 真Bridson + OpenMaya2 + axis-angle旋转 + 学术澄清
  ```

---

### Slide 6: 代码架构（基本不改）
- **增加**：文件数量标注「v1: 6模块 / v2: 7模块 / v3: 10模块(含build脚本+UI文档+检查清单)」

---

### Slide 7: 晶体几何创新
- **这是核心亮点页，需要重新设计**
- 建议拆成 3 列对比：
  ```
  v1 圆柱堆叠           v2 六棱柱+一层分支        v3 递归L-system
  [v1截图或图示]        [v2截图]                  [v3生成图/0101.jpg]
  圆柱体 · 像钉子        六棱柱 · 根部嵌入          二级三级分支 · 晶面方位角
  无分支                aimConstraint对齐          axis-angle · 无gimbal lock
  ```
- 底部标注每个版本的创新关键词

---

### Slide 8: 材质与灯光
- **改**：增加「学术严谨性」模块——标注 SSS 归属
  - 左列：Arnold BSSRDF(Jensen 2001) — 真正的次表面散射（`subsurface`/`subsurfaceColor`/`subsurfaceRadius`/`subsurfaceScale`）
  - 右列：20 盏 accent 点光源 — 外光补光（`intensity 800-1600` / `decayRate 0`）
  - 标注："材质端做 SSS，灯光端做补光——两者分开、各司其职"

---

### Slide 9: 交互 GUI（基本不改）
- **增加**：底部标注「v2→v3 新增：Logo 品牌标识 + 8阶段 progressWindow 进度条」

---

### Slide 10: 最终渲染
- **改**：渲染结果旁边标注使用的算法版本
- 左图（scene1）下标注「v3 递归L-system + 真Bridson」
- 右图（scene2）下标注「v3 递归L-system + 真Bridson」

---

### Slide 11: 动画成果（基本不改）
- **增加**：标注「v2→v3：相机从硬编码坐标变为动态晶体位置驱动」
- 增加生长动画描述：「56颗晶体 scale 0→1，每颗错开启动帧，模拟天然矿物结晶」

---

### Slide 12: AI工具 + 评估 + 致谢
- **改**：AI工具表格增加一列「贡献范围」
  - Claude Code：算法设计 · 代码生成 · 全模块重构 · 场景搭建
  - Claude MCP：Maya 直接操控 · 28技能 · 调试诊断
  - 协作者 hanqian：递归L-system · Bridson实现 · OpenMaya2优化 · PPT v3
  - ChatGPT：算法选型 · 论文引用核实
- **增加**：评估对照表底部的版本标注「全部代码在 main 分支，hanqian 改进在 7/22 合并」

---

## PPT v3 还有一个已知问题

图片嵌入用的是虚线框占位符——需要替换成实际文件路径：
- Slide 3 参考图位置 → 嵌入 `../水晶实景参考/` 中的 2 张清晰图
- Slide 10 渲染图位置 → 嵌入 `final_output/scene1_amethyst/render.png` 和 `scene2_ruby/render.png`

---

## 可用的图片资源路径（绝对路径）

| 用途 | 路径 |
|------|------|
| 实景参考1 | `/Users/xixi/大学/未来创新设计/水晶实景参考/2054a191eda785718bc103fd9e86e0f4~...jpeg` |
| 实景参考2 | `/Users/xixi/大学/未来创新设计/水晶实景参考/266362bbf6432235b7c4c433d7b25fd1~...jpeg` |
| 实景参考3 | `/Users/xixi/大学/未来创新设计/水晶实景参考/3b80ff12a708b83f91132dc8a65a690e~...png` |
| 紫水晶渲染 | `/Users/xixi/大学/未来创新设计/crystal_cavern/final_output/scene1_amethyst/render.png` |
| 红宝石渲染 | `/Users/xixi/大学/未来创新设计/crystal_cavern/final_output/scene2_ruby/render.png` |
| Arnold渲染 | `/Users/xixi/大学/未来创新设计/crystal_cavern/final_output/arnold_render.png` |
| 手动渲染 | `/Users/xixi/大学/未来创新设计/生成图/0101.jpg` |
| 全景截图 | `/Users/xixi/大学/未来创新设计/crystal_cavern/final_output/overview.0000.png` |
| 最新截图 | `/Users/xixi/大学/未来创新设计/crystal_cavern/final_output/latest_view.0000.png` |
