# GLM-4.7 Handoff — Crystal Cavern 最终优化

## 当前状态

Maya 2027 已运行 (PID 51672)，cmdPort 7002 在线。

**场景已构建并保存于**: `renders/hanqian_final/crystal_cavern.ma`

**当前参数 (已生效)**:
- Dome环境光: 1.0 (已从0.30提升3x)
- Key主光: 350 (已从180提升2x)
- Rim背光: 80 (已从40提升2x)
- Glow晶体辉光: 6000 (已从2000-4000提升)
- Camera ai_exposure: 6.0 (已从1.5提升4x)
- SSS: weight=0.95, scale=4.0, radius=0.8
- Transmission: weight=0.72, depth=5.0
- Fog: density=0.02
- 相机: 30keys, 2400f, dist=8.0, Y范围 [-1, 4.3]
- 56颗六棱柱晶体 + 球壳洞穴 + 钟乳石

**文件路径**: `/Users/xixi/大学/未来创新设计/crystal_cavern/`
**核心文件**: `final_scene.py` (全管线, ~830行)
**GUI**: `crystal_ui_v3.py` (5标签页)

---

## 北极星目标

```
一个跑在 Maya 里的「水晶洞穴一键生成器」:
观众看你拖滑块、按 Generate → 30秒凭空长出一个会发光、会飞越的水晶洞穴
按 Render → 电影级渲染图，按 Play → 飞越动画
每个 seed 都是没人见过的洞穴

最终交付: 2张1920×1080 Arnold EXR渲染图 (紫水晶seed=2026 + 红宝石seed=7777)
         + 1段飞越录屏 + PPT + GUI设计文档
```

---

## 你(GLM)需要做的事

### 1. 连接Maya
cmdPort已在7002:
```python
import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(600)
s.connect(('127.0.0.1', 7002))
code = """...your Maya Python code..."""
s.sendall((code + "\n").encode())
time.sleep(0.5)
s.shutdown(socket.SHUT_WR)
# read response...
s.close()
```

### 2. 核心任务: 渲染两张满意的静帧
当前场景在Maya viewport中。步骤:
1. 加载 `final_scene.py` 最新版 → `final_scene.build(seed=2026, ...)` 出紫水晶
2. 截图→看效果→如果暗→调灯光参数→重新截图
3. 同样的seed=7777出红宝石
4. Arnold Render View 手动触发渲染 (远程batch render有Maya限制)
5. EXR转PNG: `ffmpeg -y -i input.exr -vf "eq=gamma=X" -q:v 2 output.png`

### 3. 如果不够亮→直接改场景中灯光
```python
# Dome ×3
cmds.setAttr('CCV9_ambient.intensity', 3.0)  # 尝试
# Key ×2  
cmds.setAttr('CCV9_entrance_key.intensity', 700)  # 尝试
# Glow ×2
for lt in cmds.ls('CCV9_glow_*'):
    cmds.setAttr(lt+'.intensity', 12000)
# Exposure
cmds.setAttr(cam+'.ai_exposure', 10.0)
```

### 4. 成功标准
- 渲染图有清晰的光影层次 (暖金主光 + 蓝背光 + 晶体彩色辉光)
- 暗部接近纯黑但不死黑
- 晶体有半透光SSS效果
- 体积雾可见丁达尔光束
- 洞穴深处比入口暗

---

## 关键说明
- 不要偏离北星: 最终产物是2张渲染图+飞越录屏+PPT，不是更多代码
- Arnold batch render通过cmdPort不稳定——手动在Arnold Render View点Start Render最可靠
- 当前灯光参数已在代码中永久化(`final_scene.py`已push GitHub)
- GitHub: https://github.com/He1438911443/Innovation-Design-ZJU-2026
