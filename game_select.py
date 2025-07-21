import pygame
import json
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if os.name == 'nt':
    os.system('chcp 65001 > nul')

pygame.init()

screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Selecting")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 50)
GRAY = (180, 180, 200)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (128, 0, 128)
GREEN = (0, 200, 120)
RED = (255, 80, 80)
SHADOW = (0, 0, 0, 60)

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Кнопки
BUTTON_WIDTH = 320
BUTTON_HEIGHT = 60
BUTTON_RADIUS = 30
BUTTON_MARGIN = 30

# Для анимации
HOVER_SCALE = 1.08
ANIMATION_SPEED = 0.15

# Кнопки с иконками и цветами
MODES = [
    {"label": "Aim", "color1": (0, 180, 255), "color2": (0, 120, 255), "action": "aim"},
    {"label": "Reaction", "color1": (0, 220, 140), "color2": (0, 180, 120), "action": "reaction"},
    {"label": "Tracking", "color1": (255, 140, 0), "color2": (255, 100, 0), "action": "tracking"},
    {"label": "Stress", "color1": (255, 80, 80), "color2": (255, 120, 200), "action": "stress_aim"},
    {"label": "Back", "color1": (120, 120, 120), "color2": (80, 80, 80), "action": "back"}
]

# Для анимации наведения
hover_states = [0.0 for _ in MODES]

def draw_gradient_capsule(surface, rect, color1, color2, radius, shadow=False):
    # Тень
    if shadow:
        shadow_surf = pygame.Surface((rect.width+8, rect.height+8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, SHADOW, (0, 0, rect.width+8, rect.height+8))
        surface.blit(shadow_surf, (rect.x-4, rect.y+6))
    # Градиент
    grad_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1-ratio) + color2[0] * ratio)
        g = int(color1[1] * (1-ratio) + color2[1] * ratio)
        b = int(color1[2] * (1-ratio) + color2[2] * ratio)
        pygame.draw.line(grad_surf, (r, g, b), (0, y), (rect.width, y))
    pygame.draw.ellipse(grad_surf, (0,0,0,0), (0,0,rect.width,rect.height))
    surface.blit(grad_surf, rect.topleft)
    # Капсула
    pygame.draw.ellipse(surface, (0,0,0,0), rect, 0)
    pygame.draw.rect(surface, (0,0,0,0), rect, 0, border_radius=radius)

def draw_button(label, x, y, width, height, color1, color2, hover=0.0):
    # Анимация увеличения
    scale = 1.0 + (HOVER_SCALE-1.0)*hover
    w, h = int(width*scale), int(height*scale)
    rect = pygame.Rect(x + width//2 - w//2, y + height//2 - h//2, w, h)
    draw_gradient_capsule(screen, rect, color1, color2, BUTTON_RADIUS, shadow=True)
    # Текст
    btn_font = pygame.font.Font(None, int(38*scale))
    text_surface = btn_font.render(label, True, WHITE)
    screen.blit(text_surface, (rect.centerx - text_surface.get_width()//2, rect.centery - text_surface.get_height()//2))
    return rect

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

def start_aim_training():
    settings = load_settings()
    difficulty = settings.get('difficulty', 'medium')
    if difficulty == 'easy':
        filename = 'aim_sec_easy.py'
    elif difficulty == 'hard':
        filename = 'aim_sec_hard.py'
    else:
        filename = 'aim_sec.py'
    os.execv(sys.executable, ['python'] + [filename])

def start_reaction_test():
    os.execv(sys.executable, ['python'] + ['reaction_sec.py'])

def start_tracking_game():
    os.execv(sys.executable, ['python'] + ['tracking_sec.py'])

def start_stress_aim():
    os.execv(sys.executable, ['python'] + ['stress_aim_sec.py'])

def back_to_menu():
    os.execv(sys.executable, ['python'] + ['menu.py'])

def game_select_menu():
    running = True
    settings = load_settings()
    clock = pygame.time.Clock()
    while running:
        screen.fill(DARK_GRAY)

        # Современный заголовок
        title_font = pygame.font.Font(None, 90)
        title_text = title_font.render("Select Mode", True, (220, 220, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 80))

        # Кнопки
        btn_y = screen_height // 2 - (len(MODES)//2)*BUTTON_HEIGHT - BUTTON_MARGIN
        btn_rects = []
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for i, mode in enumerate(MODES):
            btn_rect = draw_button(
                mode["label"],
                screen_width // 2 - BUTTON_WIDTH // 2,
                btn_y + i*(BUTTON_HEIGHT + BUTTON_MARGIN),
                BUTTON_WIDTH, BUTTON_HEIGHT,
                mode["color1"], mode["color2"],
                hover_states[i]
            )
            btn_rects.append(btn_rect)
            # Анимация наведения
            if btn_rect.collidepoint((mouse_x, mouse_y)):
                hover_states[i] = min(1.0, hover_states[i] + ANIMATION_SPEED)
            else:
                hover_states[i] = max(0.0, hover_states[i] - ANIMATION_SPEED)

        # Курсор
        pygame.mouse.set_visible(False)
        pygame.draw.circle(screen, settings['crosshair_color'], (mouse_x, mouse_y), 5)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back_to_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn_rect in enumerate(btn_rects):
                    if btn_rect.collidepoint(event.pos):
                        if MODES[i]["action"] == "aim":
                            start_aim_training()
                        elif MODES[i]["action"] == "reaction":
                            start_reaction_test()
                        elif MODES[i]["action"] == "tracking":
                            start_tracking_game()
                        elif MODES[i]["action"] == "stress_aim":
                            start_stress_aim()
                        elif MODES[i]["action"] == "back":
                            back_to_menu()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_select_menu() 