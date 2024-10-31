import numpy as np
import struct

BMP_FILE_HEADER_SIZE = 14       # First 14 bytes of BMP file represents the file header
DIB_HEADER_SIZE = 40            # next 40 bytes after file header represents dib header or BITMAPINFOHEADER
NO_OF_COLOR_PLANES = 1          # always 1
BPP_VALUE = 24                  # Bits per pixel = 24
COMPRESSION_VALUE = 0           # 0 signifies no compression -> maintains BGR encoding
COLORS_IN_PALETTE = 0           # 0 defaults to 2^n
NO_OF_IMPORTANT_COLORS = 0      # 0 signifies all colors are important
HORIZONTAL_RESOLUTION = 2835    # pixels/meter
VERTICAL_RESOLUTION = 2835      # pixels/meter
TOTAL_HEADER_SIZE = 54          # Dib header size + file header size


class BMPImageReader:
    def __init__(self, pixel_array):
        self.pixel_array = pixel_array  # NumPy array of shape (height, width, 3) for BGR channels

    @staticmethod
    def from_file(file_path):
        with open(file_path, 'rb') as f:
            file_header = f.read(BMP_FILE_HEADER_SIZE)
            file_type, file_size, reserved1, reserved2, offset = struct.unpack('<2sIHHI', file_header)
            assert file_type == b'BM', "Not a valid BMP file!"

            dib_header = f.read(DIB_HEADER_SIZE)
            header_size, width, height, planes, bpp, compression, img_size, h_res, v_res, num_colors, imp_colors = \
                struct.unpack('<IIIHHIIIIII', dib_header)
            assert bpp == BPP_VALUE, "Only 24-bit BMP files are supported!"

            # Read pixel data
            f.seek(offset)  # Move to the start of pixel data
            row_padded = (width * 3 + 3) & ~3  # Row size padded to 4 bytes
            pixel_data = []

            for y in range(height):
                row = np.frombuffer(f.read(row_padded), dtype=np.uint8)[:width * 3]
                row = row.reshape((width, 3))  # Convert row into shape (width, 3) for B, G, R
                pixel_data.append(row)

            # Convert the list of rows into a NumPy array
            pixel_array = np.array(pixel_data, dtype=np.uint8)

        return BMPImageReader(pixel_array)

    def get_pixel(self, x, y):
        """Get the pixel at (x, y) as a tuple of regular integers (B, G, R)."""
        pixel = self.pixel_array[y, x]
        return tuple(int(value) for value in pixel)  # Convert np.uint8 to regular int

    def set_pixel(self, x, y, color):
        """Set the pixel at (x, y) to the given (B, G, R) color tuple."""
        self.pixel_array[y, x] = np.array(color, dtype=np.uint8)

    def display_info(self):
        height, width, channels = self.pixel_array.shape
        print(f"BMP Image Info: {width}x{height}, 24-bit color")


class BMPImageWriter:
    @staticmethod
    def arr_to_file(np_array, file_path):
        BMPImageWriter.to_file(BMPImageReader(np_array), file_path)

    def to_file(bmp_image, file_path):
        """Writes the BMPImageReader object back to a BMP file"""
        height, width, channels = bmp_image.pixel_array.shape  # Dynamically get the shape

        with open(file_path, 'wb') as f:
            # Calculate padding
            row_padded = (width * 3 + 3) & ~3
            padded_row_size = row_padded * height
            file_size = TOTAL_HEADER_SIZE + padded_row_size

            file_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, TOTAL_HEADER_SIZE)
            f.write(file_header)

            dib_header = struct.pack('<IIIHHIIIIII',
                                     DIB_HEADER_SIZE,
                                     width,
                                     height,
                                     NO_OF_COLOR_PLANES,
                                     BPP_VALUE,
                                     COMPRESSION_VALUE,
                                     padded_row_size,
                                     HORIZONTAL_RESOLUTION,
                                     VERTICAL_RESOLUTION,
                                     COLORS_IN_PALETTE,
                                     NO_OF_IMPORTANT_COLORS)
            f.write(dib_header)

            # Write pixel data (no need to reverse rows)
            for row in bmp_image.pixel_array:  # Write rows from top to bottom (as stored in the array)
                f.write(row.tobytes())  # Write row as bytes
                f.write(b'\x00' * (row_padded - width * 3))  # Add padding to the row

        # print(f"BMP image saved as {file_path}")

