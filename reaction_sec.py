import pygame
import random
import time
import json
import os
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Reaction Speed Test (Ch0kz Games)")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (40, 40, 50)
BLACK = (0, 0, 0)
GRID_COLOR = (60, 60, 70)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (128, 0, 128)
GRAY = (180, 180, 200)

# Переменные игры
total_attempts = 0
reaction_times = []  # Список времени реакции для каждого клика
circle_radius = 80  # Большой шарик по центру
sensitivity = 1.66
max_attempts = 5  # Максимум 5 попыток
crosshair_color = WHITE
last_mouse_pos = (0, 0)

# Состояние игры
game_state = "waiting"  # "waiting", "ready", "clicked"
color_change_time = 0
wait_duration = 0
current_reaction_start = 0

# Шрифты
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)

# Функция для рисования сетки
def draw_grid():
    for x in range(0, screen_width, 50):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, screen_height))
    for y in range(0, screen_height, 50):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (screen_width, y))

# Функция для рисования размытой тени
def draw_blurred_shadow(surface, pos, radius, shadow_color, blur_intensity):
    shadow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    shadow_surface.fill((0, 0, 0, 0))

    for i in range(blur_intensity):
        alpha = int(255 * (1 - i / blur_intensity))
        pygame.draw.circle(shadow_surface, (*shadow_color, alpha), (radius * 2, radius * 2), radius + i)

    surface.blit(shadow_surface, (pos[0] - radius * 2, pos[1] - radius * 2))

def display_attempts_and_stats():
    # Попытки
    attempts_text = font.render(f"Attempt {total_attempts}/{max_attempts}", True, WHITE)
    screen.blit(attempts_text, (screen_width // 2 - attempts_text.get_width() // 2, 20))
    
    # Среднее время реакции
    if reaction_times:
        avg_reaction = sum(reaction_times) / len(reaction_times)
        avg_text = small_font.render(f"Avg Reaction: {avg_reaction:.3f}s", True, WHITE)
        screen.blit(avg_text, (10, 80))
    
    # Лучшее время реакции
    if reaction_times:
        best_reaction = min(reaction_times)
        best_text = small_font.render(f"Best: {best_reaction:.3f}s", True, YELLOW)
        screen.blit(best_text, (10, 120))

def display_final_stats():
    screen.fill(DARK_GRAY)
    title_text = font.render("Reaction Test Complete!", True, WHITE)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 120))
    if reaction_times:
        avg_reaction = sum(reaction_times) / len(reaction_times)
        avg_text = font.render(f"Average Reaction: {avg_reaction:.3f}s", True, WHITE)
        screen.blit(avg_text, (screen_width // 2 - avg_text.get_width() // 2, screen_height // 2 - 40))
        best_reaction = min(reaction_times)
        best_text = font.render(f"Best Reaction: {best_reaction:.3f}s", True, GREEN)
        screen.blit(best_text, (screen_width // 2 - best_text.get_width() // 2, screen_height // 2 + 20))
        worst_reaction = max(reaction_times)
        worst_text = font.render(f"Worst Reaction: {worst_reaction:.3f}s", True, WHITE)
        screen.blit(worst_text, (screen_width // 2 - worst_text.get_width() // 2, screen_height // 2 + 80))
    restart_text = small_font.render("Press R for restart", True, WHITE)
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 160))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    waiting = False
                    return

def reset_game():
    global total_attempts, reaction_times, game_state, color_change_time, wait_duration
    total_attempts = 0
    reaction_times.clear()
    game_state = "waiting"
    color_change_time = 0
    wait_duration = 0
    start_new_round()  # Инициализируем первый раунд

def start_new_round():
    global game_state, color_change_time, wait_duration
    game_state = "waiting"
    wait_duration = random.uniform(2.0, 6.0)  # Случайное время от 2 до 6 секунд
    color_change_time = time.time() + wait_duration

# Скрытие курсора
pygame.mouse.set_visible(False)

# Загрузка настроек
def load_settings():
    global sensitivity, crosshair_color
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            sensitivity = settings.get('sensitivity', 1.66)
            crosshair_color = tuple(settings.get('crosshair_color', WHITE))
            return settings
    except FileNotFoundError:
        settings = {
            'sensitivity': 1.66,
            'crosshair_color': list(WHITE)
        }
        save_settings()
        return settings

# Сохранение настроек
def save_settings():
    global sensitivity, crosshair_color
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    
    settings.update({
        'sensitivity': sensitivity,
        'crosshair_color': list(crosshair_color)
    })
    
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# Основной игровой цикл
running = True
paused = False
load_settings()
start_new_round()

while running:
    screen.fill(DARK_GRAY)
    draw_grid()
    
    # Центр экрана
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    # Обновление состояния игры
    current_time = time.time()
    
    if game_state == "waiting" and current_time >= color_change_time:
        game_state = "ready"
        current_reaction_start = current_time
    
    # Рисование основного шарика
    if game_state == "waiting":
        circle_color = RED
        status_text = "Wait"
    elif game_state == "ready":
        circle_color = GREEN
        status_text = "Now"
    else:  # clicked
        circle_color = GREEN
        status_text = "Now"
    
    # Рисование размытой тени (как в aim_sec.py)
    draw_blurred_shadow(screen, (center_x, center_y), circle_radius, circle_color, 5)
    pygame.draw.circle(screen, circle_color, (center_x, center_y), circle_radius)
    
    # Текст статуса (полупрозрачный)
    status_font = pygame.font.Font(None, 60)
    status_surface = status_font.render(status_text, True, WHITE)
    
    # Создание полупрозрачной поверхности
    alpha_surface = pygame.Surface(status_surface.get_size(), pygame.SRCALPHA)
    alpha_surface.fill((255, 255, 255, 128))  # 128 = 50% прозрачности
    status_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    screen.blit(status_surface, (center_x - status_surface.get_width() // 2, center_y - circle_radius - 80))
    
    # Получаем позицию курсора (упрощённая версия без лагов)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Рисование размытой тени
    draw_blurred_shadow(screen, (mouse_x, mouse_y), 4, crosshair_color, 6)

    # Рисуем прицел (как в aim_sec.py)
    pygame.draw.circle(screen, crosshair_color, (mouse_x, mouse_y), 7)  # Белый кружочек
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                os.execv(sys.executable, ['python'] + ['menu.py'])
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_SLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Клавиша "?"
                display_final_stats()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            total_attempts += 1
            
            if game_state == "ready":
                # Правильный клик - засчитываем время реакции
                reaction_time = current_time - current_reaction_start
                reaction_times.append(reaction_time)
                start_new_round()  # Сразу начинаем новый раунд
            elif game_state == "waiting":
                # Слишком рано - штраф (добавляем большое время как штраф)
                reaction_times.append(2.0)  # 2 секунды как штраф за слишком ранний клик
                start_new_round()  # Сразу начинаем новый раунд
    
    # Проверка количества попыток
    if total_attempts >= max_attempts:
        display_final_stats()

    display_attempts_and_stats()
    
    pygame.display.flip()

# Завершение игры
pygame.quit() 