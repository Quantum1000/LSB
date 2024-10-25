import numpy as np

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