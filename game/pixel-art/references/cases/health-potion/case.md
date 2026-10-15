# 药水瓶 Shader 底稿

自制红色药水瓶，展示 Blender 真实光照、固定色板和材质分区的第三阶段输出。本例是 Shader 技术底稿，尚不是 Aseprite 精修后的成品。

- 原生尺寸 64×64，Shader 1.3.0，色板 4.3，实际 25 色。
- 色系为 `ruby/earth/blue`；木塞与系带映射 earth，瓶口映射 blue，瓶身与药液映射 ruby。
- alpha 为 0/255；木塞与瓶口区域跨色系像素为 0。
- 使用红色着色玻璃、红药液和蓝灰瓶口；512 samples 及具体材质值属于本例参数，不作为其他对象默认值。

[原生 PNG](native.png)、[4 倍预览](preview.png)、[技术清单](manifest.json)。本例不包含第三方游戏截图、提取素材或临摹稿。公开案例不附带包含本机路径的 Blender 工程；复现接口见 [Pixel Shader](../../../styles/parchment-fantasy/PIXEL-SHADER.md)。
