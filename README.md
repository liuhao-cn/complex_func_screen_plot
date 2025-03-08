# 复数函数可视化工具

这是一个基于Pygame的复数函数可视化工具，它能够实时显示复数函数的映射关系，帮助用户直观地理解复数函数的行为。

## 功能特点

- 实时显示复数平面上的点到函数值的映射
- 支持鼠标和键盘控制
- 可视化轨迹跟踪功能
- 实时显示坐标值和函数值
- 支持多段轨迹绘制
- 清晰的坐标系统和刻度显示
- 导数可视化模式，直观展示复变函数的局部行为

## 操作范例

- 在平面上手绘水平和垂直线，观察函数值的变化
- 手绘同心圆，观察函数值的变化
- 手绘径向轨迹，观察函数值的变化
- 手绘同心矩形、菱形、正多边形，观察函数值的变化
- 在屏幕不同位置手绘小人，观察函数值小人的形态和朝向
- 在屏幕不同位置手绘矩形，观察函数值图形的形态和朝向
- 在屏幕不同位置手绘任意闭合路径，观察函数值的变化
- 导数模式下，点击鼠标左键在不同位置添加多个导数环，观察导数在不同区域的变化
- 设置不可导的函数，如 f(z)=x+y+(x^2+y^2)i，观察闭合区域和导数环的变化


## 安装依赖

运行此程序需要以下Python库：

```bash
pip install pygame numpy matplotlib
```

## 使用方法

1. 运行程序：
```bash
python screen_demo.py
```

2. 控制方式：

- **鼠标控制**：
  - 左键点击并拖动：绘制轨迹
  - 移动鼠标：实时显示对应点的函数值

- **键盘控制**：
  - W/A/S/D：在跟踪模式下控制点的移动
  - ESC键：清除所有轨迹
  - C键：清除所有轨迹
  - P键：切换导数可视化模式

3. 显示信息：
  - 左上角：显示当前点的坐标和函数值
  - 右上角：显示当前函数表达式
  - 红色轨迹：输入平面上的轨迹
  - 黄色轨迹：对应的函数值轨迹

## 功能说明

1. **实时映射**：程序会实时计算并显示复平面上点的函数值，帮助理解函数的映射关系。

2. **轨迹跟踪**：
   - 可以通过鼠标绘制连续轨迹
   - 支持绘制多段独立轨迹
   - 轨迹保持显示直到手动清除

3. **坐标系统**：
   - 清晰的笛卡尔坐标系
   - 带有刻度标记
   - 原点位于屏幕中心

4. **精确控制**：
   - 键盘控制提供精确的点移动
   - 实时显示精确的坐标值和函数值

5. **导数可视化**：
   - 按P键进入导数可视化模式
   - 在输入平面上单击会显示彩色圆环，表示不同方向的 dz
   - 同时会在函数值位置显示彩色圆环，直观展示 df
   - 彩色表示 dz 和 df 的辐角对应性
   - 圆环半径表示 dz 和 df 的绝对值关系
   - 点击鼠标左键在不同位置添加多个导数环，观察函数在不同区域的变化特性
   - 通过导数环的形状和颜色变化，直观理解函数的保角性和伸缩性

## 自定义函数

当前示例使用的是复数函数 f(z) = z³/2，您可以通过修改代码中的`complex_function`函数来可视化其他复数函数：

```python
def complex_function(z):
    return z**3/2
```

## 注意事项

- 程序需要支持中文显示的字体
- 建议在分辨率不低于1200x800的显示器上运行
- 如果遇到性能问题，可以调整`grid_size`和`move_speed`参数