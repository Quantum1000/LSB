
import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import math
from LSB import old_read_LSB, old_write_LSB, read_LSB, write_LSB
from bmp_io import BMPImageReader as ImRead
from bmp_io import BMPImageWriter as ImWrite
from psnr import calculate_mse, calculate_psnr, add_psnr
from hist import PDH


def get_size_from_filename(name):
    match = re.search(r'(\d+)', name)  # Find the first sequence of digits in the filename
    return int(match.group()) if match else float('inf')  # Convert to integer, or use inf if no digits found


script_dir = os.path.dirname(__file__)
rel_path_template = "text_files/{size}.txt"
img = "lakelodge.bmp"

# Define the text_files directory path
text_files_dir = os.path.join(script_dir, "text_files")

# Loop through each file in the text_files directory
df = pd.DataFrame()
directory = sorted(os.listdir(text_files_dir), key=get_size_from_filename)

def extract_text_size(filename):
    # Use list comprehension to get the numeric part before 'KB'
    size = ''.join([char for char in filename if char.isdigit()])
    return int(size) if size else 0  # Convert to integer if it's not empty, else return 0

file_list = []
for filename in directory:
    if os.path.isfile(os.path.join(text_files_dir, filename)):
        with open(os.path.join(script_dir, "text_files", filename), 'rb') as file:
            data = file.read()
        size = len(data)
        file_list.append((size, filename, data))

file_list.sort()
cover = ImRead.from_file(img).pixel_array
for (size, filename, data) in file_list:
    stego1 = np.copy(cover)
    stego2 = np.copy(cover)

    bpp = write_LSB(stego1, filename, data)
    # print(stego1.shape)
    ImWrite.arr_to_file(stego1, "lsxb.bmp")
    stego = ImRead.from_file("lsxb.bmp").pixel_array
    # print(read_LSB(stego))
    lsxb_psnr = calculate_psnr(cover, stego)
    lsxb_mse = calculate_mse(cover, stego)

    old_write_LSB(stego2, filename, data, min(int(2**math.ceil(max(0,math.log2(bpp)))),8))
    ImWrite.arr_to_file(stego2, "lsb.bmp")
    old_stego = ImRead.from_file("lsb.bmp").pixel_array
    # print(old_read_LSB(stego, 1))
    # PDH(stego, old_stego)
    lsb_psnr = calculate_psnr(cover, old_stego)
    lsb_mse = calculate_mse(cover, old_stego)
    df = add_psnr(df, img, filename, size, lsb_psnr, lsb_mse, lsxb_psnr, lsxb_mse, bpp)
print(df)

# Function to plot the PSNR comparison
def plot_psnr_comparison():
    plt.figure(figsize=(10, 6))

    # Set the x-axis to a logarithmic scale
    plt.xscale('log')
    
    # Plot the LSB PSNR values
    plt.plot(df['Size'], df['LSB_PSNR'], label='LSB PSNR', color='blue', marker='o')

    # Plot the LSXB PSNR values
    plt.plot(df['Size'], df['LSXB_PSNR'], label='LSXB PSNR', color='red', marker='x')

    # Add labels and title
    plt.xlabel('Data Size (B)')
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