import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.cm import viridis, cividis, rainbow

# 复数函数定义
def complex_function(z):
    # 实现与显示公式一致的函数：z^3/2
    x = np.real(z)
    y = np.imag(z)
    f = complex(x+y, x**2+y**2)
    # f = np.sinh(z)
    return f

func_str = f"$f(z)=x+y+(x^2+y^2)i$"

# 设置窗口大小和标题
window_width = 1200
window_height = 800
grid_size = 200
move_speed = 2  # 增加移动速度以便更明显地看到效果

# 导数模式设置
RING_RADIUS = 24    # 圆环半径
RING_WIDTH = 10     # 圆环宽度
num_segments = 360 # 将导数圆环分为180段，每段2度

# 数值微分设置
EPSILON = 1e-4  # 用于数值微分的小增量


# 使用数值微分计算导数
def numerical_derivative(z):
    """使用数值微分计算复数函数在点z处的导数
    返回一个列表，包含不同方向上的导数值
    """
    # 创建一个列表来存储各个方向的导数值
    derivatives = []
    
    # 对num_segments个不同辐角的dz进行计算
    for i in range(num_segments):
        # 计算当前dz的辐角（弧度）
        dz_angle = 2 * np.pi * i / num_segments
        
        # 根据辐角和绝对值计算dz
        dz = EPSILON * complex(np.cos(dz_angle), np.sin(dz_angle))
        
        # 计算该方向上的函数值差异
        try:
            df = complex_function(z + dz) - complex_function(z)
            derivative = df / dz
            derivatives.append((dz_angle, derivative))
        except Exception:
            # 如果计算出错（例如函数在该点不可导），则跳过该方向
            continue

    # 如果所有方向都计算失败，返回空列表
    if not derivatives:
        return []
    
    # 返回所有方向的导数值列表，每个元素是(角度,导数值)的元组
    return derivatives
    

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

# 导数模式标志
derivative_mode = False

# 存储当前显示的圆环信息列表
ring_info_list = []

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
def show_coordinates(pos, z_value, show_derivative=False):
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
    # 使用buffer_rgba代替已弃用的tostring_rgb
    raw_data = renderer.buffer_rgba()
    # 将memoryview对象转换为bytes对象
    raw_data = bytes(raw_data)
    size = canvas.get_width_height()
    
    # 创建pygame表面，注意使用RGBA格式而不是RGB
    surf = pygame.image.fromstring(raw_data, size, "RGBA")
    return surf

# 渲染数学公式
formula_surface = render_math_formula(func_str)

# 绘制dz圆环函数
def draw_dz_ring(x, y):
    """在指定位置绘制表示dz的彩色圆环"""
    # 圆环的角度范围：0-360度
    for i in range(num_segments):
        # 计算当前段的起始和结束角度（弧度）
        start_angle = 2 * np.pi * i / num_segments
        end_angle = 2 * np.pi * (i + 1) / num_segments
        
        # 计算颜色（使用viridis色彩映射）
        color_val = i / num_segments
        color = tuple(int(c * 255) for c in viridis(color_val)[:3])
        
        # 绘制圆弧段
        pygame.draw.arc(screen, color, 
                        [x - RING_RADIUS, y - RING_RADIUS, 
                         2 * RING_RADIUS, 2 * RING_RADIUS], 
                        start_angle, end_angle, RING_WIDTH)

# 绘制df变形环函数
def draw_df_ring(x, y, df_derivatives):
    """在指定位置绘制表示df的变形环
    df_derivatives: 包含多个方向导数值的列表，每个元素是(角度,导数值)的元组
    """
    # 遍历每个方向的导数值
    for dz_angle, df_z in df_derivatives:
        # 获取当前方向导数的模和辐角
        df_abs = abs(df_z)
        df_angle = np.angle(df_z)
        
        # 计算对应的df角度（弧度）
        # df的角度 = dz的角度 + 导数的辐角
        df_segment_angle = dz_angle + df_angle
        
        # 计算颜色（使用viridis色彩映射，使用df角度索引）
        # 将df_segment_angle归一化到[0, 1]范围内来选择颜色
        color_val = (dz_angle % (2 * np.pi)) / (2 * np.pi)  # 保持与dz环相同的颜色映射
        color = tuple(int(c * 255) for c in rainbow(color_val)[:3])
        
        # 计算变形环上的点
        # 半径根据导数的模进行缩放
        radius = RING_RADIUS * df_abs
        # 计算当前段的起始和结束点
        segment_width = 2 * np.pi / num_segments
        start_x = x + radius * np.cos(df_segment_angle - segment_width/2)
        start_y = y - radius * np.sin(df_segment_angle - segment_width/2)
        end_x = x + radius * np.cos(df_segment_angle + segment_width/2)
        end_y = y - radius * np.sin(df_segment_angle + segment_width/2)
        
        # 绘制弧段（由于可能不是圆形，所以使用线段代替弧）
        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), RING_WIDTH)

# 主循环
running = True
clock = pygame.time.Clock()
while running:
    # 填充黑色背景
    screen.fill(BLACK)
    
    # 绘制坐标系
    draw_coordinate_system()
    
    # 显示函数公式 - 始终只显示原始函数公式
    screen.blit(formula_surface, (window_width - formula_surface.get_width() - 20, 20))
    
    # 绘制导数模式下的彩色圆环
    if derivative_mode:
        # 显示鼠标
        pygame.mouse.set_visible(True)
        
        # 获取鼠标位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 在鼠标位置绘制红色圆点
        pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 5)
        
        # 显示当前坐标信息（包括导数）
        show_coordinates((mouse_x, mouse_y), mouse2Z(mouse_x, mouse_y), True)
        
        # 如果有已保存的圆环信息，则绘制所有圆环
        for ring_info in ring_info_list:
            input_pos, output_pos, df_z = ring_info
            draw_dz_ring(*input_pos)
            draw_df_ring(*output_pos, df_z)
    # 如果在跟踪模式下
    elif tracking_mode:
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
                ring_info_list = []  # 清除所有圆环信息
            elif event.key == pygame.K_c:  # C键清除轨迹
                mouse_trail = []
                function_trail = []
                ring_info_list = []  # 清除所有圆环信息
            elif event.key == pygame.K_p:  # P键切换导数模式
                derivative_mode = not derivative_mode
                # 清除轨迹
                mouse_trail = []
                function_trail = []
                ring_info_list = []  # 清除所有圆环信息
                # 如果进入导数模式，退出跟踪模式
                if derivative_mode:
                    tracking_mode = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 鼠标左键
                if derivative_mode:
                    # 在导数模式下，绘制彩色圆环
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    z = mouse2Z(mouse_x, mouse_y)
                    
                    # 计算导数 - 使用数值微分，获取多个方向的导数值
                    df_derivatives = numerical_derivative(z)
                    
                    # 计算函数值位置
                    f_z = complex_function(z)
                    f_pos_x, f_pos_y = z2mouse(f_z)
                    
                    # 保存圆环信息到列表中，不再覆盖之前的圆环
                    ring_info_list.append(((mouse_x, mouse_y), (f_pos_x, f_pos_y), df_derivatives))
                else:
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