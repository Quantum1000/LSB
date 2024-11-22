from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import numpy as np
from LSB import old_read_LSB, old_write_LSB, read_LSB, write_LSB
from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite



app = FastAPI()

@app.post("/old_read_lsb/")
async def api_old_read_lsb(bpp: int, image: UploadFile = File(...)):
    img = ImRead.from_file_like(image.file).pixel_array
    (filename, data) = old_read_LSB(img, bpp)
    with open(filename, "wb") as f:
        f.write(data)
    return FileResponse(filename, filename=filename)

@app.post("/old_write_lsb/")
async def api_old_write_lsb(bpp: int, data: UploadFile = File(...), image: UploadFile = File(...)):
    img = ImRead.from_file_like(image.file).pixel_array
    old_write_LSB(img, data.filename, data.file.read(), bpp)
    output_file = data.filename + ".bmp"
    ImWrite.arr_to_file(img, output_file)
    return FileResponse(output_file, filename=output_file)

@app.post("/read_lsb/")
async def api_read_lsb(image: UploadFile = File(...)):
    img = ImRead.from_file_like(image.file).pixel_array
    (filename, data) = read_LSB(img)
    with open(filename, "wb") as f:
        f.write(data)
    return FileResponse(filename, filename=filename)

@app.post("/write_lsb/")
async def api_write_lsb(data: UploadFile = File(...), image: UploadFile = File(...)):
    img = ImRead.from_file_like(image.file).pixel_array
    write_LSB(img, data.filename, data.file.read())
    output_file = data.filename + ".bmp"
    ImWrite.arr_to_file(img, output_file)
    return FileResponse(output_file, filename=output_file)


