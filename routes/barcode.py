from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from models.barcode_model import BarcodeResponse
from fastapi.responses import JSONResponse
from barcode.barcode import read_barcode
import uuid
import os


barcode_router = APIRouter()


@barcode_router.post("/read-barcode/", response_model=BarcodeResponse)
async def read_barcode_api(file: UploadFile = File(...)):
    try:
        # Читаем содержимое файла в байты
        contents = await file.read()

        # Обрабатываем изображение
        result = read_barcode(contents)

        if result:
            return BarcodeResponse(**result)
        else:
            return JSONResponse(content={"message": "No barcode found in the image", "status": False}, status_code=404)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
