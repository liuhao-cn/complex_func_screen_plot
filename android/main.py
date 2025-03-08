from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, StringProperty

import numpy as np
from functools import partial

# 复数函数定义
def complex_function(z):
    # 实现与显示公式一致的函数
    x = np.real(z)
    y = np.imag(z)
    f = complex(x+y, x**2+y**2)
    return f

# 数值微分设置
DZ_EPSILON = 1e-4  # 用于数值微分的小增量
num_segments = 720  # 将导数圆环分为720段，每段0.5度

# 使用数值微分计算导数
def numerical_derivative(z):
    """使用数值微分计算复数函数在点z处的导数
    返回一个列表，包含不同方向上的导数值
    """
    # 创建一个列表来存储各个方向的导数值
    derivatives = []
    
    # 设置dz的绝对值
    dz_abs = DZ_EPSILON
    
    # 对num_segments个不同辐角的dz进行计算
    for i in range(num_segments):
        # 计算当前dz的辐角（弧度）
        dz_angle = 2 * np.pi * i / num_segments
        
        # 根据辐角和绝对值计算dz
        dz = complex(dz_abs * np.cos(dz_angle), dz_abs * np.sin(dz_angle))
        
        # 计算该方向上的函数值差异
        try:
            df = complex_function(z + dz) - complex_function(z)
            # 计算导数（df/dz）
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

# 坐标转换类
class CoordinateConverter:
    def __init__(self, grid_size=100):
        self.grid_size = grid_size
        self.update_origin()
    
    def update_origin(self):
        # 坐标轴原点(窗口中心)
        self.origin_x = Window.width // 2
        self.origin_y = Window.height // 2
    
    def touch_to_z(self, touch_x, touch_y):
        """将触摸坐标转换为复平面坐标"""
        return complex((touch_x - self.origin_x) / self.grid_size, 
                      -(touch_y - self.origin_y) / self.grid_size)
    
    def z_to_screen(self, z):
        """将复平面坐标转换为屏幕坐标"""
        return (int(z.real * self.grid_size) + self.origin_x, 
                int(-z.imag * self.grid_size) + self.origin_y)

# 复数平面绘图区域
class ComplexPlane(Widget):
    derivative_mode = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(ComplexPlane, self).__init__(**kwargs)
        self.converter = CoordinateConverter(grid_size=100)
        
        # 轨迹点列表
        self.input_trail = []
        self.output_trail = []
        self.new_trail_segment = True
        
        # 导数模式设置
        self.ring_radius = dp(24)  # 圆环半径
        self.ring_width = dp(3)    # 圆环宽度
        self.ring_info_list = []   # 存储圆环信息
        
        # 当前触摸点
        self.current_touch = None
        
        # 绑定窗口大小变化事件
        Window.bind(on_resize=self.on_window_resize)
        
        # 设置刷新
        Clock.schedule_interval(self.update, 1/30)  # 30 FPS
    
    def on_window_resize(self, instance, width, height):
        self.converter.update_origin()
        self.canvas.clear()
    
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.current_touch = touch
            
            if self.derivative_mode:
                # 在导数模式下，添加导数环
                z = self.converter.touch_to_z(touch.x, touch.y)
                
                # 计算导数
                df_derivatives = numerical_derivative(z)
                
                # 计算函数值位置
                f_z = complex_function(z)
                f_pos_x, f_pos_y = self.converter.z_to_screen(f_z)
                
                # 保存圆环信息
                self.ring_info_list.append(((touch.x, touch.y), 
                                          (f_pos_x, f_pos_y), 
                                          df_derivatives))
            else:
                # 开始新的轨迹段
                if self.new_trail_segment:
                    if self.input_trail and self.output_trail:
                        self.input_trail.append(None)
                        self.output_trail.append(None)
                    
                    # 添加新的起始点
                    self.input_trail.append((touch.x, touch.y))
                    
                    # 计算函数值
                    z = self.converter.touch_to_z(touch.x, touch.y)
                    f_z = complex_function(z)
                    f_pos = self.converter.z_to_screen(f_z)
                    self.output_trail.append(f_pos)
                    
                    self.new_trail_segment = False
                else:
                    # 继续现有轨迹
                    self.update_function_point(touch.x, touch.y)
            
            return True
        return super(ComplexPlane, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if touch == self.current_touch and not self.derivative_mode:
            # 更新轨迹
            self.update_function_point(touch.x, touch.y)
            return True
        return super(ComplexPlane, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if touch == self.current_touch:
            self.current_touch = None
            self.new_trail_segment = True
            return True
        return super(ComplexPlane, self).on_touch_up(touch)
    
    def update_function_point(self, x, y):
        """根据触摸位置更新函数点"""
        # 将触摸位置转换为复平面坐标
        z = self.converter.touch_to_z(x, y)
        
        # 计算函数值
        f_z = complex_function(z)
        
        # 将函数值转换回屏幕坐标
        f_pos = self.converter.z_to_screen(f_z)
        
        # 添加到轨迹
        self.input_trail.append((x, y))
        self.output_trail.append(f_pos)
        
        return f_pos
    
    def clear_trails(self):
        """清除所有轨迹"""
        self.input_trail = []
        self.output_trail = []
        self.ring_info_list = []
    
    def toggle_derivative_mode(self):
        """切换导数模式"""
        self.derivative_mode = not self.derivative_mode
        self.clear_trails()
    
    def update(self, dt):
        # 重绘画布
        self.canvas.clear()
        
        with self.canvas:
            # 绘制坐标系
            self.draw_coordinate_system()
            
            # 绘制轨迹
            self.draw_trails()
            
            # 绘制导数环
            if self.derivative_mode:
                for ring_info in self.ring_info_list:
                    input_pos, output_pos, df_z = ring_info
                    self.draw_dz_ring(*input_pos)
                    self.draw_df_ring(*output_pos, df_z)
            
            # 绘制当前点
            if self.current_touch:
                # 在当前触摸位置绘制红色圆点
                Color(1, 0, 0)
                Ellipse(pos=(self.current_touch.x - dp(5), self.current_touch.y - dp(5)), 
                        size=(dp(10), dp(10)))
                
                # 计算并绘制函数值点
                z = self.converter.touch_to_z(self.current_touch.x, self.current_touch.y)
                f_z = complex_function(z)
                f_pos_x, f_pos_y = self.converter.z_to_screen(f_z)
                
                Color(1, 1, 0)
                Ellipse(pos=(f_pos_x - dp(5), f_pos_y - dp(5)), 
                        size=(dp(10), dp(10)))
    
    def draw_coordinate_system(self):
        """绘制坐标系"""
        # 绘制坐标轴
        Color(1, 0, 0)  # 红色
        Line(points=[0, self.converter.origin_y, Window.width, self.converter.origin_y], width=1)  # x轴
        Line(points=[self.converter.origin_x, 0, self.converter.origin_x, Window.height], width=1)  # y轴
        
        # 绘制刻度
        Color(1, 1, 1)  # 白色
        grid_size = self.converter.grid_size
        origin_x = self.converter.origin_x
        origin_y = self.converter.origin_y
        
        # X轴刻度
        for x in range(0, int(Window.width), grid_size):
            Line(points=[x, origin_y-5, x, origin_y+5], width=1)
        
        # Y轴刻度
        for y in range(0, int(Window.height), grid_size):
            Line(points=[origin_x-5, y, origin_x+5, y], width=1)
    
    def draw_trails(self):
        """绘制轨迹"""
        # 绘制输入轨迹（红色）
        if len(self.input_trail) > 1:
            segment = []
            for point in self.input_trail:
                if point is None:
                    # 遇到None时，绘制当前段并重新开始
                    if len(segment) > 1:
                        Color(1, 0, 0)  # 红色
                        Line(points=segment, width=2)
                    segment = []
                else:
                    segment.extend([point[0], point[1]])
            # 绘制最后一段
            if len(segment) > 1:
                Color(1, 0, 0)  # 红色
                Line(points=segment, width=2)
        
        # 绘制函数值轨迹（黄色）
        if len(self.output_trail) > 1:
            segment = []
            for point in self.output_trail:
                if point is None:
                    # 遇到None时，绘制当前段并重新开始
                    if len(segment) > 1:
                        Color(1, 1, 0)  # 黄色
                        Line(points=segment, width=2)
                    segment = []
                else:
                    segment.extend([point[0], point[1]])
            # 绘制最后一段
            if len(segment) > 1:
                Color(1, 1, 0)  # 黄色
                Line(points=segment, width=2)
    
    def draw_dz_ring(self, x, y):
        """在指定位置绘制表示dz的彩色圆环"""
        # 圆环的角度范围：0-360度
        for i in range(0, num_segments, 10):  # 减少段数以提高性能
            # 计算当前段的起始和结束角度（弧度）
            start_angle = 2 * np.pi * i / num_segments
            end_angle = 2 * np.pi * (i + 10) / num_segments
            
            # 计算颜色（使用HSV色彩空间）
            h = i / num_segments  # 色相
            r, g, b = self.hsv_to_rgb(h, 1, 1)
            
            # 绘制圆弧段
            Color(r, g, b)
            Line(circle=(x, y, self.ring_radius, start_angle, end_angle), width=self.ring_width)
    
    def draw_df_ring(self, x, y, df_derivatives):
        """在指定位置绘制表示df的变形环"""
        # 遍历每个方向的导数值
        for dz_angle, df_z in df_derivatives:
            # 获取当前方向导数的模和辐角
            df_abs = abs(df_z)
            df_angle = np.angle(df_z)
            
            # 计算对应的df角度（弧度）
            df_segment_angle = dz_angle + df_angle
            
            # 计算颜色（使用HSV色彩空间）
            h = (dz_angle % (2 * np.pi)) / (2 * np.pi)  # 保持与dz环相同的颜色映射
            r, g, b = self.hsv_to_rgb(h, 1, 1)
            
            # 计算变形环上的点
            radius = self.ring_radius * df_abs
            segment_width = 2 * np.pi / num_segments
            
            # 计算当前段的起始和结束点
            start_x = x + radius * np.cos(df_segment_angle - segment_width/2)
            start_y = y - radius * np.sin(df_segment_angle - segment_width/2)
            end_x = x + radius * np.cos(df_segment_angle + segment_width/2)
            end_y = y - radius * np.sin(df_segment_angle + segment_width/2)
            
            # 绘制弧段
            Color(r, g, b)
            Line(points=[start_x, start_y, end_x, end_y], width=self.ring_width)
    
    def hsv_to_rgb(self, h, s, v):
        """将HSV颜色转换为RGB颜色"""
        if s == 0.0:
            return v, v, v
        
        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        i %= 6
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        else:
            return v, p, q


# 主应用类
class ComplexFuncApp(App):
    func_expr = StringProperty("f(z)=x+y+(x²+y²)i")
    
    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')
        
        # 创建顶部信息栏
        info_bar = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(10), 0])
        
        # 添加函数表达式标签
        func_label = Label(
            text=self.func_expr,
            size_hint_x=None,
            width=dp(200),
            color=(1, 1, 0, 1)
        )
        info_bar.add_widget(func_label)
        
        # 添加坐标信息标签（将在更新时填充）
        self.coord_label = Label(
            text="位置: (0.00, 0.00i)\n函数值: (0.00, 0.00i)",
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        self.coord_label.bind(size=self.coord_label.setter('text_size'))
        info_bar.add_widget(self.coord_label)
        
        # 创建复平面绘图区域
        self.complex_plane = ComplexPlane()
        
        # 创建底部按钮栏
        button_bar = BoxLayout(size_hint_y=None, height=dp(50))
        
        # 添加清除按钮
        clear_button = Button(
            text="清除",
            on_press=lambda x: self.complex_plane.clear_trails()
        )
        button_bar.add_widget(clear_button)
        
        # 添加导数模式切换按钮
        derivative_button = Button(
            text="导数模式",
            on_press=lambda x: self.complex_plane.toggle_derivative_mode()
        )
        button_bar.add_widget(derivative_button)
        
        # 组装布局
        layout.add_widget(info_bar)
        layout.add_widget(self.complex_plane)
        layout.add_widget(button_bar)
        
        # 设置更新回调
        Clock.schedule_interval(self.update_coord_info, 1/10)  # 10 FPS更新坐标信息
        
        return layout
    
    def update_coord_info(self, dt):
        """更新坐标信息显示"""
        if self.complex_plane.current_touch:
            # 获取当前触摸点的复平面坐标
            touch = self.complex_plane.current_touch
            z = self.complex_plane.converter.touch_to_z(touch.x, touch.y)
            
            # 计算函数值
            f_z = complex_function(z)
            
            # 更新坐标信息标签
            self.coord_label.text = f"位置: ({z.real:.2f}, {z.imag:.2f}i)\n函数值: ({f_z.real:.2f}, {f_z.imag:.2f}i)"


# 运行应用
if __name__ == "__main__":
    ComplexFuncApp().run()