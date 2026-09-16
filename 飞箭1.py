import pygame
import sys
import random
import os

# ===================== 1. 初始化与常量定义 =====================
pygame.init()

# 窗口配置
WIDTH, HEIGHT = 800, 650
CELL_SIZE = 60       # 单个格子像素大小
GRID_SIZE = 5        # 5×5棋盘网格
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 60, 60)
GREEN = (0, 180, 0)
BLUE = (30, 144, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (100, 100, 100)

# 方向常量
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

# 游戏状态
STATE_START = 0   # 开始界面
STATE_PLAYING = 1 # 游戏进行中
STATE_WIN = 2     # 全部通关
STATE_LOSE = 3    # 本关失败

# 棋盘居中偏移
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 120

# 中文字体加载：直接读取系统字体文件
def get_font(size):
    font_path = "C:/Windows/Fonts/simhei.ttf"
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    else:
        return pygame.font.Font(None, size)


# ===================== 2. 箭头类 =====================
class Arrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.active = True      # 是否仍在棋盘上
        self.flying = False     # 是否正在飞出
        self.shake_time = 0     # 碰撞抖动计时
        self.fly_speed = 8      # 飞出动画速度
        self.x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        self.y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.color = BLUE

    def get_rect(self):
        """获取箭头的点击碰撞区域"""
        x = GRID_OFFSET_X + self.col * CELL_SIZE
        y = GRID_OFFSET_Y + self.row * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def update(self):
        """更新箭头状态（飞出动画、抖动动画）"""
        # 飞出动画：沿方向移动
        if self.flying:
            if self.direction == UP:
                self.y -= self.fly_speed
            elif self.direction == DOWN:
                self.y += self.fly_speed
            elif self.direction == LEFT:
                self.x -= self.fly_speed
            elif self.direction == RIGHT:
                self.x += self.fly_speed
            
            # 飞出屏幕外则标记为消除
            if (self.y < -CELL_SIZE or self.y > HEIGHT + CELL_SIZE or
                self.x < -CELL_SIZE or self.x > WIDTH + CELL_SIZE):
                self.active = False

        # 碰撞抖动动画：闪烁+左右抖动
        if self.shake_time > 0:
            self.shake_time -= 1
            self.color = RED if self.shake_time % 10 < 5 else BLUE
            # 抖动结束后，强制恢复为蓝色
            if self.shake_time <= 0:
                self.color = BLUE

    def draw(self, screen):
        """绘制箭头（三角形）"""
        if not self.active:
            return
        
        # 抖动偏移量
        offset_x = random.randint(-3, 3) if self.shake_time > 0 else 0
        center_x = self.x + offset_x
        center_y = self.y
        size = CELL_SIZE // 3

        # 根据方向生成三角形顶点
        if self.direction == UP:
            points = [(center_x, center_y - size),
                      (center_x - size, center_y + size),
                      (center_x + size, center_y + size)]
        elif self.direction == DOWN:
            points = [(center_x, center_y + size),
                      (center_x - size, center_y - size),
                      (center_x + size, center_y - size)]
        elif self.direction == LEFT:
            points = [(center_x - size, center_y),
                      (center_x + size, center_y - size),
                      (center_x + size, center_y + size)]
        else: # RIGHT
            points = [(center_x + size, center_y),
                      (center_x - size, center_y - size),
                      (center_x - size, center_y + size)]
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, BLACK, points, 2)

    def start_fly(self):
        """触发飞出动画"""
        self.flying = True

    def shake(self):
        """触发碰撞反馈"""
        self.shake_time = 30

