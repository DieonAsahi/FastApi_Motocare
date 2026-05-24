from fastapi import FastAPI, UploadFile, File
import shutil
from ocr.model import read_odometer

app = FastAPI()


@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):

    # simpan gambar upload
    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # OCR
    hasil = read_odometer(path)

    return {
        "odometer": hasil
    }