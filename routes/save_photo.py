import os
import shutil
from fastapi import UploadFile, HTTPException


# Функция для сохранения файла
async def save_file(file: UploadFile, folder: str = "photo") -> str:
    try:
        # Создаем папку, если она не существует
        os.makedirs(folder, exist_ok=True)

        # Генерируем уникальное имя файла
        file_name = file.filename
        file_path = os.path.join(folder, file_name)

        # Если файл с таким именем уже существует, добавляем числовой суффикс
        counter = 1
        while os.path.exists(file_path):
            name, extension = os.path.splitext(file_name)
            file_name = f"{name}_{counter}{extension}"
            file_path = os.path.join(folder, file_name)
            counter += 1

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Возвращаем только имя файла
        return file_name
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not save file: {str(e)}")
