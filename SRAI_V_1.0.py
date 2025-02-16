import torch
import torch.nn as nn
import cupy as cp
import os
import time
from concurrent.futures import ThreadPoolExecutor
import cv2  # Сохранение с помощью OpenCV

# Устройство для вычислений
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Используем устройство: {device}")

# Установка типа тензоров по умолчанию
def torch_backends():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    torch.backends.mkl.enabled = True
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.cufft_plan_cache_enabled = True
    torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction = True
    torch.set_num_threads(16)
    torch.backends.cudnn.deterministic = False
torch_backends()

# Определение модели
NewCNN = nn.Sequential(
    nn.Conv2d(3, 3, 3, 1, padding=1),
    nn.ReLU(),
).to(device).half()

# Оптимизация модели с использованием TorchScript
example_input = torch.zeros(1, 3, 256, 256).to(device).half()  # Пример входного тензора
model = torch.jit.trace(NewCNN, example_input)  # Трассировка модели для оптимизации

# Загрузка весов модели
state_dict_path = "C:/model_weights.pth"
if not os.path.exists(state_dict_path):
    print(f"Файл весов {state_dict_path} не найден!")
    exit()

state_dict = torch.load(state_dict_path, map_location=device, weights_only=True)
model.load_state_dict(state_dict, strict=False)

# Папка с изображениями
screenshot_folder = "C:/screenshots"
if not os.path.exists(screenshot_folder):
    print(f"Папка {screenshot_folder} не существует!")
    exit()
image_paths = [os.path.join(screenshot_folder, f) for f in os.listdir(screenshot_folder) if f.endswith(".jpeg")]

if not image_paths:
    print("Не найдено изображений в папке!")
    exit()

# Параметры обработки
batch_size = 10
max_images_to_load = batch_size  # Максимальное количество изображений для загрузки

# Кэш для загруженных изображений
image_cache = {}

# Функция для загрузки и преобразования изображения
def load_and_transform(image_path):
    if image_path in image_cache:
        return image_cache[image_path]

    image = cv2.imread(image_path)  # OpenCV загружает BGR
    image = cp.asarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).transpose(2, 0, 1).astype(cp.float16) / 255.0
    image_tensor = torch.tensor(image, device=device)  # Переносим CuPy массив в PyTorch тензор
    image_cache[image_path] = image_tensor
    return image_tensor

starttime = time.time()

# Функция для обработки и сохранения одного изображения
# Функция для обработки и сохранения одного изображения
def process_and_save(image_path, idx):
    # Загрузка и преобразование изображения
    image_tensor = load_and_transform(image_path)

    # Инференс
    model.eval()
    with torch.no_grad():
        output = model(image_tensor.unsqueeze(0))

    # Преобразуем тензор в формат [0, 255] на GPU
    output = output.squeeze().cpu().detach().clamp(0, 1)  # Ограничиваем значения в пределах [0, 1]
    output = output.permute(1, 2, 0).mul(255).byte()  # Преобразуем в формат [0, 255] и RGB

    # Переносим изображение на CPU для сохранения с помощью OpenCV
    output_cpu = output.cpu().numpy()  # Переносим в массив NumPy для OpenCV
    output_bgr = cv2.cvtColor(output_cpu, cv2.COLOR_RGB2BGR)  # Преобразуем в формат BGR

    # Сохраняем изображение
    result_path = f"C:/photoes/result_{idx + 1}.jpeg"
    cv2.imwrite(result_path, output_bgr)  # Сохраняем изображение в формате JPEG

    

# Параллельная обработка и сохранение
with ThreadPoolExecutor(max_workers=16) as executor:
    for i in range(3):
        starttime = time.time()
        executor.map(process_and_save, image_paths[:max_images_to_load], range(len(image_paths)))

print("Время выполнения:", time.time() - starttime)
