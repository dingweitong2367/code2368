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


# ===================== 3. 游戏主类 =====================
class ArrowGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭 - 箭头解谜游戏")
        self.clock = pygame.time.Clock()
        self.font = get_font(36)
        self.big_font = get_font(72)
        
        self.state = STATE_START
        self.current_level = 0
        self.max_mistakes = 3    # 每关3次失误机会
        self.mistakes_left = self.max_mistakes
        self.arrows = []
        
        # 3个可通关关卡（难度递增，均有合理消除顺序）
        self.levels = [
            # 第1关：入门级
            [
                (0, 4, UP),
                (2, 3, RIGHT),
                (2, 1, RIGHT),
                (4, 2, DOWN),
                (1, 0, LEFT)
            ],
            # 第2关：进阶级
            [
                (0, 2, DOWN),
                (2, 2, DOWN),
                (4, 2, DOWN),
                (3, 1, LEFT),
                (3, 4, LEFT),
                (1, 0, UP)
            ],
            # 第3关：挑战级
            [
                (0, 1, DOWN),
                (2, 1, DOWN),
                (4, 1, DOWN),
                (4, 3, UP),
                (2, 3, UP),
                (0, 3, UP),
                (1, 0, RIGHT),
                (1, 2, RIGHT),
                (3, 4, LEFT),
                (3, 2, LEFT)
            ]
        ]

        # 游戏内重新开始按钮
        self.restart_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT - 80, 160, 50)
        # 失败界面按钮
        self.lose_restart_btn = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 60, 220, 55)
        self.lose_back_btn = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 130, 220, 55)

    def load_level(self, level_index):
        """加载指定关卡，重置所有状态"""
        self.arrows = []
        self.mistakes_left = self.max_mistakes
        level_data = self.levels[level_index]
        for row, col, direction in level_data:
            self.arrows.append(Arrow(row, col, direction))

    def check_path(self, arrow):
        """核心逻辑：检查箭头前进方向是否有阻挡
        返回True表示路径畅通，可以飞出
        """
        active_arrows = [a for a in self.arrows 
                         if a.active and not a.flying and a != arrow]
        
        if arrow.direction == RIGHT:
            for a in active_arrows:
                if a.row == arrow.row and a.col > arrow.col:
                    return False
            return True
        elif arrow.direction == LEFT:
            for a in active_arrows:
                if a.row == arrow.row and a.col < arrow.col:
                    return False
            return True
        elif arrow.direction == UP:
            for a in active_arrows:
                if a.col == arrow.col and a.row < arrow.row:
                    return False
            return True
        elif arrow.direction == DOWN:
            for a in active_arrows:
                if a.col == arrow.col and a.row > arrow.row:
                    return False
            return True
        return False

    def handle_click(self, pos):
        """处理鼠标左键点击"""
        if self.state == STATE_START:
            start_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 60)
            if start_btn.collidepoint(pos):
                self.state = STATE_PLAYING
                self.current_level = 0
                self.load_level(0)
            return

        if self.state == STATE_WIN:
            # 通关界面点击返回开始
            self.state = STATE_START
            return

        if self.state == STATE_LOSE:
            # 失败界面：重新开始本关
            if self.lose_restart_btn.collidepoint(pos):
                self.load_level(self.current_level)
                self.state = STATE_PLAYING
            # 失败界面：返回主菜单
            elif self.lose_back_btn.collidepoint(pos):
                self.state = STATE_START
            return

        if self.state == STATE_PLAYING:
            # 点击重新开始按钮
            if self.restart_btn.collidepoint(pos):
                self.load_level(self.current_level)
                return

            # 点击箭头
            for arrow in self.arrows:
                if arrow.active and not arrow.flying and arrow.get_rect().collidepoint(pos):
                    if self.check_path(arrow):
                        arrow.start_fly()
                    else:
                        arrow.shake()
                        self.mistakes_left -= 1
                        if self.mistakes_left <= 0:
                            self.state = STATE_LOSE
                    break

    def check_win(self):
        """检查本关是否通关，通关则进入下一关"""
        active_count = len([a for a in self.arrows if a.active])
        if active_count == 0:
            if self.current_level < len(self.levels) - 1:
                self.current_level += 1
                self.load_level(self.current_level)
            else:
                self.state = STATE_WIN

    def update(self):
        """更新游戏每一帧的状态"""
        if self.state == STATE_PLAYING:
            for arrow in self.arrows:
                arrow.update()
            self.check_win()

    def draw_grid(self):
        """绘制棋盘网格线"""
        for i in range(GRID_SIZE + 1):
            x = GRID_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(self.screen, GRAY, 
                            (x, GRID_OFFSET_Y), 
                            (x, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE), 2)
            y = GRID_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, GRAY, 
                            (GRID_OFFSET_X, y), 
                            (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, y), 2)

    def draw_ui(self):
        """绘制游戏界面的UI信息"""
        title_text = self.big_font.render("一箭又一箭", True, BLACK)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))

        level_text = self.font.render(f"关卡: {self.current_level + 1}/{len(self.levels)}", True, BLACK)
        self.screen.blit(level_text, (50, 80))

        arrow_count = len([a for a in self.arrows if a.active])
        count_text = self.font.render(f"剩余箭头: {arrow_count}", True, BLACK)
        self.screen.blit(count_text, (50, 120))

        mistake_text = self.font.render(f"剩余失误: {self.mistakes_left}/{self.max_mistakes}", True, RED)
        self.screen.blit(mistake_text, (WIDTH - 250, 80))

        # 重新开始按钮
        pygame.draw.rect(self.screen, LIGHT_BLUE, self.restart_btn, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, self.restart_btn, 2, border_radius=10)
        btn_text = self.font.render("重新开始", True, BLACK)
        self.screen.blit(btn_text, (self.restart_btn.centerx - btn_text.get_width()//2, 
                                      self.restart_btn.centery - btn_text.get_height()//2))
