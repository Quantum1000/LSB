from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
from psnr import calculate_mse, calculate_psnr, add_psnr
from hist import PDH
import pandas as pd
import numpy as np
import os
import re

seed = 42

# Requires bpp to be a power of 2
def old_read_LSB(img, bpp):
    count = 0
    output = 0
    filename = ""
    data = bytearray()
    lenlen = 0
    length = 0
    bit = 0
    stage = 0
    for row in img:
        for col in row:
            for color in col:
                if (bit >= 8):
                    data += int(output).to_bytes(1, "little")
                    output = 0
                    bit = 0
                    count += 1
                # In the first stage, the file name is read
                if(stage == 0):
                    if(len(data) != 0 and data[-1] == 0):
                        filename = data.decode("utf-8")
                        data = bytearray()
                        stage = 1
                # The second stage reads one byte to figure out how many length bytes it will read
                elif(stage == 1):
                    if(bit == 0):
                        lenlen = int.from_bytes(data, "little")
                        data = bytearray()
                        stage = 2
                # The third stage reads lenlen bytes to know how large the data is
                elif(stage == 2):
                    if(len(data) == lenlen):
                        length = int.from_bytes(data, "little")
                        data = bytearray()
                        stage = 3
                # The fourth stage reads length bytes of data
                elif(stage == 3):
                    if(len(data) == length):
                        done = True
                        break
                output = output | (color & (2**bpp-1)) << bit
                bit += bpp
    return (filename, data)


# Requires bpp to be a power of 2
def old_write_LSB(img, filename, data, bpp):
    index = 0
    bit = 0
    filename = filename + chr(0)
    # absurdity check
    assert((len(data).bit_length()+7)//8 < 256)
    length = len(data).to_bytes((len(data).bit_length()+7)//8, "little")
    lenlen = len(length).to_bytes(1, "little")
    output = filename.encode('utf-8') + lenlen + length + data
    for i in range(len(img)):
        for j in range(len(img[i])):
            for k in range(len(img[i, j])):
                if (bit >= 8):
                    index += 1
                    bit = 0
                if(index >= len(output)):
                    done = True
                    break
                img[i, j, k] = (img[i, j, k] & ~np.uint8((2**bpp-1))) | ((output[index] & (np.uint8((2**bpp-1)) << bit)) >> bit)
                bit += bpp


def read_LSB(img):
    output = 0
    data = bytearray()
    filename = ""
    bit = 0
    cbit = 0
    done = False
    img = img.reshape((-1))
    rng = np.random.default_rng(seed=seed)
    indices = rng.permutation(len(img))
    stage = 0
    lenlen = 0
    length = 0
    while cbit <= 8 and not done:
        for i in indices:
            if(bit >= 8):
                data+=int(output).to_bytes(1, "little")
                output = 0
                bit = 0
            # In the first stage, the file name is read
            if(stage == 0):
                if(len(data) != 0 and data[-1] == 0):
                    filename = data.decode("utf-8")
                    data = bytearray()
                    stage = 1
            # The second stage reads one byte to figure out how many length bytes it will read
            elif(stage == 1):
                if(bit == 0):
                    lenlen = int.from_bytes(data, "little")
                    data = bytearray()
                    stage = 2
            # The third stage reads lenlen bytes to know how large the data is
            elif(stage == 2):
                if(len(data) == lenlen):
                    length = int.from_bytes(data, "little")
                    data = bytearray()
                    stage = 3
            # The fourth stage reads length bytes of data
            elif(stage == 3):
                if(len(data) == length):
                    done = True
                    break
            output = output | (img[i] & 1 << cbit) >> cbit << bit
            bit += 1
        cbit += 1
    return (filename, data)


def write_LSB(img, filename, data):
    # make the filename null terminated
    filename = filename + chr(0)
    index = 0
    string = ""
    bit = 0
    cbit = 0
    done = False
    img = img.reshape((-1))
    rng = np.random.default_rng(seed=seed)
    indices = rng.permutation(len(img))
    # absurdity check
    assert((len(data).bit_length()+7)//8 < 256)
    length = len(data).to_bytes((len(data).bit_length()+7)//8, "little")
    lenlen = len(length).to_bytes(1, "little")
    output = filename.encode('utf-8') + lenlen + length + data
    while cbit <= 8 and not done:
        for i in indices:
            if(bit >= 8):
                index += 1
                bit = 0
            if(index >= len(output)):
                done = True
                break
            img[i] = (img[i] & ~(np.uint8(1) << cbit)) | ((output[index] & (np.uint8(1) << bit)) >> bit << cbit)
            bit += 1
        cbit += 1
    bpc = (index*8 / len(img))
    return bpc

with open("LSBtest.webp", "rb") as file:
    data = file.read()

image = ImRead.from_file("yacht.bmp").pixel_array
img = image.copy()
old_write_LSB(img, "LSBTest3.webp", data, 1)
print(ImWrite.arr_to_file(img, "new.bmp"))
img = ImRead.from_file("new.bmp").pixel_array
(filename, data) = old_read_LSB(img, 1)
with open(filename[:-1], "wb") as file:
    file.write(data)