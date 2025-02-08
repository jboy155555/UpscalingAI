import pygame
import sys
import os
from PIL import Image

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH = 1920
HEIGHT = 1080
FPS = 50
fps = 50

# Настройки анимации
TEXTURE_DIR = "C:/photoes/"  # Папка с текстурами
FRAME_DELAY = 1 / fps * 1000  # Задержка между кадрами в миллисекундах (плавность)
print(FRAME_DELAY)

# Настройки шрифта
FONT_SIZE = 36
FONT_COLOR = (255, 255, 255)  # Белый цвет
BG_COLOR = (30, 30, 30)

# Загрузка текстур
textures = []
textures2 = []
i = 1
while True:
    try:
        path = os.path.join(TEXTURE_DIR, f"result_{i}.jpeg")
        img = Image.open(path)  # Загрузка изображения с помощью Pillow
        img = img.resize((950, 1080))
        path2 = os.path.join(TEXTURE_DIR, f"obs{i}.jpeg")
        img2 = Image.open(path2)  # Загрузка изображения с помощью Pillow
        img2 = img2.resize((950, 1080))  # Изменение размера
        img = pygame.image.fromstring(img.tobytes(), img.size, img.mode) 
        img2 = pygame.image.fromstring(img2.tobytes(), img2.size, img2.mode) # Конвертация в Pygame
        textures.append(img)
        textures2.append(img2)
        i += 1
    except (FileNotFoundError, OSError):
        break

if not textures:
    print("Не найдено ни одной текстуры!")
    pygame.quit()
    sys.exit()

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Texture Animation with FPS")
clock = pygame.time.Clock()

# Загрузка шрифта
try:
    font = pygame.font.SysFont('Arial', FONT_SIZE, bold=True)
except:
    font = pygame.font.Font(None, FONT_SIZE)

# Параметры анимации
current_frame = 0
last_update = pygame.time.get_ticks()

# Основной цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Логика анимации
    now = pygame.time.get_ticks()
    if now - last_update > FRAME_DELAY:
        current_frame = (current_frame + 1) % len(textures)
        last_update = now

    # Отрисовка
    screen.fill(BG_COLOR)

    # Отображение текстуры
    current_texture = textures[current_frame]
    tex_rect = current_texture.get_rect(center=(1435, HEIGHT // 2))
    screen.blit(current_texture, tex_rect)
    current_texture2 = textures2[current_frame]
    tex_rect2 = current_texture2.get_rect(center=(475, HEIGHT // 2))
    screen.blit(current_texture2, tex_rect2)
    pygame.draw.rect(screen, (255,255,255), (950,0, 10,1080))
    # Отображение FPS
    fps = clock.get_fps()
    fps_text = f"FPS: {fps:.5f}"
    fps_surface = font.render(fps_text, True, FONT_COLOR)
    fps_rect = fps_surface.get_rect(topleft=(20, 20))

    # Фон для FPS
    pygame.draw.rect(screen, (0, 0, 0), fps_rect.inflate(20, 10))
    screen.blit(fps_surface, fps_rect)

    # Обновление экрана
    pygame.display.flip()

    # Поддержание FPS
    clock.tick(FPS)

# Завершение работы
pygame.quit()
sys.exit()
