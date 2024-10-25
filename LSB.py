from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
from psnr import calculate_mse, calculate_psnr
from hist import PDH
import numpy as np
import os


def read_LSB(img):
    count = 0
    output = 0
    string = ""
    bit = 0
    for row in img:
        for col in row:
            for color in col:
                if (bit >= 8):
                    string += chr(output)
                    output = 0
                    bit = 0
                    count += 1
                if (len(string) != 0 and ord(string[-1]) == 0):
                    break
                output = output | (color & 1) << bit
                bit += 1
    return string


def write_LSB(img, data):
    index = 0
    bit = 0
    for i in range(len(img)):
        for j in range(len(img[i])):
            for k in range(len(img[i, j])):
                if (bit >= 8):
                    index += 1
                    bit = 0

                if (index < len(data)):
                    char = data[index]
                    if isinstance(char, str) and ord(char) <= 255:
                        value = ord(char)
                    else:
                        value = ord("'")  # use (') as default value for non-ASCII characters

                    img[i, j, k] = (img[i, j, k] & ~np.uint8(1)) | ((value & (np.uint8(1) << bit)) >> bit)
                    bit += 1

                elif (index == len(data)):
                    img[i, j, k] = img[i, j, k] & ~np.uint8(1)
                    bit += 1

                else:
                    break


script_dir = os.path.dirname(__file__)
rel_path = "text_files/50KB.txt"

with open(os.path.join(script_dir, rel_path), 'r', encoding='utf-8', errors='ignore') as file:
    message = file.read()
    message.encode('ascii', 'ignore').decode('ascii')
cover = ImRead.from_file("yacht.bmp").pixel_array
stego = np.copy(cover)
write_LSB(stego, message)
ImWrite.arr_to_file(stego, "new.bmp")
stego = ImRead.from_file("new.bmp").pixel_array
print(read_LSB(stego))
PDH(cover, stego)
calculate_psnr(cover, stego)
