import aiohttp, aiofiles, json, logging, os, asyncio
from urllib.parse import urlparse
import aiohttp.client_exceptions
from aiohttp.log import client_logger, internal_logger


semaphore = asyncio.Semaphore(20)
    

# ссылка на скачивание
async def extract_file_id(gdrive_link):
    try:
        parsed_url = urlparse(gdrive_link)
        path_parts = parsed_url.path.split('/')
        
        if len(path_parts) <= 3: 
            client_logger.error(f"Error URL: {gdrive_link}")
            return None
        
        file_id = path_parts[3]
        download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        internal_logger.info(f"Success extract_file_id: {download_link}")
        # print(download_link)
        return download_link
    
    except Exception as e:
        client_logger.error(f"Error parsing URL: {e}")
        return None


# скачать фото
async def download_foto(download_link):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(download_link) as resp:
                if resp.status == 200:
                    file_content = await resp.read()
                    content_dir = "uploads"
                    if not os.path.exists(content_dir):
                        os.makedirs(content_dir)
                    temp_file_path = os.path.join(content_dir, 'photo.jpg')

                    with open(temp_file_path, 'wb') as temp_file:
                        temp_file.write(file_content)
                        print(f"Файл скачан: {temp_file_path}")

                    return temp_file_path
                
                else:
                    client_logger.error(f"Error Download Photo: {resp.status}")
                    return None
                
    except Exception as e:
        client_logger.error(f"Error Download Photo: {e}")
        return None


# отправить фото
async def send_photo_to_chat(chat_id, file_path, token, caption, keyboard=None):
    async with semaphore:
        #start = (datetime.now())
        #print(f"Поток: {semaphore}")
        #print("Пауза 2 секунды")
        try:
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open(file_path, 'rb') as photo:
                    photo_bytes = await photo.read()

                data = aiohttp.FormData()
                data.add_field(name='chat_id', value=str(chat_id))
                data.add_field(name='photo', value=photo_bytes, filename='photo.jpg', content_type='image/jpeg')
                data.add_field(name='caption', value=caption)
                if keyboard is not None:
                    keyboard_json = json.dumps(keyboard)
                    data.add_field(name='reply_markup', value=keyboard_json, content_type='application/json')
                url = f'https://api.telegram.org/bot{token}/sendPhoto'
                # print("Отправляю сообщение на чат: ", chat_id,)
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        response.raise_for_status()
                        internal_logger.info(f"{chat_id}: Success")
                        print(f"Success: {chat_id}")

                        await asyncio.sleep(1)
                    else:
                        error_message = await response.text()
                        client_logger.error(f"{chat_id}: {error_message}")
                        print(f"Error:{chat_id}: {error_message}")
                        return False
                #end = (datetime.now()) 
                #difference = end - start
                #seconds_difference = difference.total_seconds()
                #print(f"Прошло: {seconds_difference} секунд")

                return True
        except Exception as e:
            error_message = await response.text()
            client_logger.error(f"{chat_id}: {error_message}")
            print(f"Error:{chat_id}: {error_message}")
            return False



# асинхронная функция для отправки фотографий всем указанным чатам
async def send_photo(chat_ids, file_path, token, caption, keyboard):
    # Списки для хранения результатов
    errors = []
    success_count = 0
    error_ids = []
    # сессия для HTTP-запросов
    async with aiohttp.ClientSession() as session:
        # очередь
        queue = asyncio.Queue()
        #print ("queue", queue)
        for chat_id in chat_ids:
            # создаем задачу
            task = asyncio.create_task(send_photo_to_chat(chat_id, file_path, token, caption, keyboard))
            internal_logger.info(f"{task}")

            # Добавляем задачу в очередь
            await queue.put(task)
        
        # извлекаем задачи и выполняем их асинхронно
        while not queue.empty():
            task = await queue.get()
            # получаем результат
            try:
                result = await task
                # ошибка
                if result is False:
                    errors.append(chat_id)
                    error_ids.append(chat_id)
                else:
                    # успех
                    success_count += 1
            # исключение
            except Exception as e:
                client_logger.error(f"{chat_id}: Error in send_photo: {e}")
                errors.append(chat_id)
                error_ids.append(chat_id)

        result = {
                'successCount': success_count,
                'errorCount': len(errors),
            }
        internal_logger.error(f"{result}")

        return result