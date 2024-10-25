from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
import numpy as np

def read_LSB(img):
    count = 0
    output = 0
    string = "Message: "
    bit = 0
    for row in img:
        for col in row:
            for color in col:
                if(bit >= 8):
                    string+=chr(output)
                    output = 0
                    bit = 0
                    count += 1
                if(ord(string[-1]) == 0):
                    break
                output = output | (color & 1) << bit
                bit += 1
    print(string)


def write_LSB(img, data):
    index = 0
    bit = 0
    for i in range(len(img)):
        for j in range(len(img[i])):
            for k in range(len(img[i,j])):
                if(bit >= 8):
                    index += 1
                    bit = 0

                if(index < len(data)):
                    char = data[index]
                    if isinstance(char, str) and ord(char) <= 255:
                        value = ord(char)
                    else:
                        value = ord("'")  # use (') as default value for non-ASCII characters

                    img[i, j, k] = (img[i, j, k] & ~np.uint8(1)) | ((value & (np.uint8(1) << bit)) >> bit)
                    bit += 1

                elif(index == len(data)):
                    img[i,j,k] = img[i,j,k] & ~np.uint8(1)
                    bit += 1

                else:
                    break


with open('message.txt', 'r', encoding='utf-8', errors='ignore') as file:
    message = file.read()
    print(message.encode('ascii', 'ignore').decode('ascii'))

original_image = ImRead.from_file("new.bmp").pixel_array
stego_image = np.copy(original_image)
write_LSB(stego_image, message)
ImWrite.arr_to_file(stego_image, "new_stego.bmp")
img = ImRead.from_file("new.bmp").pixel_array
read_LSB(stego_image)
