# 水晶洞穴：Maya 零基础操作图解

这份手册的目标不是让你短时间学会 Maya 全部功能，而是让你能完成三件事：

1. 知道当前场景里每一部分是什么；
2. 会播放和检查晶体生长飞越动画；
3. 能向老师解释我是怎样用 Maya 验证程序生成、材质和渲染的。

## 1. 先认识当前场景

![当前 Maya 场景](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/01_current_scene_timeline.png)

看图时只需要认识四个区域：

- **左侧 Outliner（大纲视图）**：像文件夹目录，列出场景中的洞穴、晶体、灯光和相机。
- **中间 Viewport（视口）**：实时观察三维场景。这里显示的是 Viewport 2.0 预览，不等于最终 Arnold 成片。
- **右侧属性区域**：显示当前选中物体、材质或渲染节点的属性。
- **底部 Timeline（时间轴）**：当前动画范围是第 390–525 帧，24 fps。

你向老师可以这样解释：

> 我没有逐个摆放这些晶体。程序生成场景以后，我在 Maya 里检查场景层级、播放关键帧，并用 Arnold 渲染验证材质和灯光。

## 2. 场景层级是什么

![场景层级](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/02_scene_hierarchy.png)

左侧最重要的是 `crystalCavern_v10` 总组。它相当于整个项目的总文件夹。生成器把对象分组，是为了方便单独隐藏、选择和检查。

你需要理解的逻辑是：

```text
crystalCavern_v10
├── 洞穴管道与主晶室
├── 洞壁晶体与四组主晶簇
├── 灯光与体积雾
├── 飞越相机
└── Arnold 渲染节点
```

老师如果问“这些内容是不是程序生成的”，可以回答：

> 是。程序一次性创建洞穴网格、晶体分组、材质、灯光、相机和动画关键帧。Outliner 的分组是生成结果的结构证据。

## 3. 怎样播放动画

底部时间轴右侧有向前播放按钮。操作顺序：

1. 确认开始帧是 `390`、结束帧是 `525`；
2. 单击时间轴上的 `390`，检查生长开始；
3. 单击向前播放按钮；
4. 如果播放卡顿，按 `Esc` 停止，不要连续重复点击；
5. 现场汇报优先播放最终 MP4，因为它比 Maya 实时缓存更稳定。

备用视频：

`crystal_cavern/renders/tunnel_v10/crystal_cavern_growth_flythrough_FINAL_v27.mp4`

## 4. 为什么说晶体是“扎根生长”

### 第 390 帧：晶体刚从根部出现

![第390帧](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/03_growth_start_frame390.png)

这一帧中，主晶簇体积较小，位置仍然贴着岩床。这里验证的是 **Pivot（轴心）在矿物根部**。

如果轴心错误地在世界原点，晶体缩放时会从远处飞进来；现在它们从自己的根部向上变大。

### 第 450 帧：主晶簇已经长成

![第450帧](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/04_growth_mid_frame450.png)

与第 390 帧相比，可以看到：

- 主干已经明显变高；
- 子分支围绕主干展开；
- 不同晶簇错峰生长；
- 相机位置也随时间变化。

向老师解释：

> L-system 决定晶体的父子分支结构，根部 Pivot 决定动画怎样生长。一个解决“长什么样”，另一个解决“怎样长出来”。

## 5. 晶体材质是怎样组成的

![晶体材质节点](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/05_arnold_crystal_material.png)

右侧当前选中的是 `CCV10_ice`，即主要的冰晶/石英 Arnold 材质。它连接了：

- `microBump`：极轻微的表面凹凸；
- `mineralNoise`：三维矿物噪声；
- `roughnessVariation`：粗糙度变化。

最终材质不是“把透明度拉高”，而是五层共同工作：

1. 外层石英壳：折射率 IOR 1.54，控制透光和折射；
2. 深浅交替晶面：打破塑料般的均匀外观；
3. 乳白色内核：让晶体内部有厚度；
4. 薄裂纹平面：产生内部高光；
5. 微弱噪声：让矿物不显得过度干净。

不要在答辩现场随意改这些参数。你只需要知道：**外层负责透明，内部层负责真实的厚度和不规则性。**

## 6. 一键生成界面怎样使用

![生成器界面](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/06_generator_gui.png)

从零开始使用时，只记住以下顺序：

1. 打开 Maya；
2. 打开 Crystal Cavern 生成器窗口；
3. 在 Cave / Crystals / Lighting / Output 四个标签页检查参数；
4. 改 `Seed`，例如从 2026 改成 2027；
5. 按绿色 `Generate`；
6. 等待进度条完成，不要在生成过程中反复点击；
7. 按 `Preview` 或播放按钮检查动画；
8. 按 `Render Still` 输出 Arnold 静帧。

参数的大白话：

- **Seed**：洞穴方案编号；
- **Density**：晶体数量；
- **Roughness**：洞壁不规则程度；
- **Fog Density**：雾的浓度；
- **Lighting**：彩色光的强度和颜色；
- **Render Still**：渲染一张高质量图片；
- **Play / Preview**：播放飞越和生长动画。

## 7. Viewport 与 Arnold 有什么区别

### Viewport 2.0

- 优点：快、能实时播放；
- 用途：检查构图、碰撞、关键帧和动画节奏；
- 局限：透明折射、内部裂纹、体积雾不如最终渲染准确。

### Arnold

- 优点：能计算真实感更强的透射、折射、阴影和雾；
- 用途：最终静帧和高质量输出；
- 局限：每一帧渲染更慢，不适合课堂上临时等待完整动画。

最终 Arnold 成片：

![最终 Arnold 渲染](/Users/xixi/大学/未来创新设计/crystal_cavern/maya_tutorial_screenshots/07_final_arnold_render.png)

向老师解释：

> 我用 Viewport 2.0 做实时动画验证，用 Arnold 做光学和材质验证。两者不是两套模型，而是同一套程序生成几何的两种显示方式。

## 8. 你在现场最安全的操作流程

1. 汇报前先打开中文版 PPT 和最终 MP4；
2. Maya 保持打开最终动画场景；
3. 不要在现场重新 Generate，除非老师明确要求；
4. 如果老师要看生长，直接拖动时间轴从 390 到 450；
5. 如果老师要看最终质量，打开 Arnold 成片 PNG；
6. 如果 Maya 缓存提示内存不足，按 Esc 停止，改播 MP4；
7. 不要保存你在现场临时拖动或选中的状态，避免覆盖最终场景。

## 9. 老师要求现场演示新 Seed 时

先说：

> 我现在改变 Seed，生成器会重新计算中心线、隧道截面、晶体分布和局部变化。相同 Seed 可以重复得到相同结果。

然后：

1. 保存当前场景的副本；
2. 改 Seed；
3. 按 Generate 一次；
4. 等待进度完成；
5. 展示 Outliner、视口和时间轴；
6. 若要保留新结果，使用新的文件名另存，不覆盖最终版。

## 10. 一句话总结 Maya 部分

> Python 负责“按照规则自动创建”，Maya 负责“承载、检查、播放和渲染”，Arnold 负责“把几何和材质变成电影级画面”。
