import os
import subprocess as subp
import tkinter as tk
import wave
import math
import struct

import colorama
import pyperclip

from PIL import Image
from tkinter import filedialog

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED
LIGHTRED = colorama.Fore.LIGHTRED_EX

ZERO_WIDTH_SPACE = '\u200b'
ZERO_WIDTH_NON_JOINER = '\u200c'
ZERO_WIDTH_JOINER = '\u200d'
LEFT_TO_RIGHT_MARK = '\u200e'
RIGHT_TO_LEFT_MARK = '\u200f'
MIDDLE_DOT = '\u00b7'

padding = 11

zero_space_symbols = [
    ZERO_WIDTH_SPACE,
    ZERO_WIDTH_NON_JOINER,
    ZERO_WIDTH_JOINER,
    ]

_sound = None
num_lsb = 0
params = None
num_channels = None
sample_width = None
n_frames = None
n_samples = 0
fmt = None
smallest_byte = None
mask = None


def tartarus_ascii():
    """Print the app's title screen."""
    print(os.system('cls||clear'))
    print(f"\n{RED}  _____  _    ____ _____  _    ____  _   _ ____ {RESET}")
    print(f"{RED} |_   _|/ \  |  _ \_   _|/ \  |  _ \| | | / ___| {RESET}")
    print(f"{RED}   | | / _ \ | |_) || | / _ \ | |_) | | | \___ \ {RESET}")
    print(f"{RED}   | |/ ___ \|  _ < | |/ ___ \|  _ <| |_| |___) |{RESET}")
    print(f"{RED}   |_/_/   \_\_| \_\|_/_/   \_\_| \_\\\___/|____/ {RESET}")
    print(f"                   Made by Theos")


def help():
    """Print the help menu."""
    print(f"{YELLOW}zwc{RESET} - Hidden messages using Zero Width Characters.")
    print(f"{YELLOW}siEncode{RESET} - Steganography; Hide message in image.")
    print(f"{YELLOW}siCheck{RESET} - Steganography Check; Look for hidden message in image.")
    print(f"{YELLOW}pip_merge{RESET} - Merge two images into one (For best result use PNG " +
        "with opaque background).")
    print(f"{YELLOW}pip_unmerge{RESET} - Unmerge images.")
    print(f"{YELLOW}swEncode{RESET} - Encode text inside of wav file.")
    print(f"{YELLOW}swRecover{RESET} - Recover text from the wav file.")

tartarus_ascii()


# ZERO WIDTH CHARACTERS #

def to_base(num, b, numerals='0123456789abcdefghijklmnopqrstuvwxyz'):
    """Docstring TODO"""
    return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) +
        numerals[num % b])


def encode_text():
    """Requests input string, encodes, then copies encoded text to clipboard."""
    message = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter message to encode: ")
    encoded = LEFT_TO_RIGHT_MARK
    for message_char in message:
        code = '{0}{1}'.format('0' * padding, int(str(to_base(
            ord(message_char), len(zero_space_symbols)))))
        code = code[len(code) - padding:]
        for code_char in code:
            index = int(code_char)
            encoded = encoded + zero_space_symbols[index]

    encoded += RIGHT_TO_LEFT_MARK

    pyperclip.copy(encoded)
    print(f"{GREEN}[+]{RESET} Encoded message copied to clipboard. {GREEN}[+]{RESET}")


def decode_text():
    """Requests encoded text, then displays decoded text."""
    message = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter message to decode: ")
    extract_encoded_message = message.split(LEFT_TO_RIGHT_MARK)[1]
    message = extract_encoded_message
    extract_encoded_message = message.split(RIGHT_TO_LEFT_MARK)[0]
    encoded = ''
    decoded = ''

    for message_char in message:
        if message_char in zero_space_symbols:
            encoded = encoded + str(zero_space_symbols.index(message_char))

    cur_encoded_char = ''

    for index, encoded_char in enumerate(encoded):
        cur_encoded_char = cur_encoded_char + encoded_char
        if index > 0 and (index + 1) % padding == 0:
            decoded = decoded + chr(int(cur_encoded_char, len(zero_space_symbols)))
            cur_encoded_char = ''

    return decoded


def hidden_message():
    """Launches text encoding or decoding."""
    print("")
    option = int(input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} "
        "Choose ZWC option (1 - Encode / 2 - Decode): ").lower())
    if option == 1:
        encode_text()
    elif option == 2:
        print(f"{GREEN}[+]{RESET} Decoded Message:  " + decode_text())


# STEGANOGRAPHY - WAV #

def prepare():
    global _sound, num_lsb, params, num_channels, sample_width, n_frames, n_samples, fmt, smallest_byte, mask

    root = tk.Tk()
    root.withdraw()
    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter carrier wav name (with extension): ", 
        end="", flush=True)
    print('', end="")
    sound = filedialog.askopenfilename()
    print(sound)

    num_lsb = int(input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter number of LSBs to use: "))

    _sound = wave.open(sound, "r")

    params = _sound.getparams()
    num_channels = _sound.getnchannels()
    sample_width = _sound.getsampwidth()
    n_frames = _sound.getnframes()
    n_samples = n_frames * num_channels

    if (sample_width == 1): 
        fmt = "{}B".format(n_samples)
        mask = (1 << 8) - (1 << num_lsb)
        smallest_byte = -(1 << 8)
    elif (sample_width == 2): 
        fmt = "{}h".format(n_samples)
        mask = (1 << 15) - (1 << num_lsb)
        smallest_byte = -(1 << 15)
    else:
        raise ValueError("File has an unsupported bit-depth")


def hide_data():
    """Encode text inside of WAV file"""
    prepare()

    max_bytes_to_hide = (n_samples * num_lsb) // 8

    root = tk.Tk()
    root.withdraw()
    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter name of text file containing data to enocode (with extension): ", 
        end="", flush=True)
    print('', end="")
    data = filedialog.askopenfilename()
    print(data)

    filesize = os.stat(data).st_size

    if (filesize > max_bytes_to_hide):
        required_LSBs = math.ceil(filesize * 8 / n_samples)
        raise ValueError("Input file too large to hide, "
                         "requires {} LSBs, using {}"
                         .format(required_LSBs, num_lsb))
    
    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET}" + " Using {} B out of {} B".format(filesize, max_bytes_to_hide))

    raw_data = list(struct.unpack(fmt, _sound.readframes(n_frames)))
    _sound.close()

    input_data = memoryview(open(data, "rb").read())

    data_index = 0
    sound_index = 0

    values = []
    buffer = 0
    buffer_length = 0
    done = False

    while(not done):
        while (buffer_length < num_lsb and data_index // 8 < len(input_data)):
            buffer += (input_data[data_index // 8] >> (data_index % 8)
                        ) << buffer_length
            bits_added = 8 - (data_index % 8)
            buffer_length += bits_added
            data_index += bits_added
            
        current_data = buffer % (1 << num_lsb)
        buffer >>= num_lsb
        buffer_length -= num_lsb

        while (sound_index < len(raw_data) and
               raw_data[sound_index] == smallest_byte):

            values.append(struct.pack(fmt[-1], raw_data[sound_index]))
            sound_index += 1

        if (sound_index < len(raw_data)):
            current_sample = raw_data[sound_index]
            sound_index += 1

            sign = 1
            if (current_sample < 0):
                current_sample = -current_sample
                sign = -1

            altered_sample = sign * ((current_sample & mask) | current_data)

            values.append(struct.pack(fmt[-1], altered_sample))

        if (data_index // 8 >= len(input_data) and buffer_length <= 0):
            done = True
        
    while(sound_index < len(raw_data)):
        # At this point, there's no more data to hide. So we append the rest of
        # the samples from the original sound file.
        values.append(struct.pack(fmt[-1], raw_data[sound_index]))
        sound_index += 1
    
    output_path = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter name of the output wav (with extension): ")
    sound_steg = wave.open(output_path, "w")
    sound_steg.setparams(params)
    sound_steg.writeframes(b"".join(values))
    sound_steg.close()
    print(f"{GREEN}[+]{RESET} Data hidden over " + "{} audio file.".format(output_path))


def recover_data():
    """Recover text encoded inside of WAV file"""
    prepare()

    raw_data = list(struct.unpack(fmt, _sound.readframes(n_frames)))
    mask = (1 << num_lsb) - 1
    output_path = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter name of the output text file (with extension): ")
    output_file = open(output_path, "wb+")

    bytes_to_recover = int(input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter number of bytes to recover: "))

    data = bytearray()
    sound_index = 0 
    buffer = 0
    buffer_length = 0
    _sound.close()

    while (bytes_to_recover > 0):
        
        next_sample = raw_data[sound_index]
        if (next_sample != smallest_byte):
            buffer += (abs(next_sample) & mask) << buffer_length
            buffer_length += num_lsb
        sound_index += 1
        
        while (buffer_length >= 8 and bytes_to_recover > 0):
            current_data = buffer % (1 << 8)
            buffer >>= 8
            buffer_length -= 8
            data += struct.pack('1B', current_data)
            bytes_to_recover -= 1

    output_file.write(bytes(data))
    output_file.close()
    print(f"{GREEN}[+]{RESET} Data recovered to" + " {} text file".format(output_path))

# PICTURE IN PICTURE #

def int_to_bin(rgb):
    """Docstring TODO"""
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return ('{0:08b}'.format(r),
            '{0:08b}'.format(g),
            '{0:08b}'.format(b))


def bin_to_int(rgb):
    """Docstring TODO"""
    r, g, b = rgb
    return (int(r, 2),
            int(g, 2),
            int(b, 2))


def merge_rgb(rgb1, rgb2):
    """Docstring TODO"""
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    rgb = (r1[:4] + r2[:4],
            g1[:4] + g2[:4],
            b1[:4] + b2[:4])
    return rgb


def merge(img1, img2):
    """Merges two images into one.
    
    Args:
        img1: The first, larger image.
        img2: The second, smaller image.

    Returns:
        PIL Resulting merged PIL Image object.
    """
    
    if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
        print(f"{RED}[!]{RESET} Second image can not be bigger than the first one. {RED}[!]{RESET}")

    pixel_map1 = img1.load()
    pixel_map2 = img2.load()

    new_image = Image.new(img1.mode, img1.size)
    pixels_new = new_image.load()

    for i in range(img1.size[0]):
        for j in range(img1.size[1]):
            rgb1 = int_to_bin(pixel_map1[i, j])

            rgb2 = int_to_bin((0, 0, 0))

            if i < img2.size[0] and j < img2.size[1]:
                rgb2 = int_to_bin(pixel_map2[i, j])

            rgb = merge_rgb(rgb1, rgb2)

            pixels_new[i, j] = bin_to_int(rgb)

    return new_image


def unmerge(img):
    """Unmerges one images into two.
    
    Args:
        img: A previously merged PIL Image object.

    Returns:
        Extracted merged PIL Image object.
    """
    pixel_map = img.load()

    new_image = Image.new(img.mode, img.size)
    pixels_new = new_image.load()

    original_size = img.size

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = int_to_bin(pixel_map[i, j])

            rgb = (r[4:] + '0000',
                    g[4:] + '0000',
                    b[4:] + '0000')

            pixels_new[i, j] = bin_to_int(rgb)

            if pixels_new[i, j] != (0, 0, 0):
                original_size = (i + 1, j + 1)

    new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

    return new_image


def pip_merge():
    """Launches image merging."""
    root = tk.Tk()
    root.withdraw()

    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter first image name (with extension): ", 
        end="", flush=True)
    print('', end="")
    img1 = filedialog.askopenfilename()
    print(img1)

    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter second image name (with extension): ", 
        end="", flush=True)
    img2 = filedialog.askopenfilename()
    print(img2)
    root.destroy()

    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Save merged image as (with extension): ",
        end="", flush=True)
    filepath = filedialog.asksaveasfilename(filetypes=[('Image Files', '*.png')],
        defaultextension=[('Image Files', '*.png')])
    print(filepath)
    
    merged_image = merge(Image.open(img1), Image.open(img2))
    merged_image.save(filepath)
    subp.call(filepath, shell=True)
    root.destroy()


def pip_unmerge():
    """Launches image unmerging."""
    root = tk.Tk()
    root.withdraw()
    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter image to unmerge (with extension): ",
        end="", flush=True)
    img = filedialog.askopenfilename()
    print(img)

    print(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter new name for the unmerged image (with extension): ",
        end="", flush=True)
    output = filedialog.asksaveasfilename(filetypes=[('Image Files', '*.png')],
        defaultextension=[('Image Files', '*.png')])
    print(output)

    unmerged_image = unmerge(Image.open(img))
    unmerged_image.save(output)
    subp.call(output, shell=True)
    root.destroy()


# STEGANOGRAPHY - IMAGE #

def generate_data(data):
    """Docstring TODO"""
    new_data = []

    for i in data:
        new_data.append(format(ord(i), '08b'))
    return new_data


def modify_pixel(pix, data):
    """Docstring TODO"""
    datalist = generate_data(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]

        for j in range(0, 8):
            if datalist[i][j] == '0' and pix[j]% 2 != 0:
                pix[j] -= 1

            elif datalist[i][j] == '1' and pix[j] % 2 == 0:
                if pix[j] != 0:
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if i == lendata - 1:
            if pix[-1] % 2 == 0:
                if pix[-1] != 0:
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encode_enc(newimg, data):
    """Docstring TODO"""
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modify_pixel(newimg.getdata(), data):

        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1


def image_encode():
    """Encode text inside of image's metadata"""
    img = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter image name (with extension): ")
    try:
        image = Image.open(img, 'r')
    except:
        print(f"{RED}[!]{RESET} Can't find image. {RED}[!]{RESET}")
        return

    data = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter data to be encoded : ")
    if len(data) == 0:
        raise ValueError('Data is empty')

    newimg = image.copy()
    encode_enc(newimg, data)

    new_img_name = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} "
        "Enter the name of new image (with extension): ")
    newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))

    print(f"{GREEN}[+]{RESET} "
        f"Successfully created new image with hidden message. {GREEN}[+]{RESET}")


def image_decode():
    """Decode text from image's metadata"""
    img = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter image name (with extension): ")
    try:
        image = Image.open(img, 'r')
    except:
        print(f"{RED}[!]{RESET} Can't find image. {RED}[!]{RESET}")
        return

    data = ''
    imgdata = iter(image.getdata())

    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binary_string = ''

        for i in pixels[:8]:
            if i % 2 == 0:
                binary_string += '0'
            else:
                binary_string += '1'

        data += chr(int(binary_string, 2))
        if pixels[-1] % 2 != 0:
            if data != "":
                print(f"{GREEN}[+]{RESET} Decoded Message : {data} {GREEN}[+]{RESET}")
                return
            else:
                print(f"{GREEN}[+]{RESET} Image does not contain any encoded message. "
                    f"{data} {GREEN}[+]{RESET}")
                return


while True:
    command = input(f"\n{RED}Tartarus: {RESET}")
    cmd_splitted = command.split(' ', 1)

    if cmd_splitted[0] == "zwc":
        hidden_message()
    if cmd_splitted[0] == "siEncode":
        image_encode()
    if cmd_splitted[0] == "siCheck":
        image_decode()
    if cmd_splitted[0] == "pip_merge":
        pip_merge()
    if cmd_splitted[0] == "pip_unmerge":
        pip_unmerge()
    if cmd_splitted[0] == "swEncode":
        hide_data()
    if cmd_splitted[0] == "swRecover":
        recover_data()
    if cmd_splitted[0] == "help":
        help()
