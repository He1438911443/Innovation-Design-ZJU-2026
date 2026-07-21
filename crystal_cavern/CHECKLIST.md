# Crystal Cavern — 最终交付检查清单

> 目标：答辩前所有交付物就绪，每项打勾确认

---

## 一、代码与工程

- [ ] **7 个 Python 模块** — cave_terrain.py / crystal_seed.py / crystal_growth.py / cave_lighting.py / crystal_ui.py / arnold_render.py / batch_render.py — 全部可运行、无报错
- [ ] **final_scene.py** — 全管线集成，8 阶段 progressWindow，单函数 `build(seed, density, fog_density, render)`
- [ ] **MCP 集成** — 28 个 Maya 技能已部署（dcc-mcp-maya v0.9.16），通过 `cmds.loadPlugin("dcc_mcp_maya_plugin")` 加载
- [ ] **GitHub 就绪** — https://github.com/He1438911443/Innovation-Design-ZJU-2026 — 128 个文件

---

## 二、GUI 用户界面（25 分）

- [ ] **4 标签页** — Terrain / Crystals / Lighting / Render
- [ ] **16 个控件** — 全部有 min/max 安全范围 + 合理默认值
- [ ] **Logo 品牌文字** — "◆ Crystal Cavern v10 ◆" 显示在窗口顶部
- [ ] **Generate 按钮** — 读取所有控件值 → 调用 `final_scene.build()`
- [ ] **progressWindow** — 8 阶段进度条（Cleaning → Materials → Shell → Terrain → Stalactites → Seeds → Crystals → Lighting）
- [ ] **"Render Still" 按钮** — 触发 Arnold 渲染
- [ ] **UI 设计文档** — `Crystal_Cavern_UI_Design_Document.docx` 已提交，包含：
  - [ ] Section 1: Layout Hierarchy（完整树形图）
  - [ ] Section 2: Callback Functions（generate / reset / render / close）
  - [ ] Section 3: Control Details Table（16 控件 + 安全范围）
  - [ ] Section 4: User Guide（打开 / 生成 / 渲染 / 参数修改）
  - [ ] Section 5: Parameter Comparison（紫水晶 vs 红宝石对比表）

---

## 三、答辩 PPT（v3 需要重做）

- [ ] **12 页，深色科技风**，所有图片已嵌入（非占位符）
- [ ] Slide 1: 标题页 — Crystal Cavern / 浙大 2026 / Prof. Xiaosong Yang
- [ ] Slide 2: 项目概述 — 统计数据 + 实景概念图
- [ ] Slide 3: 实景参考 — 奈卡水晶洞 vs 程序化生成目标（**嵌入 ../水晶实景参考/ 2-4 张**）
- [ ] Slide 4: 算法创新 — 四卡片（Diamond-Square / Poisson-disc / L-System / Subsurface）
- [ ] Slide 5: 五阶段管线 — Stage 1→5 流程图 + **嵌入 final_output/overview.0000.png**
- [ ] Slide 6: 代码架构 — 7 模块清单
- [ ] Slide 7: 晶体几何创新 — 六棱柱 / aimConstraint / L分支 / 根部嵌入 / 渐变
- [ ] Slide 8: 材质与灯光 — SSS + transmission + coat + 三层布光 + 体积雾
- [ ] Slide 9: 交互 GUI — 截图 + 功能点
- [ ] Slide 10: 最终渲染 — **左 final_output/scene1_amethyst/render.png** / **右 final_output/scene2_ruby/render.png**
- [ ] Slide 11: 动画成果 — 960 帧飞越 + 56 颗生长动画
- [ ] Slide 12: AI 工具 + 评估对照 + Thank You

---

## 四、三维场景与动画

- [ ] **6 个 .ma 场景文件** — 在 `final_output/` 和 `renders/` 下，可在 Maya 中打开
- [ ] **最新场景** — `renders/final_v10/crystal_cavern_v10.ma`（1.2 MB，56 颗大晶体）
- [ ] **960 帧飞越动画** — 在场景文件中，Maya 中按 ▶ 可播放
- [ ] **56 颗晶体生长动画** — Scale 0→1，错开启动帧，720 帧周期
- [ ] **Arnold 渲染设置已配置** — AA=5, transmission=5, SSS=3, 1920×1080 EXR

---

## 五、渲染图

- [ ] **至少 1 张 Arnold 渲染图** — `../生成图/0101.jpg` 或 `final_output/arnold_render.png`
- [ ] **紫水晶场景** — `final_output/scene1_amethyst/`（render.png + viewport + .ma + EXR）
- [ ] **红宝石场景** — `final_output/scene2_ruby/`（render.png + viewport + .ma + EXR）
- [ ] **两套参数对比截图** — 同参数不同 seed 的不同结果

---

## 六、文档

- [ ] **FINAL_REPORT.md** — 算法引用 + 创新说明 + 评估标准对应
- [ ] **PRESENTATION_SCRIPT.md** — 6 分钟英文讲稿 + UI 部分 + L-System 理论
- [ ] **CHECKLIST.md** — 本文件
- [ ] **ppt_prompts.md** — PPT 配图生成 prompt

---

## 七、口头汇报脚本补充

### UI 部分（25 分关键点，~1 分钟）

"我的 GUI 遵循 Maya 标准布局层级——window 下面 tabLayout，每个 tab 里 columnLayout 组织控件。4 个标签页把参数按 Terrain / Crystals / Lighting / Render 分组——因为 16 个控件堆在一页会非常拥挤。这也是张老师课上强调的 tabLayout 最佳实践。"

"每个控件都有安全范围——Seed 1~99999, Density 0.5~4.0——防止用户输入崩溃值。默认参数就能生成不错效果，因为用户是'超级懒的'，他们直接按 Generate。"

"生成过程中有 progressWindow 显示 8 阶段进度条，用户知道系统在运行，不会以为卡死了。"

### L-System 理论（~30 秒）

"晶体生长基于 L-System，1968 年由 Lindenmayer 提出。核心思想——从字符串 'F' 出发，反复重写如 'F→F[+F][-F]'，多轮迭代后得到复杂形态。这就是'自相似性'——远处看是大树，近处看每根枝条是小树。"

"我在三维空间实现这个思想——每颗主晶在球面上随机方位角和仰角，生成 3-8 根侧生晶体。迭代次数、分支角度、长度都是可控参数。"

---

## 八、提交

- [ ] GitHub README.md 展示项目简介
- [ ] Word 文档提交（UI Design Document）
- [ ] Maya .ma 场景文件随附
- [ ] 渲染图随附
- [ ] 答辩 PPT 最终版就绪

---

*最后更新：2026-07-22 · 未来创新设计 · 浙江大学*
