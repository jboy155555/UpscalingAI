import torch
import torch.nn as nn
import cupy as cp
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
import cv2  # Для сохранения с помощью OpenCV

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def torch_backends():
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
    torch.set_num_threads(16)
torch_backends()

# Создаем модель
models = nn.Sequential(
    nn.Conv2d(3, 3, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.Upsample(size=(1080, 1920), mode='bilinear', align_corners=False)
).to(device).half()  # Приводим модель к float16

# Пример входных данных
example_input = torch.zeros(1, 3, 256, 256, device=device, dtype=torch.float16)

# Трассируем модель
model = torch.jit.trace(models, example_input)
print("Модель успешно трассирована!")

state_dict_path = "C:/super_resolutiong.pth"
if not os.path.exists(state_dict_path):
    print(f"Файл весов {state_dict_path} не найден!")
    exit()

# Загрузка весов (параметр weights_only=True, если требуется)
state_dict = torch.load(state_dict_path, map_location=device, weights_only=True)
model.load_state_dict(state_dict, strict=False)

# Папка с исходными изображениями (предположим, они называются, например, obs1.jpeg, obs2.jpeg, ...)
screenshot_folder = "C:/Users/SoaPisGirseb/Desktop/GODD"
if not os.path.exists(screenshot_folder):
    print(f"Папка {screenshot_folder} не существует!")
    exit()

# Собираем пути к файлам с расширением .jpeg
image_paths = [
    os.path.join(screenshot_folder, f)
    for f in os.listdir(screenshot_folder)
    if f.endswith(".jpeg")
]

if not image_paths:
    print("Не найдено изображений в папке!")
    exit()

# Если нужно обработать не более batch_size изображений:
batch_size = 60
max_images_to_load = min(batch_size, len(image_paths))
image_paths = image_paths[:max_images_to_load]

# Функция для корректной сортировки по числовой части имени файла
def sort_key(path):
    basename = os.path.basename(path)
    match = re.search(r'\d+', basename)
    if match:
        return int(match.group())
    return 0

# Сортируем пути по числовой части имени файла
sorted_image_paths = sorted(image_paths, key=sort_key)

# Кэш для загруженных изображений
image_cache = {}

# Функция для загрузки и преобразования изображения
def load_and_transform(image_path):
    if image_path in image_cache:
        return image_cache[image_path]
    
    # Загрузка изображения с помощью OpenCV (BGR)
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")
    
    # Преобразование в RGB, затем в массив CuPy, перестановка осей и преобразование в float16
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_cp = cp.asarray(image_rgb).transpose(2, 0, 1).astype(cp.float16) / 255.0
    # Преобразуем CuPy массив в PyTorch тензор через DLPack
    image_tensor = torch.from_dlpack(image_cp.toDlpack())
    image_cache[image_path] = image_tensor
    return image_tensor


start_time = time.time()
def process_and_save(image_path, idx):
    # Загружаем и преобразуем изображение (на GPU)
    image_tensor = load_and_transform(image_path)
    
    # Переводим модель в режим инференса и выполняем вычисления (на GPU)
    model.eval()
    with torch.no_grad():
        output = model(image_tensor.unsqueeze(0))
    
    # Убираем размерность батча и ограничиваем значения в диапазоне [0,1]
    output = output.squeeze().clamp(0, 1)
    
    # Меняем порядок осей с (C, H, W) на (H, W, C) и масштабируем до [0, 255]
    output = output.permute(1, 2, 0).mul(255).byte()
    
    # Меняем порядок каналов с RGB на BGR (все операции остаются на GPU)
    output = output[..., [2, 1, 0]]
    
    # Преобразуем тензор на GPU в cupy-массив через DLPack.
    # Используем torch.utils.dlpack.to_dlpack для создания нового DLPack-объекта,
    # а затем cupy.from_dlpack для конвертации.
    cp_output = cp.from_dlpack(torch.utils.dlpack.to_dlpack(output))
    
    # Единожды переводим данные с GPU в CPU (один переход) для сохранения через OpenCV
    result = cp.asnumpy(cp_output)
    
    result_path = f"C:/photoes/result_{idx + 1}.jpeg"
    cv2.imwrite(result_path, result)


# Параллельная обработка и сохранение.
# Используем ThreadPoolExecutor с одним рабочим потоком, чтобы сохранялся порядок.
with ThreadPoolExecutor(max_workers=16) as executor:
    for i in range(15):    # executor.map сохраняет порядок согласно последовательности входных данных.
        
        list(executor.map(process_and_save, sorted_image_paths, range(len(sorted_image_paths))))

        print("Время выполнения:", time.time() - start_time)
