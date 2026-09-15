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
