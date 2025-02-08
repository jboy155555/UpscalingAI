import ctypes
import psutil
import time
import keyboard

user32 = ctypes.windll.user32

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

def get_hwnd_from_pid(pid):
    hwnds = []
    
    def callback(hwnd, lParam):
        found_pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(found_pid))
        if found_pid.value == pid:
            hwnds.append(hwnd)
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(EnumWindowsProc(callback), 0)
    
    return hwnds[0] if hwnds else None

# Введи PID игры вручную
game_pid = 9900  # Замени на свой PID
hwnd = get_hwnd_from_pid(game_pid)

# Состояния для каждой клавиши
key_d_pressed = False
key_a_pressed = False
key_w_pressed = False
key_s_pressed = False

# Функция отправки клавиши
def send_key(hwnd, keycode):
    user32.PostMessageW(hwnd, WM_KEYDOWN, keycode, 0)
    time.sleep(0.01)
    user32.PostMessageW(hwnd, WM_KEYUP, keycode, 0)

# Обработчики клавиш
def on_key_a():
    global key_a_pressed
    if not key_a_pressed:  # Если клавиша A еще не была нажата
        print("Нажата клавиша A!")
        send_key(hwnd, 0x41)  # Код клавиши 'A'
        key_a_pressed = True  # Устанавливаем флаг, чтобы не повторять

def on_key_d():
    global key_d_pressed
    if not key_d_pressed:  # Если клавиша D еще не была нажата
        print("Нажата клавиша D!")
        send_key(hwnd, 0x44)  # Код клавиши 'D'
        key_d_pressed = True  # Устанавливаем флаг, чтобы не повторять

def on_key_w():
    global key_w_pressed
    if not key_w_pressed:  # Если клавиша W еще не была нажата
        print("Нажата клавиша W!")
        send_key(hwnd, 0x57)  # Код клавиши 'W'
        key_w_pressed = True  # Устанавливаем флаг, чтобы не повторять

def on_key_s():
    global key_s_pressed
    if not key_s_pressed:  # Если клавиша S еще не была нажата
        print("Нажата клавиша S!")
        send_key(hwnd, 0x53)  # Код клавиши 'S'
        key_s_pressed = True  # Устанавливаем флаг, чтобы не повторять
off = False
# Если клавиша зажата, отправляем повторяющиеся события
def on_key_held(keycode, key_name):
    print(f"Клавиша {key_name} удерживается")
    send_key(hwnd, keycode)  # Отправляем клавишу каждый раз

# Функция для сброса флагов
def on_combo():
    global off
    off = True
    print('awdawddwa')

# Проверяем, что hwnd найдено
if hwnd:
    while True:
        
        keyboard.add_hotkey('a', on_key_a)  # Обработка клавиши A
        keyboard.add_hotkey('d', on_key_d)  # Обработка клавиши D
        keyboard.add_hotkey('w', on_key_w)  # Обработка клавиши W
        keyboard.add_hotkey('s', on_key_s)  # Обработка клавиши S
        keyboard.add_hotkey('right altdaswd', on_combo)  # Сброс флагов

        # Для удерживаемых клавиш, например, зажимаем D
        if keyboard.is_pressed('a'):
            on_key_held(0x41, 'A')
        if keyboard.is_pressed('d'):
            on_key_held(0x44, 'D')
        if keyboard.is_pressed('w'):
            on_key_held(0x57, 'W')
        if keyboard.is_pressed('s'):
            on_key_held(0x53, 'S')
        if off == True:
            break
        time.sleep(0.01)  # Добавляем небольшую задержку, чтобы не перегружать процессор
