import pygetwindow as gw
import pyautogui

# Найти окно игры (замените 'Choo-Choo Charles' на точное название окна)
game_window = None
for window in gw.getWindowsWithTitle('Choo-Choo Charles'):
    if 'Choo-Choo Charles' in window.title:
        game_window = window
        break

if game_window:
    # Задать размеры окна 640x360 (изменяется равномерно, без обрезки)
    game_window.resizeTo(640, 360)

    # Переместить окно в центр экрана
    screen_width, screen_height = pyautogui.size()
    game_window.moveTo((screen_width - 640) // 2, (screen_height - 360) // 2)

    print("Окно успешно уменьшено!")
else:
    print("Игра не найдена. Убедитесь, что она запущена.")
