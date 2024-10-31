from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
from psnr import calculate_mse, calculate_psnr
from hist import PDH
import numpy as np
import os
seed = 42

# Requires bpp to be a power of 2
def old_read_LSB(img, bpp):
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
                output = output | (color & (2**bpp-1)) << bit
                bit += bpp
    return string


# Requires bpp to be a power of 2
def old_write_LSB(img, data, bpp):
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

                    img[i, j, k] = (img[i, j, k] & ~np.uint8((2**bpp-1))) | ((value & (np.uint8((2**bpp-1)) << bit)) >> bit)
                    bit += bpp

                elif(index == len(data)):
                    img[i,j,k] = img[i,j,k] & ~np.uint8((2**bpp-1))
                    bit += bpp

                else:
                    break


def read_LSB(img):
    output = 0
    string = ""
    bit = 0
    cbit = 0
    maxi = 0
    done = False
    shape = img.shape
    img = img.reshape((-1))
    rng = np.random.default_rng(seed=seed)
    indices = rng.permutation(len(img))
    while cbit <= 8 and not done:
        for i in indices:
            if(bit >= 8):
                string+=chr(output)
                output = 0
                bit = 0
            if(len(string) != 0 and ord(string[-1]) == 0):
                maxi = i
                done = True
                break
            output = output | (img[i] & 1 << cbit) >> cbit << bit
            bit += 1
        cbit += 1
    return string


def write_LSB(img, data):
    index = 0
    output = 0
    string = ""
    bit = 0
    cbit = 0
    maxi = 0
    done = False
    shape = img.shape
    img = img.reshape((-1))
    rng = np.random.default_rng(seed=seed)
    indices = rng.permutation(len(img))
    while cbit <= 8 and not done:
        for i in indices:
            if(bit >= 8):
                index += 1
                bit = 0
            if(index < len(data)):
                char = data[index]
                if isinstance(char, str) and ord(char) <= 255:
                    value = ord(char)
                else:
                    value = ord("'")  # use (') as default value for non-ASCII characters

                img[i] = (img[i] & ~np.uint8(1) << cbit) | ((value & (np.uint8(1) << bit)) >> bit << cbit)
                bit += 1
            # if the data is done being read, add a null terminator
            elif(index == len(data)):
                img[i] = img[i] & ~np.uint8(1) << cbit
                bit += 1
            else:
                done = True
                maxi = i
                break
        cbit += 1
    bpc = (cbit + maxi / len(img))
    return bpc
    
        

script_dir = os.path.dirname(__file__)
rel_path = "text_files/156KB.txt"

with open(os.path.join(script_dir, rel_path), 'r', encoding='utf-8', errors='ignore') as file:
    message = file.read()
    #print(message.encode('ascii', 'ignore').decode('ascii'))
cover = ImRead.from_file("yacht.bmp").pixel_array
stego = np.copy(cover)
print(write_LSB(stego, message))
print(stego.shape)
ImWrite.arr_to_file(stego, "new.bmp")
stego = ImRead.from_file("new.bmp").pixel_array
print(read_LSB(stego))
PDH(cover, stego)
print(calculate_psnr(cover, stego))