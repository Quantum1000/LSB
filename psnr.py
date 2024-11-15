import numpy as np
import pandas as pd
import math

df = pd.DataFrame(columns=["Image", "Text_Size", "LSB_PSNR", "LSXB_PSNR", "Difference"])


def calculate_mse(image1, image2):
    """Calculate the Mean Squared Error (MSE) between two images."""
    return np.mean((image1 - image2) ** 2)

def calculate_psnr(original, stego):
    """Calculate the PSNR between two images."""
    mse = calculate_mse(original, stego)
    if mse == 0:  # Means the images are identical
        return float('inf')
    MAX_PIXEL_VALUE = 255.0  # For 8-bit images
    psnr = 10 * math.log10((MAX_PIXEL_VALUE ** 2) / mse)
    return psnr


def add_psnr(df, image, filename, size, lsb_psnr, lsb_mse, lsxb_psnr, lsxb_mse, bpp):
    """Add the PSNR comparisons of LSB and LSXB implementation to df"""
    psnr_difference = lsb_psnr - lsxb_psnr

    data = pd.DataFrame({
        "Image": [image],
        "File": [filename],
        "Size": [size],
        "LSB_PSNR": [lsb_psnr],
        "LSXB_PSNR": [lsxb_psnr],
        "LSB_MSE": [lsb_mse],
        "LSXB_MSE": [lsxb_mse],
        "Difference": [psnr_difference],
        "BPP": [bpp],
        "Old_BPP": [min(int(2**math.ceil(max(0,math.log2(bpp)))),8)]
    })
    return pd.concat([df, data], ignore_index=True)

