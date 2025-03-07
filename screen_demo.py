import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# 设置窗口大小和标题
window_width = 1200
window_height = 800
grid_size = 200
move_speed = 2  # 增加移动速度以便更明显地看到效果

func_str = f"$f(z)=z^3/2$"
# 复数函数定义
def complex_function(z):
    # 实现与显示公式一致的函数：z^3/2
    f = z**3/2
    return f


# 初始化pygame
pygame.init()

# 加载支持中文的字体
try:
    chinese_font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 24)  # 使用黑体
    small_chinese_font = pygame.font.Font("C:\\Windows\\Fonts\\simhei.ttf", 20)  # 小号字体
except:
    print("无法加载中文字体，将使用系统默认字体")
    chinese_font = pygame.font.SysFont(None, 24)
    small_chinese_font = pygame.font.SysFont(None, 20)

# 创建窗口
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("复数函数可视化")

# 设置颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)  # 鼠标轨迹和坐标轴
YELLOW = (255, 255, 0)  # 函数值轨迹
GREEN = (0, 255, 0)  # 额外颜色
BLUE = (0, 0, 255)  # 额外颜色

# 坐标轴原点(窗口中心)
origin_x = window_width // 2
origin_y = window_height // 2

# 跟踪模式标志和轨迹点列表
tracking_mode = False
mouse_trail = []
function_trail = []
# 新增标志，表示是否需要开始新的轨迹
new_trail_segment = True

# 初始化鼠标位置变量
mouse_x, mouse_y = origin_x, origin_y

# 坐标转换函数
def mouse2Z(mousex, mousey):
    """将屏幕坐标转换为复平面坐标"""
    return complex((mousex - origin_x) / grid_size, -(mousey - origin_y) / grid_size)

def z2mouse(z):
    """将复平面坐标转换为屏幕坐标"""
    return int(z.real * grid_size ) + origin_x, int(-z.imag * grid_size ) + origin_y

# 绘制函数
def draw_coordinate_system():
    """绘制坐标系"""
    # 绘制坐标轴
    pygame.draw.line(screen, RED, (0, origin_y), (window_width, origin_y), 2)  # x轴
    pygame.draw.line(screen, RED, (origin_x, 0), (origin_x, window_height), 2)  # y轴
    
    # 绘制刻度
    for x in range(0, window_width, grid_size):
        pygame.draw.line(screen, WHITE, (x, origin_y-5), (x, origin_y+5), 1)
        # 添加刻度值
        if x != origin_x:  # 不在原点绘制0
            value = (x - origin_x) / grid_size
            text = small_chinese_font.render(f"{value:.1f}", True, WHITE)
            screen.blit(text, (x - 10, origin_y + 10))
    
    for y in range(0, window_height, grid_size):
        pygame.draw.line(screen, WHITE, (origin_x-5, y), (origin_x+5, y), 1)
        # 添加刻度值
        if y != origin_y:  # 不在原点绘制0
            value = -(y - origin_y) / grid_size
            text = small_chinese_font.render(f"{value:.1f}", True, WHITE)
            screen.blit(text, (origin_x + 10, y - 10))

def draw_trails():
    """绘制鼠标和函数轨迹"""
    # 绘制鼠标轨迹（红色）
    if len(mouse_trail) > 1:
        # 分段绘制轨迹
        segment = []
        for point in mouse_trail:
            if point is None:
                # 遇到None时，绘制当前段并重新开始
                if len(segment) > 1:
                    pygame.draw.lines(screen, RED, False, segment, 2)
                segment = []
            else:
                segment.append(point)
        # 绘制最后一段
        if len(segment) > 1:
            pygame.draw.lines(screen, RED, False, segment, 2)
    
    # 绘制函数值轨迹（黄色）
    if len(function_trail) > 1:
        # 分段绘制轨迹
        segment = []
        for point in function_trail:
            if point is None:
                # 遇到None时，绘制当前段并重新开始
                if len(segment) > 1:
                    pygame.draw.lines(screen, YELLOW, False, segment, 2)
                segment = []
            else:
                segment.append(point)
        # 绘制最后一段
        if len(segment) > 1:
            pygame.draw.lines(screen, YELLOW, False, segment, 2)

def update_function_point(mouse_pos):
    """根据鼠标位置更新函数点"""
    global mouse_trail, function_trail
    
    # 将鼠标位置转换为复平面坐标
    z = mouse2Z(*mouse_pos)
    
    # 计算函数值
    f_z = complex_function(z)
    
    # 将函数值转换回屏幕坐标
    f_pos = z2mouse(f_z)
    
    # 添加到轨迹
    mouse_trail.append(mouse_pos)
    function_trail.append(f_pos)
    
    return f_pos

# 显示当前坐标信息
def show_coordinates(pos, z_value):
    """显示当前坐标信息"""
    text = chinese_font.render(f"位置: ({z_value.real:.2f}, {z_value.imag:.2f}i)", True, WHITE)
    screen.blit(text, (10, 10))
    
    # 显示函数值
    f_z = complex_function(z_value)
    text = chinese_font.render(f"函数值: ({f_z.real:.2f}, {f_z.imag:.2f}i)", True, YELLOW)
    screen.blit(text, (10, 40))

# 创建数学公式渲染函数
def render_math_formula(formula, size=16):
    """使用matplotlib渲染数学公式"""
    # 创建一个matplotlib图形
    fig = Figure(figsize=(3, 1), dpi=150)
    # 设置图形背景为黑色
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111)
    
    # 设置坐标区域背景为黑色
    ax.patch.set_facecolor('black')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # 渲染公式，使用白色文本
    ax.text(1.1, 0.5, formula, fontsize=size, ha='right', va='center', color='white')
    
    # 将图形转换为pygame表面
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    
    # 创建pygame表面
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    return surf

# 渲染数学公式
formula_surface = render_math_formula(func_str)

# 主循环
running = True
clock = pygame.time.Clock()
while running:
    # 填充黑色背景
    screen.fill(BLACK)
    
    # 绘制坐标系
    draw_coordinate_system()
    
    # 显示函数公式
    screen.blit(formula_surface, (window_width - formula_surface.get_width() - 20, 20))
    
    # 如果在跟踪模式下
    if tracking_mode:
        # 隐藏鼠标
        pygame.mouse.set_visible(False)
        
        # 处理键盘按键状态
        keys = pygame.key.get_pressed()
        
        # 保存旧的鼠标位置，用于检测是否有移动
        old_mouse_x, old_mouse_y = mouse_x, mouse_y
        
        # 根据按键更新鼠标位置
        if keys[pygame.K_w]:  # 上
            mouse_y -= move_speed
        if keys[pygame.K_s]:  # 下
            mouse_y += move_speed
        if keys[pygame.K_a]:  # 左
            mouse_x -= move_speed
        if keys[pygame.K_d]:  # 右
            mouse_x += move_speed
            
        # 确保鼠标位置不超出窗口范围
        mouse_x = max(0, min(window_width, mouse_x))
        mouse_y = max(0, min(window_height, mouse_y))
        
        # 如果鼠标位置有变化，则更新轨迹
        if old_mouse_x != mouse_x or old_mouse_y != mouse_y:
            # 设置鼠标位置
            pygame.mouse.set_pos(mouse_x, mouse_y)
            
            # 更新函数点
            f_pos = update_function_point((mouse_x, mouse_y))
            
            # 在当前鼠标位置绘制红色圆点
            pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 5)
            
            # 在函数值位置绘制黄色圆点
            pygame.draw.circle(screen, YELLOW, f_pos, 5)
        
        # 绘制轨迹
        draw_trails()
        
        # 显示当前坐标信息
        show_coordinates((mouse_x, mouse_y), mouse2Z(mouse_x, mouse_y))
    else:
        # 显示鼠标
        pygame.mouse.set_visible(True)
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 在鼠标位置绘制红色圆点
        pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 5)
        
        # 显示当前坐标信息
        show_coordinates((mouse_x, mouse_y), mouse2Z(mouse_x, mouse_y))
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC键清除轨迹，不退出程序
                mouse_trail = []
                function_trail = []
            elif event.key == pygame.K_c:  # C键清除轨迹
                mouse_trail = []
                function_trail = []
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 鼠标左键
                # 进入跟踪模式
                tracking_mode = True
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 如果需要开始新的轨迹段
                if new_trail_segment:
                    # 不清除现有轨迹，而是添加None作为分隔符
                    # 确保在添加新点之前添加分隔符，防止连接到上一段轨迹
                    if mouse_trail and function_trail:
                        mouse_trail.append(None)
                        function_trail.append(None)
                    
                    # 添加新的起始点
                    mouse_trail.append((mouse_x, mouse_y))
                    
                    # 计算初始函数值
                    z = mouse2Z(mouse_x, mouse_y)
                    f_z = complex_function(z)
                    f_pos = z2mouse(f_z)
                    function_trail.append(f_pos)
                    
                    # 重置标志
                    new_trail_segment = False
                else:
                    # 继续现有轨迹
                    f_pos = update_function_point((mouse_x, mouse_y))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 鼠标左键释放
                # 继续保持跟踪模式，不清除轨迹
                # 设置标志，下次点击时开始新的轨迹段
                new_trail_segment = True
        elif event.type == pygame.MOUSEMOTION and tracking_mode:
            # 在跟踪模式下，鼠标移动时更新轨迹
            # 在跟踪模式下，鼠标移动时更新轨迹
            mouse_x, mouse_y = event.pos
            
            # 如果需要开始新的轨迹段，先添加分隔符
            if new_trail_segment and mouse_trail and function_trail:
                mouse_trail.append(None)
                function_trail.append(None)
                new_trail_segment = False
                
            f_pos = update_function_point((mouse_x, mouse_y))
            
            # 在当前鼠标位置绘制红色圆点
            pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 5)
            
            # 在函数值位置绘制黄色圆点
            pygame.draw.circle(screen, YELLOW, f_pos, 5)
    
    # 更新显示
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)

# 退出pygame
pygame.quit()
sys.exit()