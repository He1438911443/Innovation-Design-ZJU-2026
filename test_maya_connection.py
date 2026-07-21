"""
Maya + VS Code 连接测试脚本

用法：
1. 确保 Maya 已打开并启动了命令端口（userSetup.py 自动执行）
2. 在 VS Code 里选中这段代码，按 Ctrl+Enter 或 Cmd+Enter 发送到 Maya 执行
3. Maya 里应该出现一个立方体 + 打印 "连接成功" 信息

如果 VS Code 没有自动连接 Maya，可能需要安装 MayaCode 插件并配置端口：
- VS Code → 扩展 → 搜索 "MayaCode" → 安装
- 设置端口为 7002（与 userSetup.py 中的 PORT 一致）
"""

import maya.cmds as cmds

# 1. 清理场景
cmds.file(new=True, force=True)

# 2. 创建一个立方体
cube = cmds.polyCube(name="connection_test_cube")[0]
cmds.move(0, 3, 0, cube)

# 3. 给它上色
shader = cmds.shadingNode("lambert", asShader=True)
cmds.setAttr(shader + ".color", 0.2, 0.6, 0.8, type="double3")
cmds.select(cube)
cmds.hyperShade(assign=shader)

# 4. 打印验证
print("=" * 50)
print("✅ VS Code → Maya 连接正常！")
print("✅ 立方体已创建：connection_test_cube")
print("✅ 材质已应用")
print("=" * 50)

# 5. 如果到这里没有报错，说明一切正常
# 你可以尝试：
# - 选中下面这行代码，Ctrl+Enter 单独执行：
cmds.polySphere(name="bonus_sphere", radius=2)
cmds.move(5, 3, 0, "bonus_sphere")
print("✅ 球体也已创建！连接完全正常 🎉")

