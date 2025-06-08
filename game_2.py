import pygame
import random
import time
import json
import os
import sys

pygame.init()

screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Aim Master (Ch0kz Games)")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
GRID_COLOR = (100, 100, 100)

score = 0
total_shots = 0
missed_shots = 0  # Новая переменная для промахов
circles = []
sensitivity = 1.66
start_time = time.time()
game_duration = 60
crosshair_color = WHITE

CURSOR_COLORS = {"white": WHITE, "red": RED, "black": BLACK}

def create_circle():
    radius = random.randint(8, 35)
    x = random.randint(radius, screen_width - radius)
    y = random.randint(radius, screen_height - radius)
    circles.append({'pos': (x, y), 'radius': radius, 'spawn_time': time.time()})

def draw_grid():
    for x in range(0, screen_width, 50):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, screen_height))
    for y in range(0, screen_height, 50):
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
    accuracy = (score / total_shots) * 100 if total_shots > 0 else 0
    font = pygame.font.Font(None, 74)
    screen.fill(DARK_GRAY)
    text = font.render(f"Your score: {score}", True, WHITE)
    accuracy_text = font.render(f"Accuracy: {accuracy:.2f}%", True, WHITE)
    missed_text = font.render(f"Misses: {missed_shots}", True, WHITE)
    restart_text = font.render("Press R for restart", True, WHITE)
    
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - 50))
    screen.blit(accuracy_text, (screen_width // 2 - accuracy_text.get_width() // 2, screen_height // 2))
    screen.blit(missed_text, (screen_width // 2 - missed_text.get_width() // 2, screen_height // 2 + 50))
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 100))
    
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
    global score, total_shots, missed_shots, circles, start_time
    score = 0
    total_shots = 0
    missed_shots = 0
    circles.clear()
    start_time = time.time()

pygame.mouse.set_visible(False)
last_spawn_time = time.time()

running = True
while running:
    screen.fill(DARK_GRAY)
    draw_grid()
    
    if time.time() - last_spawn_time >= 1:
        create_circle()
        last_spawn_time = time.time()
    
    for circle in circles[:]:
        elapsed_time = time.time() - circle['spawn_time']
        alpha = max(0, int(255 * (1 - elapsed_time / 3)))
        if alpha == 0:
            circles.remove(circle)
        else:
            surf = pygame.Surface((circle['radius'] * 4, circle['radius'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 0, 0, alpha), (circle['radius'] * 2, circle['radius'] * 2), circle['radius'])
            screen.blit(surf, (circle['pos'][0] - circle['radius'] * 2, circle['pos'][1] - circle['radius'] * 2))
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, crosshair_color, (mouse_x, mouse_y), 7)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                os.execv(sys.executable, ['python', 'menu.py'])
            elif event.key == pygame.K_r:
                reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            total_shots += 1
            hit = False
            for circle in circles[:]:
                if (mouse_x - circle['pos'][0])**2 + (mouse_y - circle['pos'][1])**2 <= circle['radius']**2:
                    circles.remove(circle)
                    score += 1
                    hit = True
                    break
            if not hit:
                missed_shots += 1
    
    if time.time() - start_time >= game_duration:
        display_final_stats()
    
    display_score_and_timer()

pygame.quit()
