import logging
import os

# Логирование
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

internal_logger = logging.getLogger("internal")
client_logger = logging.getLogger("client")

internal_log_filename = 'internal.log'
client_log_filename = 'error.log'

log_format = "%(asctime)s - %(levelname)s - %(message)s"

if not internal_logger.handlers:  # Проверяем, нет ли уже добавленных обработчиков
    internal_logger_handler = logging.FileHandler(filename=os.path.join(log_directory, internal_log_filename),
                                                  encoding='utf-8')
    internal_logger_handler.setFormatter(logging.Formatter(log_format))  # Устанавливаем формат
    internal_logger.addHandler(internal_logger_handler)
    internal_logger.setLevel(logging.DEBUG)

if not client_logger.handlers:  # Проверяем, нет ли уже добавленных обработчиков
    client_log_handler = logging.FileHandler(filename=os.path.join(log_directory, client_log_filename),
                                             encoding='utf-8')
    client_log_handler.setFormatter(logging.Formatter(log_format))  # Устанавливаем формат
    client_logger.addHandler(client_log_handler)
    client_logger.setLevel(logging.DEBUG)