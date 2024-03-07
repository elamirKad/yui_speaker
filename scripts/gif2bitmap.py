import numpy as np
from PIL import Image, ImageSequence, ImageOps
import os, re


def gif_to_png_frames(gif_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with Image.open(gif_path) as img:
        for frame_number, frame in enumerate(ImageSequence.Iterator(img)):
            frame = frame.convert('RGB')

            width, height = frame.size
            target_width, target_height = 128, 64
            ratio = min(target_width / width, target_height / height)
            new_size = (int(width * ratio), int(height * ratio))

            frame = frame.resize(new_size, Image.Resampling.LANCZOS)

            new_img = Image.new("RGB", (target_width, target_height), "white")
            top_left = ((target_width - new_size[0]) // 2, (target_height - new_size[1]) // 2)
            new_img.paste(frame, top_left)

            new_img = ImageOps.invert(new_img)

            frame_path = os.path.join(output_dir, f'frame_{frame_number}.png')
            new_img.save(frame_path)
            print(f'Saved {frame_path}')


def png_to_byte_arrays(png_directory):
    byte_arrays = []
    for png_file in sorted(os.listdir(png_directory)):
        if png_file.endswith('.png'):
            png_path = os.path.join(png_directory, png_file)
            img = Image.open(png_path).convert('1')
            img_array = np.array(img, dtype=np.bool_)
            height, width = img_array.shape
            bytes_per_row = ((width + 7) // 8)
            binary_list = []

            for y in range(height):
                for x_byte in range(bytes_per_row):
                    byte = 0
                    for bit in range(8):
                        x_pixel = x_byte * 8 + bit
                        if x_pixel < width:
                            if img_array[y, x_pixel]:
                                byte |= (1 << (7-bit))
                    binary_list.append(byte)

            byte_arrays.append((png_file.replace('.png', ''), binary_list, width, height))
    return byte_arrays


def byte_arrays_to_c_array(byte_arrays, output_file):
    frame_data = []

    c_array_str = "const unsigned char frames[numberOfFrames][1024] = {\n"
    frame_data.append(c_array_str)
    for name, binary_list, width, height in byte_arrays:
        c_array_str = "{"
        c_array_str += ",".join(f"0x{byte:02x}" for byte in binary_list)
        c_array_str += "},\n"
        frame_data.append(c_array_str)

    combined_c_array = "".join(frame_data)
    combined_c_array = combined_c_array + "};"

    with open(output_file, 'w') as out_file:
        out_file.write(combined_c_array)
        print(f"C array has been written to {output_file}")


gif_path = 'audio.gif'
output_dir = 'frames'
xbm_directory = 'xbm'
output_file = 'frames.c'
gif_to_png_frames(gif_path, output_dir)
byte_arrays = png_to_byte_arrays(output_dir)
byte_arrays_to_c_array(byte_arrays, output_file)
