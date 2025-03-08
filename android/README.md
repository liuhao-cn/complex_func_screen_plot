# 复数函数可视化工具 - Android版

这是复数函数可视化工具的Android移植版本，使用Kivy框架将Python代码转换为Android兼容的应用。

## 项目结构

- `main.py` - 主应用入口
- `complexfunc.kv` - Kivy界面布局文件
- `buildozer.spec` - Buildozer配置文件，用于打包APK

## 功能特点

- 实时显示复数平面上的点到函数值的映射
- 触摸控制绘制轨迹
- 可视化轨迹跟踪功能
- 实时显示坐标值和函数值
- 支持多段轨迹绘制
- 清晰的坐标系统和刻度显示
- 导数可视化模式，直观展示复变函数的局部行为

## 使用方法

1. 触摸控制：
   - 触摸并拖动：绘制轨迹
   - 触摸屏幕：实时显示对应点的函数值

2. 界面按钮：
   - 清除：清除所有轨迹
   - 导数模式：切换导数可视化模式

3. 显示信息：
   - 左上角：显示当前点的坐标和函数值
   - 右上角：显示当前函数表达式
   - 红色轨迹：输入平面上的轨迹
   - 黄色轨迹：对应的函数值轨迹

## 构建APK

1. 安装Buildozer：
```bash
pip install buildozer
```

2. 初始化Buildozer配置（已完成）：
```bash
buildozer init
```

3. 构建APK：
```bash
buildozer android debug
```

## 注意事项

- 需要安装Java JDK和Android SDK
- 首次构建可能需要下载依赖，耗时较长
- 建议在Linux或WSL环境下构建