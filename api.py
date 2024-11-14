from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import numpy as np
from PIL import Image
from LSB import old_read_LSB, old_write_LSB, read_LSB, write_LSB

app = FastAPI()

@app.post("/old_read_lsb/")
async def api_old_read_lsb(bpp: int, file: UploadFile = File(...)):
    img = np.array(Image.open(file.file))
    data = old_read_LSB(img, bpp)
    return {"data": data}

@app.post("/old_write_lsb/")
async def api_old_write_lsb(bpp: int, data: str, file: UploadFile = File(...)):
    img = np.array(Image.open(file.file))
    old_write_LSB(img, data, bpp)
    return {"message": "data written using old LSB"}

@app.post("/read_lsb/")
async def api_read_lsb(file: UploadFile = File(...)):
    img = np.array(Image.open(file.file))
    data = read_LSB(img)
    return {"data": data}

@app.post("/write_lsb/")
async def api_write_lsb(data: str, file: UploadFile = File(...)):
    img = np.array(Image.open(file.file))
    write_LSB(img, data)
    return {"message": "data written using new lsb"}

