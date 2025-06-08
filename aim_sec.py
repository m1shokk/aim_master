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
pygame.display.set_caption("Aim Master (Ch0kz Games)")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
GRID_COLOR = (100, 100, 100)  # Цвет сетки
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

# Переменные игры   
score = 0
total_shots = 0  # Общее количество выстрелов
circle_radius = 20
circles = []
sensitivity = 1.66
start_time = time.time()  # Время начала игры
game_duration = 60  # Длительность игры в секундах
crosshair_color = WHITE  # Изначально белый цвет прицела
last_mouse_pos = (0, 0)  # Последняя позиция мыши

# Цвета для выбора курсора
CURSOR_COLORS = {
    "white": WHITE,
    "red": RED,
    "green": GREEN,
    "yellow": YELLOW,
    "black": BLACK,
    "blue": BLUE,
    "purple": PURPLE
}

def create_circle():
    x = random.randint(circle_radius, screen_width - circle_radius)
    y = random.randint(circle_radius, screen_height - circle_radius)
    circles.append((x, y))

def draw_grid():
    for x in range(0, screen_width, 50):  # Вертикальные линии
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, screen_height))
    for y in range(0, screen_height, 50):  # Горизонтальные линии
        pygame.draw.line(screen, GRID_COLOR, (0, y), (screen_width, y))

def display_score_and_timer():
    font = pygame.font.Font(None, 74)
    text = font.render(f"{score}", True, WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, 20))
    
    remaining_time = max(0, game_duration - int(time.time() - start_time))
    timer_text = font.render(f"{remaining_time} sec", True, WHITE)
    screen.blit(timer_text, (10, 10))

    pygame.display.flip()

def display_final_stats():
    global score
    accuracy = (score / total_shots) * 100 if total_shots > 0 else 0
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    
    # Загружаем текущий рекорд
    settings = load_settings()
    high_score = settings.get('high_score', 0)
    
    # Обновляем рекорд если текущий счет выше
    if score > high_score:
        high_score = score
        settings['high_score'] = high_score
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    
    screen.fill(DARK_GRAY)
    text = font.render(f"Your score: {score}", True, WHITE)
    accuracy_text = font.render(f"Accuracy: {accuracy:.2f}%", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    restart_text = small_font.render("Press R for restart", True, WHITE)
    
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - 100))
    screen.blit(accuracy_text, (screen_width // 2 - accuracy_text.get_width() // 2, screen_height // 2 - 20))
    screen.blit(high_score_text, (screen_width // 2 - high_score_text.get_width() // 2, screen_height // 2 + 60))
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 140))
    
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

def reset_game():
    global score, total_shots, circles, start_time
    score = 0
    total_shots = 0  # Сброс общего количества выстрелов
    circles.clear()
    start_time = time.time()  # Сброс времени

# Скрытие курсора
pygame.mouse.set_visible(False)

# Функция для рисования размытой тени №№
def draw_blurred_shadow(surface, pos, radius, shadow_color, blur_intensity):
    shadow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    shadow_surface.fill((0, 0, 0, 0))

    for i in range(blur_intensity):
        alpha = int(255 * (1 - i / blur_intensity))
        pygame.draw.circle(shadow_surface, (*shadow_color, alpha), (radius * 2, radius * 2), radius + i)

    surface.blit(shadow_surface, (pos[0] - radius * 2, pos[1] - radius * 2))

# Загрузка настроек
def load_settings():
    global sensitivity, crosshair_color
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            sensitivity = settings.get('sensitivity', 1.66)
            crosshair_color = tuple(settings.get('crosshair_color', WHITE))
            return settings  # Возвращаем весь словарь настроек
    except FileNotFoundError:
        settings = {
            'sensitivity': 1.66,
            'crosshair_color': list(WHITE),
            'high_score': 0
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
load_settings()  # Загрузка настроек при запуске игры
while running:
    screen.fill(DARK_GRAY)
    draw_grid()  # Рисуем сетку
    
    if len(circles) < 1:
        create_circle()
    
    for circle in circles:
        draw_blurred_shadow(screen, circle, circle_radius, RED, 5)  # Размытая тень
        pygame.draw.circle(screen, RED, circle, circle_radius)
    
    # Получаем позицию курсора и применяем чувствительность
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_rel_x, mouse_rel_y = pygame.mouse.get_rel()
    
    # Применяем чувствительность к движению мыши
    if mouse_rel_x != 0 or mouse_rel_y != 0:
        mouse_x = last_mouse_pos[0] + (mouse_rel_x * sensitivity)
        mouse_y = last_mouse_pos[1] + (mouse_rel_y * sensitivity)
        
        # Ограничиваем движение мыши пределами экрана
        mouse_x = max(0, min(screen_width, mouse_x))
        mouse_y = max(0, min(screen_height, mouse_y))
        
        # Обновляем позицию мыши
        pygame.mouse.set_pos(int(mouse_x), int(mouse_y))
    
    last_mouse_pos = (mouse_x, mouse_y)
    
    # Рисование размытой тени
    draw_blurred_shadow(screen, (mouse_x, mouse_y), radius=4, shadow_color=crosshair_color, blur_intensity=6)

    # Рисуем прицел
    pygame.draw.circle(screen, crosshair_color, (mouse_x, mouse_y), 7)  # Белый кружочек
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Запускаем menu.py и закрываем aim_sec.py
                os.execv(sys.executable, ['python'] + ['menu.py'])
            elif event.key == pygame.K_r:
                reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            total_shots += 1  # Увеличиваем общее количество выстрелов
            hit = False
            for circle in circles[:]:
                if (mouse_x - circle[0])**2 + (mouse_y - circle[1])**2 <= circle_radius**2:
                    circles.remove(circle)
                    score += 1
                    hit = True
                    break
            if not hit:
                score -= 1

    # Проверка времени
    if time.time() - start_time >= game_duration:
        display_final_stats()

    display_score_and_timer()

# Завершение игры
pygame.quit()
