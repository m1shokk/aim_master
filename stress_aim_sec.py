import pygame
import random
import math
import sys
import os
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if os.name == 'nt':
    os.system('chcp 65001 > nul')

pygame.init()

screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Stress Aim Mode")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 50)
GRAY = (180, 180, 200)
RED = (255, 80, 80)
PINK = (255, 120, 200)

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

ROUNDS_PER_MATCH = 5
RED_BALLS_RANGE = (3, 5)
PINK_BALLS_RANGE = (1, 2)
BALL_RADIUS = 32
BALL_LIFETIME = 2.0  # seconds
BALL_FADE_TIME = 0.5  # seconds (last part of lifetime is fade)
MARGIN = 100

class Ball:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.spawn_time = pygame.time.get_ticks() / 1000.0
        self.clicked = False
        self.alpha = 255
        self.fading = False

    def update(self, now):
        elapsed = now - self.spawn_time
        if elapsed > BALL_LIFETIME - BALL_FADE_TIME:
            self.fading = True
            fade_elapsed = elapsed - (BALL_LIFETIME - BALL_FADE_TIME)
            self.alpha = max(0, 255 - int(255 * (fade_elapsed / BALL_FADE_TIME)))
        if elapsed > BALL_LIFETIME:
            return False  # Ball should disappear
        return True

    def draw(self, surface):
        ball_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        color = self.color + (self.alpha,)
        pygame.draw.circle(ball_surf, color, (self.radius, self.radius), self.radius)
        surface.blit(ball_surf, (self.x - self.radius, self.y - self.radius))

    def is_hovered(self, mx, my):
        return math.hypot(mx - self.x, my - self.y) <= self.radius

def draw_grid():
    grid_size = 50
    for x in range(0, screen_width, grid_size):
        pygame.draw.line(screen, (60, 60, 70), (x, 0), (x, screen_height), 1)
    for y in range(0, screen_height, grid_size):
        pygame.draw.line(screen, (60, 60, 70), (0, y), (screen_width, y), 1)

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {'sensitivity': 1.66, 'crosshair_color': (255, 255, 255)}
        save_settings(settings)
    return settings

def save_settings(settings):
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def back_to_menu():
    os.execv(sys.executable, ['python'] + ['game_select.py'])

def spawn_balls():
    balls = []
    # Красные
    red_count = random.randint(*RED_BALLS_RANGE)
    for _ in range(red_count):
        x, y = get_random_pos()
        balls.append(Ball(RED, x, y))
    # Розовые (иногда)
    if random.random() < 0.7:  # 70% шанс появления розовых
        pink_count = random.randint(*PINK_BALLS_RANGE)
        for _ in range(pink_count):
            x, y = get_random_pos()
            balls.append(Ball(PINK, x, y))
    random.shuffle(balls)
    return balls

def get_random_pos():
    x = random.randint(MARGIN, screen_width - MARGIN)
    y = random.randint(MARGIN, screen_height - MARGIN)
    return x, y

def display_round_info(round_num, wins, fails):
    text = f"Round: {round_num+1}/5  |  Wins: {wins}  |  Fails: {fails}"
    surface = small_font.render(text, True, WHITE)
    screen.blit(surface, (20, 20))

def display_final_stats(wins, fails):
    screen.fill(DARK_GRAY)
    title = font.render("Stress Aim Results", True, WHITE)
    screen.blit(title, (screen_width//2 - title.get_width()//2, screen_height//2 - 150))
    res = font.render(f"Wins: {wins} out of 5", True, (0, 220, 140) if wins >= 3 else RED)
    screen.blit(res, (screen_width//2 - res.get_width()//2, screen_height//2 - 50))
    info = small_font.render("ESC - menu, R - restart", True, GRAY)
    screen.blit(info, (screen_width//2 - info.get_width()//2, screen_height//2 + 50))

def stress_aim_game():
    settings = load_settings()
    clock = pygame.time.Clock()
    round_num = 0
    wins = 0
    fails = 0
    state = "playing"
    balls = []
    red_left = 0
    round_failed = False
    round_start_time = 0

    # Время исчезновения зависит от сложности
    difficulty = settings.get('difficulty', 'medium')
    if difficulty == 'easy':
        ball_lifetime = 4.0
    elif difficulty == 'hard':
        ball_lifetime = 2.0
    else:
        ball_lifetime = 3.0
    global BALL_LIFETIME
    BALL_LIFETIME = ball_lifetime

    def start_round():
        nonlocal balls, red_left, round_failed, round_start_time
        balls = spawn_balls()
        red_left = sum(1 for b in balls if b.color == RED)
        round_failed = False
        round_start_time = pygame.time.get_ticks() / 1000.0

    def finish_round(success):
        nonlocal round_num, wins, fails, state
        if success:
            wins += 1
        else:
            fails += 1
        round_num += 1
        if round_num >= ROUNDS_PER_MATCH:
            state = "finished"
        else:
            start_round()

    start_round()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        now = pygame.time.get_ticks() / 1000.0
        screen.fill(DARK_GRAY)
        draw_grid()

        if state == "playing":
            display_round_info(round_num, wins, fails)
            # Update balls
            for ball in balls[:]:
                alive = ball.update(now)
                if not alive and not ball.clicked and ball.color == RED:
                    round_failed = True
                if not alive:
                    balls.remove(ball)
            # Draw balls
            for ball in balls:
                ball.draw(screen)
            # Check lose
            if round_failed:
                finish_round(False)
            # Check win
            if red_left == 0 and not round_failed:
                finish_round(True)
        elif state == "finished":
            display_final_stats(wins, fails)

        # Курсор
        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(screen, settings['crosshair_color'], (mx, my), 5)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back_to_menu()
                elif event.key == pygame.K_r:
                    round_num = 0
                    wins = 0
                    fails = 0
                    state = "playing"
                    start_round()
            elif event.type == pygame.MOUSEBUTTONDOWN and state == "playing":
                for ball in balls:
                    if ball.is_hovered(mx, my):
                        if ball.color == RED:
                            if not ball.clicked:
                                ball.clicked = True
                                balls.remove(ball)
                                red_left -= 1
                        elif ball.color == PINK:
                            round_failed = True
                        break
                else:
                    # Клик мимо любого шара
                    round_failed = True
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    stress_aim_game() 