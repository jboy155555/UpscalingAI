import time
import threading
import os
from queue import Queue
from obswebsocket import obsws, requests
from PIL import Image  # Импортируем Pillow для работы с изображениями

# Параметры подключения OBS
host = "127.0.0.1"
port = 4455
password = "gagunime7"

# Количество рабочих потоков (каждый со своим соединением)
worker_count = 4

# Очередь задач: каждая задача – кортеж (номер_скриншота,)
task_queue = Queue()

# Папка, где будет сохраняться скриншоты
save_folder = "C:/screenshots"

def worker_func(worker_id):
    """
    Рабочий поток: создаёт собственное соединение с OBS
    и обрабатывает задачи из очереди.
    При получении None завершается.
    """
    ws_local = obsws(host, port, password)
    ws_local.connect()
    while True:
        task = task_queue.get()
        if task is None:
            task_queue.task_done()
            break
        (frame_num,) = task  # номер скриншота
        image_path = os.path.join(save_folder, f"obs{frame_num}.jpeg")
        
        # Сохранение скриншота через OBS
        response = ws_local.call(requests.SaveSourceScreenshot(
            sourceName="neiro_v1",
            imageFormat="jpeg",
            imageQuality=100,
            imageFilePath=image_path
        ))
        if not response.status:
            print(f"Ошибка при сохранении {frame_num}: {response.datain}")
        else:
            # После сохранения выполняем resize с помощью Pillow
            try:
                # Открываем изображение
                img = Image.open(image_path)
                # Изменяем размер до 1920x1080 (замените размеры, если нужно другое значение)
                resized_img = img.resize((640, 360), Image.LANCZOS)
                # Сохраняем изображение (перезаписываем оригинал)
                resized_img.save(image_path)
            except Exception as e:
                print(f"Ошибка при изменении размера изображения {image_path}: {e}")
        task_queue.task_done()
    ws_local.disconnect()

def main():
    repetitions = 10       # Повторить процесс 10 раз (10 секунд)
    capture_count = 60     # 60 скриншотов за 1 секунду
    time_per_frame = 1 / capture_count  # Интервал между кадрами (секунда)
    total_frames = repetitions * capture_count

    # Запуск рабочих потоков
    workers = []
    for i in range(worker_count):
        t = threading.Thread(target=worker_func, args=(i,))
        t.start()
        workers.append(t)
    
    global_frame = 1
    start_time = time.time()
    
    # Для каждого "секундного блока" ставим задачи на 60 скриншотов
    for rep in range(repetitions):
        rep_start = time.time()
        for i in range(capture_count):
            task_queue.put((global_frame,))
            global_frame += 1
            
            # Ждём, пока не наступит время следующего кадра
            elapsed = time.time() - rep_start
            target = time_per_frame * (i + 1)
            remaining = target - elapsed
            if remaining > 0:
                time.sleep(remaining)
        
        # Ждём, пока все задачи текущего блока будут выполнены
        task_queue.join()
        rep_elapsed = time.time() - rep_start
        print(f"Репетиция {rep+1}: Захвачено {capture_count} изображений за {rep_elapsed:.3f} секунд")
    
    # Останавливаем рабочих: для каждого рабочего кладём в очередь None
    for _ in range(worker_count):
        task_queue.put(None)
    for t in workers:
        t.join()
    
    total_elapsed = time.time() - start_time
    print(f"Общее время: {total_elapsed:.3f} секунд, всего изображений: {total_frames}")

if __name__ == "__main__":
    main()
