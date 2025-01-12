from pyzbar.pyzbar import decode
from PIL import Image
import io

def read_barcode(image_bytes):
    # Открываем изображение из байтов
    image = Image.open(io.BytesIO(image_bytes))
    
    # Используем pyzbar для поиска штрих-кодов на изображении
    barcodes = decode(image)
    
    # Перебираем найденные штрих-коды
    for barcode in barcodes:
        # Извлекаем информацию о штрих-коде
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type
        
        # Возвращаем информацию
        return {
            'type': barcode_type,
            'data': barcode_data
        }
    return None


# Пример использования
# image_path = "barcode/photo_2024-09-15_18-32-54.jpg"
# print(read_barcode(image_path))