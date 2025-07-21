import pygame
import json
import sys
import os
import io
import random
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if os.name == 'nt':
    os.system('chcp 65001 > nul')

pygame.init()

screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Tracking Trainer")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 50)
GRAY = (180, 180, 200)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (128, 0, 128)
GREEN = (0, 200, 120)
RED = (255, 80, 80)

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Настройки игры
GAME_DURATION = 30  # секунд
TARGET_RADIUS = 25
MARGIN = 80  # отступ от краёв экрана
BASE_SPEED = 2.0
SPEED_VARIATION = 0.8
SPEED_CHANGE_INTERVAL = 0.5  # секунды

def draw_grid():
    grid_size = 50
    for x in range(0, screen_width, grid_size):
        pygame.draw.line(screen, (60, 60, 70), (x, 0), (x, screen_height), 1)
    for y in range(0, screen_height, grid_size):
        pygame.draw.line(screen, (60, 60, 70), (0, y), (screen_width, y), 1)

def display_timer_and_tracking_time(time_left, tracking_time):
    # Таймер
    timer_text = f"Time left: {time_left:.1f}s"
    timer_surface = font.render(timer_text, True, WHITE)
    screen.blit(timer_surface, (20, 20))
    # Время трекинга
    tracking_text = f"Tracking: {tracking_time:.1f}s"
    tracking_surface = font.render(tracking_text, True, GREEN)
    screen.blit(tracking_surface, (20, 80))

def display_final_stats(tracking_time):
    screen.fill(DARK_GRAY)
    title_text = font.render("Tracking Results", True, WHITE)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 150))
    tracking_text = f"Tracking time: {tracking_time:.1f} seconds"
    tracking_surface = font.render(tracking_text, True, GREEN)
    screen.blit(tracking_surface, (screen_width // 2 - tracking_surface.get_width() // 2, screen_height // 2 - 50))
    instruction_text = "Press R to restart or ESC to exit"
    instruction_surface = small_font.render(instruction_text, True, GRAY)
    screen.blit(instruction_surface, (screen_width // 2 - instruction_surface.get_width() // 2, screen_height // 2 + 50))

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

def tracking_game():
    settings = load_settings()
    clock = pygame.time.Clock()

    # Размер круга зависит от сложности
    difficulty = settings.get('difficulty', 'medium')
    if difficulty == 'easy':
        target_radius = 35
    elif difficulty == 'hard':
        target_radius = 18
    else:
        target_radius = 25

    class TrackingTarget:
        def __init__(self):
            self.radius = target_radius
            self.x = screen_width // 2
            self.y = screen_height // 2
            self.vx = random.uniform(-BASE_SPEED, BASE_SPEED)
            self.vy = random.uniform(-BASE_SPEED, BASE_SPEED)
            self.speed = BASE_SPEED
            self.last_speed_change = 0
        def update(self, dt):
            self.last_speed_change += dt
            if self.last_speed_change >= SPEED_CHANGE_INTERVAL:
                self.speed = BASE_SPEED + random.uniform(-SPEED_VARIATION, SPEED_VARIATION)
                self.last_speed_change = 0
            if random.random() < 0.02:
                angle = random.uniform(0, 2 * math.pi)
                self.vx = math.cos(angle) * self.speed
                self.vy = math.sin(angle) * self.speed
            new_x = self.x + self.vx
            new_y = self.y + self.vy
            if new_x - self.radius < MARGIN:
                new_x = MARGIN + self.radius
                self.vx = abs(self.vx)
            elif new_x + self.radius > screen_width - MARGIN:
                new_x = screen_width - MARGIN - self.radius
                self.vx = -abs(self.vx)
            if new_y - self.radius < MARGIN:
                new_y = MARGIN + self.radius
                self.vy = abs(self.vy)
            elif new_y + self.radius > screen_height - MARGIN:
                new_y = screen_height - MARGIN - self.radius
                self.vy = -abs(self.vy)
            self.x = new_x
            self.y = new_y
        def draw(self, is_hovered):
            if is_hovered:
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 3)
            else:
                pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

    def reset_game():
        nonlocal target, game_time, tracking_time, is_tracking, game_state
        target = TrackingTarget()
        game_time = GAME_DURATION
        tracking_time = 0
        is_tracking = False
        game_state = "playing"
    
    target = TrackingTarget()
    game_time = GAME_DURATION
    tracking_time = 0
    is_tracking = False
    game_state = "playing"
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        if game_state == "playing":
            game_time -= dt
            if game_time <= 0:
                game_state = "finished"
            
            target.update(dt)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            distance = math.sqrt((mouse_x - target.x)**2 + (mouse_y - target.y)**2)
            
            if distance <= target.radius:
                if not is_tracking:
                    is_tracking = True
                tracking_time += dt
            else:
                is_tracking = False
            
            screen.fill(DARK_GRAY)
            draw_grid()
            target.draw(is_tracking)
            display_timer_and_tracking_time(game_time, tracking_time)
            
        elif game_state == "finished":
            display_final_stats(tracking_time)
        
        pygame.mouse.set_visible(False)
        pygame.draw.circle(screen, settings['crosshair_color'], (pygame.mouse.get_pos()), 5)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back_to_menu()
                elif event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_QUESTION:
                    game_state = "finished"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "finished":
                    reset_game()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    tracking_game() 