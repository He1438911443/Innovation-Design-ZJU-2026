# Crystal Cavern — 答辩前汇报检查清单

> 答辩当日 / 提交前逐项核对，全部打勾方可离手。
> 最后更新：2026-07-22 · 未来创新设计 · 浙江大学

---

## 交付物核对（答辩前）

- [ ] **答辩 PPT v3 图片齐全** — `答辩PPT_v3.pptx` 12 页深色科技风，所有图片为实际嵌入（非虚线占位符）：slide 3 实景参考、slide 2 / 5 / 8 渲染与 viewport、slide 10 紫水晶 vs 红宝石双场景对比
- [ ] **UI 设计文档已提交** — `Crystal_Cavern_UI_Design_Document.docx`（Layout 层级 / Callback / 16 控件安全范围 / 用户指南 / 参数对比）
- [ ] **Maya 场景文件就绪**（`final_output/` 与 `renders/` 下）— `scene1_amethyst/crystal_cavern.ma`、`scene2_ruby/crystal_cavern.ma`、`scene_latest/crystal_cavern.ma` 等，可在 Maya 中直接打开
- [ ] **Arnold 渲染图（至少 1 张）** — `final_output/arnold_render.png` 及 `scene1_amethyst/render.png` / `scene2_ruby/render.png`，1920×1080
- [ ] **960 帧飞越动画可在 Maya 中播放** — 动态相机路径 6 关键帧 spline 插值，32 秒 @ 30fps，打开 .ma 按 ▶ 可播放
- [ ] **56 颗晶体生长动画（scale 0→1）** — 错开启动帧 (spread 200 frames)，每颗 520 帧周期，700+ 帧长成完整晶簇
- [ ] **源代码 GitHub 就绪（128 文件）** — https://github.com/He1438911443/Innovation-Design-ZJU-2026，7 个 Python 模块均可运行
- [ ] **口头脚本补充完成** — `PRESENTATION_SCRIPT.md` 末尾已追加 GUI Design（~1 分钟）与 L-System 理论（~30 秒）两段现场脚本

## 文档完整性

- [ ] **FINAL_REPORT.md 更新** — 算法引用 / 创新说明 / 评估标准对应齐全，含 6 分钟英文讲稿主稿

---

## 现场播放自检（上台前 5 分钟）

- [ ] PPT 在答辩电脑上打开无字体丢失（微软雅黑 / Arial / Consolas）
- [ ] 第 2 / 3 / 5 / 8 / 10 页图片正常显示（非红叉、非黑框）
- [ ] 演示用 Maya 场景预加载到可播放帧范围
- [ ] 备份 PDF（导出 `答辩PPT_v3.pdf`）已拷入 U 盘

---

*每项确认无误后再上台 —— Crystal Cavern, ZJU 2026.*