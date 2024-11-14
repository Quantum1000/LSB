from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
from psnr import calculate_mse, calculate_psnr, add_psnr, view_psnr_comparison
from hist import PDH
import numpy as np
import os
import re

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
    done = False
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
    count = 0
    done = False
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

                img[i] = (img[i] & ~(np.uint8(1) << cbit)) | ((value & (np.uint8(1) << bit)) >> bit << cbit)
                bit += 1
                count += 1
            # if the data is done being read, add a null terminator
            elif(index == len(data)):
                img[i] = img[i] & ~(np.uint8(1) << cbit)
                bit += 1
                count += 1
            else:
                done = True
                break
        cbit += 1
    bpc = (count / len(img))
    return bpc


def get_size_from_filename(name):
    match = re.search(r'(\d+)', name)  # Find the first sequence of digits in the filename
    return int(match.group()) if match else float('inf')  # Convert to integer, or use inf if no digits found


script_dir = os.path.dirname(__file__)
rel_path_template = "text_files/{size}.txt"
img = "yacht.bmp"

# Define the text_files directory path
text_files_dir = os.path.join(script_dir, "text_files")

# Loop through each file in the text_files directory
directory = sorted(os.listdir(text_files_dir), key=get_size_from_filename)
for filename in directory:
    # Check if it's a file and has the expected "KB" format
    # Check if it's a file and has the expected "KB" format
    if os.path.isfile(os.path.join(text_files_dir, filename)) and "KB" in filename:
        size = filename.split('.')[0]

        # Update the rel_path based on the file's name size
        rel_path = rel_path_template.format(size=size)

        with open(os.path.join(script_dir, rel_path), 'r', encoding='utf-8', errors='ignore') as file:
            message = file.read()
            message.encode('ascii', 'ignore').decode('ascii')
        cover = ImRead.from_file(img).pixel_array
        stego1 = np.copy(cover)
        stego2 = np.copy(cover)

        old_write_LSB(stego2, message, 2)
        ImWrite.arr_to_file(stego2, "lsb.bmp")
        old_stego = ImRead.from_file("lsb.bmp").pixel_array
        # print(old_read_LSB(stego, 1))
        # PDH(stego, old_stego)
        lsb_psnr = calculate_psnr(cover, old_stego)
        lsb_mse = calculate_mse(cover, old_stego)

        write_LSB(stego1, message)
        # print(stego1.shape)
        ImWrite.arr_to_file(stego1, "lsxb.bmp")
        stego = ImRead.from_file("lsxb.bmp").pixel_array
        # print(read_LSB(stego))
        lsxb_psnr = calculate_psnr(cover, stego)
        lsxb_mse = calculate_mse(cover, stego)

        file_size = os.path.splitext(os.path.basename(rel_path))[0]
        add_psnr(img, file_size, lsb_psnr, lsb_mse, lsxb_psnr, lsxb_mse)

view_psnr_comparison()
