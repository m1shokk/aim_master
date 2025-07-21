import pygame
import json
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if os.name == 'nt':
    os.system('chcp 65001 > nul')

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Меню")


def resource_path(relative_path):
    """Путь к ресурсу для работы и из исходников, и из exe PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


# Загрузка изображения
preview_image_path = resource_path('preview_menu.png')
preview_image = pygame.image.load(preview_image_path)
preview_image = pygame.transform.scale(preview_image, (screen_width, int(screen_height)))


# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
VILALA = (120, 105, 255)

# Шрифты
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Кнопки
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
button_color = (128, 128, 128)  # Серый цвет кнопок
button_hover_color = YELLOW  # Цвет при наведении
border_radius = 20  # Радиус округления углов кнопок

def draw_button(text, x, y, width, height, action=None):
    font = pygame.font.Font(None, 50)
    button_rect = pygame.Rect(x, y, width, height)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Проверка наведения мыши
    if button_rect.collidepoint((mouse_x, mouse_y)):
        color = VILALA  # Подсветка желтым цветом при наведении
        pygame.draw.rect(screen, color, button_rect, border_radius=15)  # Яркая подсветка при наведении
        # Обработка клика
        if pygame.mouse.get_pressed()[0]:  # Проверка нажатия кнопки мыши
            if action:  # Выполнение действия при нажатии
                action()  
    else:
        pygame.draw.rect(screen, GRAY, button_rect, border_radius=15)
    
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {'sensitivity': 1.66, 'crosshair_color': (255, 255, 255)}  # Значения по умолчанию
        save_settings(settings)
    return settings

def save_settings(settings):
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def open_settings():
    settings = load_settings()
    slider_value = settings['sensitivity']
    crosshair_color = settings['crosshair_color']
    difficulty = settings.get('difficulty', 'medium')
    settings_running = True
    dragging_slider = False
    # Цвета и параметры для красивого дизайна
    BG_COLOR = (40, 40, 50)
    BLOCK_COLOR1 = (60, 60, 80)
    BLOCK_COLOR2 = (30, 30, 40)
    BUTTON_GRAD1 = (0, 180, 255)
    BUTTON_GRAD2 = (0, 120, 255)
    BUTTON_RADIUS = 28
    BUTTON_MARGIN = 30
    HOVER_SCALE = 1.08
    ANIMATION_SPEED = 0.15
    # Для анимации наведения
    hover_states = [0.0, 0.0, 0.0]
    while settings_running:
        screen.fill(BG_COLOR)
        # Заголовок
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("Settings", True, (220, 220, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 60))
        # --- Sensitivity Block ---
        block_rect = pygame.Rect(screen_width//2-220, 170, 440, 90)
        pygame.draw.rect(screen, BLOCK_COLOR1, block_rect, border_radius=30)
        sens_label = small_font.render(f"Sensitivity: {slider_value:.2f}", True, WHITE)
        screen.blit(sens_label, (block_rect.centerx - sens_label.get_width()//2, block_rect.y+10))
        # Красивая полоска
        pygame.draw.rect(screen, (80, 80, 120), (block_rect.x+40, block_rect.y+50, 320, 12), border_radius=8)
        fill_w = int((slider_value-0.1)/7.9*320)
        pygame.draw.rect(screen, (0, 180, 255), (block_rect.x+40, block_rect.y+50, fill_w, 12), border_radius=8)
        # Кружок-ползунок
        slider_x = block_rect.x+40+fill_w
        pygame.draw.circle(screen, (0, 180, 255), (slider_x, block_rect.y+56), 16)
        # --- Crosshair Color Block ---
        color_block_rect = pygame.Rect(screen_width//2-220, 280, 440, 110)
        pygame.draw.rect(screen, BLOCK_COLOR1, color_block_rect, border_radius=30)
        label = small_font.render("Crosshair Color", True, WHITE)
        screen.blit(label, (color_block_rect.centerx - label.get_width()//2, color_block_rect.y+10))
        colors = [WHITE, RED, YELLOW, GREEN, BLUE, PURPLE]
        for i, color in enumerate(colors):
            color_x = color_block_rect.x + 40 + i*60
            color_y = color_block_rect.y + 50
            pygame.draw.circle(screen, color, (color_x, color_y), 22)
            if crosshair_color == color:
                pygame.draw.circle(screen, (0, 180, 255), (color_x, color_y), 26, 3)
        # --- Difficulty Block ---
        diff_block_rect = pygame.Rect(screen_width//2-220, 410, 440, 90)
        pygame.draw.rect(screen, BLOCK_COLOR1, diff_block_rect, border_radius=30)
        diff_label = small_font.render("Difficulty:", True, WHITE)
        screen.blit(diff_label, (diff_block_rect.x+30, diff_block_rect.y+15))
        diff_names = ["easy", "medium", "hard"]
        for i, name in enumerate(diff_names):
            btn_x = diff_block_rect.x+160+i*90
            btn_y = diff_block_rect.y+20
            btn_w = 80
            btn_h = 50
            # Градиентная кнопка
            grad_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            for y in range(btn_h):
                ratio = y/btn_h
                r = int(BUTTON_GRAD1[0]*(1-ratio)+BUTTON_GRAD2[0]*ratio)
                g = int(BUTTON_GRAD1[1]*(1-ratio)+BUTTON_GRAD2[1]*ratio)
                b = int(BUTTON_GRAD1[2]*(1-ratio)+BUTTON_GRAD2[2]*ratio)
                pygame.draw.line(grad_surf, (r,g,b), (0,y), (btn_w,y))
            scale = 1.0 + (HOVER_SCALE-1.0)*hover_states[i]
            sw, sh = int(btn_w*scale), int(btn_h*scale)
            btn_rect = pygame.Rect(btn_x+btn_w//2-sw//2, btn_y+btn_h//2-sh//2, sw, sh)
            screen.blit(grad_surf, btn_rect.topleft)
            pygame.draw.rect(screen, (0,0,0,40), btn_rect, 2, border_radius=18)
            txt = small_font.render(name.capitalize(), True, WHITE if difficulty==name else (180,180,200))
            screen.blit(txt, (btn_rect.centerx-txt.get_width()//2, btn_rect.centery-txt.get_height()//2))
            # Анимация наведения
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if btn_rect.collidepoint((mouse_x, mouse_y)):
                hover_states[i] = min(1.0, hover_states[i]+ANIMATION_SPEED)
            else:
                hover_states[i] = max(0.0, hover_states[i]-ANIMATION_SPEED)
        # --- Back Button ---
        back_rect = pygame.Rect(screen_width//2-100, screen_height-120, 200, 60)
        grad_surf = pygame.Surface((200, 60), pygame.SRCALPHA)
        for y in range(60):
            ratio = y/60
            r = int(120*(1-ratio)+80*ratio)
            g = int(120*(1-ratio)+80*ratio)
            b = int(120*(1-ratio)+80*ratio)
            pygame.draw.line(grad_surf, (r,g,b), (0,y), (200,y))
        screen.blit(grad_surf, back_rect.topleft)
        pygame.draw.rect(screen, (0,0,0,40), back_rect, 2, border_radius=22)
        back_txt = small_font.render("Back", True, WHITE)
        screen.blit(back_txt, (back_rect.centerx-back_txt.get_width()//2, back_rect.centery-back_txt.get_height()//2))
        # Курсор
        pygame.mouse.set_visible(False)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, settings['crosshair_color'], (mouse_x, mouse_y), 5)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Back
                if back_rect.collidepoint(event.pos):
                    settings_running = False
                # Цвет
                for i, color in enumerate(colors):
                    color_x = color_block_rect.x + 40 + i*60
                    color_y = color_block_rect.y + 50
                    if (event.pos[0]-color_x)**2 + (event.pos[1]-color_y)**2 <= 22**2:
                        settings['crosshair_color'] = color
                        save_settings(settings)
                        crosshair_color = color
                        break
                # Ползунок чувствительности
                if block_rect.x+40-16 < event.pos[0] < block_rect.x+40+320+16 and block_rect.y+50-16 < event.pos[1] < block_rect.y+50+16:
                    dragging_slider = True
                # Кнопки сложности
                for i, name in enumerate(diff_names):
                    btn_x = diff_block_rect.x+160+i*90
                    btn_y = diff_block_rect.y+20
                    btn_w = 80
                    btn_h = 50
                    scale = 1.0 + (HOVER_SCALE-1.0)*hover_states[i]
                    sw, sh = int(btn_w*scale), int(btn_h*scale)
                    btn_rect = pygame.Rect(btn_x+btn_w//2-sw//2, btn_y+btn_h//2-sh//2, sw, sh)
                    if btn_rect.collidepoint(event.pos):
                        difficulty = name
                        settings['difficulty'] = name
                        save_settings(settings)
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
            if event.type == pygame.MOUSEMOTION and dragging_slider:
                if block_rect.x+40-16 < event.pos[0] < block_rect.x+40+320+16 and block_rect.y+50-16 < event.pos[1] < block_rect.y+50+16:
                    slider_value = max(0.1, min(8.0, (event.pos[0] - (block_rect.x+40)) / 320 * 7.9 + 0.1))
                    settings['sensitivity'] = slider_value
                    save_settings(settings)

def draw_blurred_shadow(surface, pos, radius, shadow_color, blur_intensity):
    shadow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    shadow_surface.fill((0, 0, 0, 0))

    for i in range(blur_intensity):
        alpha = int(255 * (1 - i / blur_intensity))
        pygame.draw.circle(shadow_surface, (*shadow_color, alpha), (radius * 2, radius * 2), radius + i)

    surface.blit(shadow_surface, (pos[0] - radius * 2, pos[1] - radius * 2))

def start_game():
    os.execv(sys.executable, ['python'] + ['aim_sec.py'])

def start_game_select():
    os.execv(sys.executable, ['python'] + ['game_select.py'])

def main_menu():
    running = True
    settings = load_settings()  # Загружаем настройки
    while running:
        screen.fill(DARK_GRAY)

        # Отображение изображения
        screen.blit(preview_image, (0, 0))  # Отображаем изображение в верхней части экрана

        # Рисуем кнопки
        draw_button("Start", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 - BUTTON_HEIGHT - 20, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: start_game_select())
        draw_button("Settings", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 + 20, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: open_settings())
        draw_button("Exit", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 + BUTTON_HEIGHT + 60, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: pygame.quit())

        # Рисуем курсор с тенью (оптимизированная версия)
        pygame.mouse.set_visible(False)  # Скрываем стандартный курсор
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, settings['crosshair_color'], (mouse_x, mouse_y), 5)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if screen_width // 2 - BUTTON_WIDTH // 2 < event.pos[0] < screen_width // 2 + BUTTON_WIDTH // 2 and screen_height // 2 - BUTTON_HEIGHT - 20 < event.pos[1] < screen_height // 2 - BUTTON_HEIGHT - 20 + BUTTON_HEIGHT:
                    start_game_select()  # Запуск окна выбора режима
                elif screen_width // 2 - BUTTON_WIDTH // 2 < event.pos[0] < screen_width // 2 + BUTTON_WIDTH // 2 and screen_height // 2 + 20 < event.pos[1] < screen_height // 2 + 20 + BUTTON_HEIGHT:
                    open_settings()
                elif screen_width // 2 - BUTTON_WIDTH // 2 < event.pos[0] < screen_width // 2 + BUTTON_WIDTH // 2 and screen_height // 2 + BUTTON_HEIGHT + 60 < event.pos[1] < screen_height // 2 + BUTTON_HEIGHT + 60 + BUTTON_HEIGHT:
                    running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
