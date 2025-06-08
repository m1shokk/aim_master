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
        color = YELLOW  # Подсветка желтым цветом при наведении
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
    
    settings_running = True
    dragging_slider = False
    while settings_running:
        screen.fill(DARK_GRAY)

        # Отображаем интерфейс настроек
        draw_button("Back", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 + 200, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: None)
        
        # Отображаем текущее значение чувствительности
        sensitivity_text = small_font.render(f"Sensitivity: {slider_value:.2f}", True, WHITE)
        screen.blit(sensitivity_text, (screen_width // 2 - sensitivity_text.get_width() // 2, screen_height // 2 - 50))
        
        # Ползунок для изменения чувствительности
        pygame.draw.rect(screen, WHITE, (screen_width // 2 - 100, screen_height // 2, 200, 10))  # Ползунок
        pygame.draw.rect(screen, ORANGE, (screen_width // 2 - 100 + int((slider_value - 0.1) / 7.9 * 200), screen_height // 2 - 5, 10, 20))  # Индикатор ползунка

        # Блок для выбора цвета курсора
        crosshair_color_block_x = screen_width // 2 - 150
        crosshair_color_block_y = screen_height // 2 + 50
        block_width = 300
        block_height = 150
        block_border_radius = 20
        
        # Рисуем блок для цветов
        pygame.draw.rect(screen, DARK_GRAY, (crosshair_color_block_x, crosshair_color_block_y, block_width, block_height), border_radius=block_border_radius)
        
        # Текст "Crosshair Color" посередине блока
        label = small_font.render("Crosshair Color", True, WHITE)
        screen.blit(label, (crosshair_color_block_x + (block_width - label.get_width()) // 2, crosshair_color_block_y + 10))

        # Цветные квадратики (3 сверху, 3 снизу)
        colors = [WHITE, RED, YELLOW, GREEN, BLUE, PURPLE]
        for i, color in enumerate(colors):
            color_x = crosshair_color_block_x + (i % 3) * 100 + 25  # Смещение по x
            color_y = crosshair_color_block_y + (i // 3) * 50 + 40  # Смещение по y
            pygame.draw.rect(screen, color, (color_x, color_y, 50, 50))
            if crosshair_color == color:
                pygame.draw.rect(screen, BLACK, (color_x, color_y, 50, 50), 5)  # Обводка выбранного цвета

        # Рисуем курсор с тенью
        pygame.mouse.set_visible(False)  # Скрываем стандартный курсор
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_blurred_shadow(screen, (mouse_x, mouse_y), radius=4, shadow_color=settings['crosshair_color'], blur_intensity=6)
        pygame.draw.circle(screen, settings['crosshair_color'], (mouse_x, mouse_y), 5)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Если нажата клавиша ESC
                    settings_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if screen_width // 2 - BUTTON_WIDTH // 2 < event.pos[0] < screen_width // 2 + BUTTON_WIDTH // 2 and screen_height // 2 + 200 < event.pos[1] < screen_height // 2 + 200 + BUTTON_HEIGHT:
                    settings_running = False
                # Проверка нажатия на квадратики цветов
                for i, color in enumerate(colors):
                    if crosshair_color_block_x + (i % 3) * 100 + 25 < event.pos[0] < crosshair_color_block_x + (i % 3) * 100 + 25 + 50 and crosshair_color_block_y + (i // 3) * 50 + 40 < event.pos[1] < crosshair_color_block_y + (i // 3) * 50 + 40 + 50:
                        settings['crosshair_color'] = color
                        save_settings(settings)  # Сохраняем настройки
                        break
                # Изменение чувствительности с помощью ползунка
                if screen_width // 2 - 100 < event.pos[0] < screen_width // 2 + 100 and screen_height // 2 - 5 < event.pos[1] < screen_height // 2 + 5:
                    dragging_slider = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

            # Обработка изменения ползунка при зажатии мыши
            if event.type == pygame.MOUSEMOTION and dragging_slider:
                if screen_width // 2 - 100 < event.pos[0] < screen_width // 2 + 100 and screen_height // 2 - 5 < event.pos[1] < screen_height // 2 + 5:
                    slider_value = max(0.1, min(8.0, (event.pos[0] - (screen_width // 2 - 100)) / 200 * 7.9 + 0.1))
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
    # Запускаем aim_sec.py и закрываем menu.py
    os.execv(sys.executable, ['python'] + ['aim_sec.py'])

def main_menu():
    running = True
    settings = load_settings()  # Загружаем настройки
    while running:
        screen.fill(DARK_GRAY)

        # Отображение изображения
        screen.blit(preview_image, (0, 0))  # Отображаем изображение в верхней части экрана

        # Рисуем кнопки
        draw_button("Start", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 - BUTTON_HEIGHT - 20, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: start_game())
        draw_button("Settings", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 + 20, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: open_settings())
        draw_button("Exit", screen_width // 2 - BUTTON_WIDTH // 2, screen_height // 2 + BUTTON_HEIGHT + 60, BUTTON_WIDTH, BUTTON_HEIGHT, lambda: pygame.quit())

        # Рисуем курсор с тенью
        pygame.mouse.set_visible(False)  # Скрываем стандартный курсор
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_blurred_shadow(screen, (mouse_x, mouse_y), radius=4, shadow_color=settings['crosshair_color'], blur_intensity=6)
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
                    start_game()  # Запуск aim_sec.py
                elif screen_width // 2 - BUTTON_WIDTH // 2 < event.pos[0] < screen_width // 2 + BUTTON_WIDTH // 2 and screen_height // 2 + 20 < event.pos[1] < screen_height // 2 + 20 + BUTTON_HEIGHT:
                    open_settings()
                elif screen_width // 2 - BUTTON_WIDTH // 2 < event.pos[0] < screen_width // 2 + BUTTON_WIDTH // 2 and screen_height // 2 + BUTTON_HEIGHT + 60 < event.pos[1] < screen_height // 2 + BUTTON_HEIGHT + 60 + BUTTON_HEIGHT:
                    running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
