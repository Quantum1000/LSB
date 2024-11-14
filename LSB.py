from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
from psnr import calculate_mse, calculate_psnr, add_psnr
from hist import PDH
import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import math

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


def get_size_from_filename(name):
    match = re.search(r'(\d+)', name)  # Find the first sequence of digits in the filename
    return int(match.group()) if match else float('inf')  # Convert to integer, or use inf if no digits found


script_dir = os.path.dirname(__file__)
rel_path_template = "text_files/{size}.txt"
img = "yacht.bmp"

# Define the text_files directory path
text_files_dir = os.path.join(script_dir, "text_files")

# Loop through each file in the text_files directory
df = pd.DataFrame()
directory = sorted(os.listdir(text_files_dir), key=get_size_from_filename)

def extract_text_size(filename):
    # Use list comprehension to get the numeric part before 'KB'
    size = ''.join([char for char in filename if char.isdigit()])
    return int(size) if size else 0  # Convert to integer if it's not empty, else return 0

for filename in directory:
    # Check if it's a file and has the expected "KB" format
    if os.path.isfile(os.path.join(text_files_dir, filename)) and "KB" in filename:
        size = filename.split('.')[0]

        # Update the rel_path based on the file's name size
        rel_path = rel_path_template.format(size=size)

        with open(os.path.join(script_dir, rel_path), 'rb') as file:
            message = file.read()
        cover = ImRead.from_file(img).pixel_array
        stego1 = np.copy(cover)
        stego2 = np.copy(cover)

        bpp = write_LSB(stego1, size+".txt", message)
        # print(stego1.shape)
        ImWrite.arr_to_file(stego1, "lsxb.bmp")
        stego = ImRead.from_file("lsxb.bmp").pixel_array
        # print(read_LSB(stego))
        lsxb_psnr = calculate_psnr(cover, stego)
        lsxb_mse = calculate_mse(cover, stego)

        old_write_LSB(stego2, size+".txt", message, min(int(math.ceil(math.sqrt(bpp))**2),8))
        ImWrite.arr_to_file(stego2, "lsb.bmp")
        old_stego = ImRead.from_file("lsb.bmp").pixel_array
        # print(old_read_LSB(stego, 1))
        # PDH(stego, old_stego)
        lsb_psnr = calculate_psnr(cover, old_stego)
        lsb_mse = calculate_mse(cover, old_stego)

        file_size = os.path.splitext(os.path.basename(rel_path))[0]
        df = add_psnr(df, img, file_size, lsb_psnr, lsb_mse, lsxb_psnr, lsxb_mse)
print(df)

# Function to plot the PSNR comparison
def plot_psnr_comparison():
    """Plot a line chart comparing LSB vs LSXB PSNR values."""
    plt.figure(figsize=(10, 6))

    # Ensure 'Text_Size' is numeric (use the extract_text_size function to convert them)
    df['Text_Size'] = df['Text_Size'].apply(extract_text_size)

    # Set the x-axis to a logarithmic scale
    plt.xscale('log')
    
    # Plot the LSB PSNR values
    plt.plot(df['Text_Size'], df['LSB_PSNR'], label='LSB PSNR', color='blue', marker='o')

    # Plot the LSXB PSNR values
    plt.plot(df['Text_Size'], df['LSXB_PSNR'], label='LSXB PSNR', color='red', marker='x')

    # Add labels and title
    plt.xlabel('Text Size (KB)')
    plt.ylabel('PSNR (dB)')
    plt.title('PSNR Comparison between LSB and LSXB')

    # Display the legend
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Call the function to plot the PSNR comparison chart
plot_psnr_comparison()

