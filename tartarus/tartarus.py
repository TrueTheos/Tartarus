import os
import colorama
import pyperclip
import re
import cv2
import pathlib
import imageio
from PIL import Image

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

zeroSpaceSymbols = [
    ZERO_WIDTH_SPACE,
    ZERO_WIDTH_NON_JOINER,
    ZERO_WIDTH_JOINER,
]

def tartarusAscii():
    print(os.system('cls||clear'))
    print(f"\n{RED}  _____  _    ____ _____  _    ____  _   _ ____ {RESET}")
    print(f"{RED} |_   _|/ \  |  _ \_   _|/ \  |  _ \| | | / ___| {RESET}")
    print(f"{RED}   | | / _ \ | |_) || | / _ \ | |_) | | | \___ \ {RESET}")
    print(f"{RED}   | |/ ___ \|  _ < | |/ ___ \|  _ <| |_| |___) |{RESET}")
    print(f"{RED}   |_/_/   \_\_| \_\|_/_/   \_\_| \_\\\___/|____/ {RESET}")
    print(f"                   Made by Theos")

def help():
    print(f"{YELLOW}zwc{RESET} - Hidden messages using Zero Width Characters.")
    print(f"{YELLOW}siEncode{RESET} - Steganography; Hide message in image.")
    print(f"{YELLOW}siCheck{RESET} - Steganography Check; Look for hidden message in image.")
    print(f"{YELLOW}pipMerge{RESET} - Merge two images into one (For best resoult use PNG with opaque background).")
    print(f"{YELLOW}pipUnmerge{RESET} - Unmerge images.")
    print(f"{YELLOW}zwc{RESET} - Hidden messages using zero-width characters.")

tartarusAscii()

# ZERO WIDTH CHARACTERS #

def to_base(num, b, numerals='0123456789abcdefghijklmnopqrstuvwxyz'):
    return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

def encodeText():
    message = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter message to encode: ")
    encoded = LEFT_TO_RIGHT_MARK
    for message_char in message:
        code = '{0}{1}'.format('0' * padding, int(str(to_base(ord(message_char), len(zeroSpaceSymbols)))))
        code = code[len(code) - padding:]
        for code_char in code:
            index = int(code_char)
            encoded = encoded + zeroSpaceSymbols[index]
    
    encoded += RIGHT_TO_LEFT_MARK

    pyperclip.copy(encoded)
    print(f"{GREEN}[+]{RESET} Encoded message coppied to clipboard. {GREEN}[+]{RESET}")

def decodeText():
    message = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter message to decode: ")
    extractEncodedMessage = message.split(LEFT_TO_RIGHT_MARK)[1]
    message = extractEncodedMessage
    extractEncodedMessage = message.split(RIGHT_TO_LEFT_MARK)[0]
    encoded = ''
    decoded = ''

    for message_char in message:
        if message_char in zeroSpaceSymbols:
            encoded = encoded + str(zeroSpaceSymbols.index(message_char))

    cur_encoded_char = ''

    for index, encoded_char in enumerate(encoded):
        cur_encoded_char = cur_encoded_char + encoded_char
        if index > 0 and (index + 1) % padding == 0:
            decoded = decoded + chr(int(cur_encoded_char, len(zeroSpaceSymbols)))
            cur_encoded_char = ''

    return decoded

def hiddenMessage():
    print("")
    option = int(input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Choose ZWC option (1 - Encode / 2 - Decode): ").lower())
    if(option == 1):
        encodeText()
    elif(option == 2):
        print(f"{GREEN}[+]{RESET} Decoded Message :  " + decodeText())

# PICTURE IN PICTURE #

def intToBin(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return ('{0:08b}'.format(r),
            '{0:08b}'.format(g),
            '{0:08b}'.format(b))

def binToInt(rgb):
    r, g, b = rgb
    return (int(r, 2),
            int(g, 2),
            int(b, 2))

def mergeRgb(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    rgb = (r1[:4] + r2[:4],
            g1[:4] + g2[:4],
            b1[:4] + b2[:4])
    return rgb

def merge(img1, img2):
    if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
        print(f"{RED}[!]{RESET} Second image can not be bigger than the first one. {RED}[!]{RESET}")

    pixel_map1 = img1.load()
    pixel_map2 = img2.load()

    new_image = Image.new(img1.mode, img1.size)
    pixels_new = new_image.load()

    for i in range(img1.size[0]):
        for j in range(img1.size[1]):
            rgb1 = intToBin(pixel_map1[i, j])

            rgb2 = intToBin((0, 0, 0))

            if i < img2.size[0] and j < img2.size[1]:
                rgb2 = intToBin(pixel_map2[i, j])

            rgb = mergeRgb(rgb1, rgb2)

            pixels_new[i, j] = binToInt(rgb)

    return new_image

def unmerge(img):
    pixel_map = img.load()

    new_image = Image.new(img.mode, img.size)
    pixels_new = new_image.load()

    original_size = img.size

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = intToBin(pixel_map[i, j])

            rgb = (r[4:] + '0000',
                    g[4:] + '0000',
                    b[4:] + '0000')

            pixels_new[i, j] = binToInt(rgb)

            if pixels_new[i, j] != (0, 0, 0):
                original_size = (i + 1, j + 1)

    new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

    return new_image

def pipMerge():
    img1 = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter first image name (with extension): ")
    img2 = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter second image name (with extension): ")
    output = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter name for the merged image (with extension): ")
    mergedImage = merge(Image.open(img1), Image.open(img2))
    mergedImage.save(output)

def pipUnmerge():
    img = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter image to unmerge (with extension): ")
    output = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter new name for the unmerged image (with extension): ")
    unmergedImage = unmerge(Image.open(img))
    unmergedImage.save(output)

# STEGANOGRAPHY - IMAGE #

def generateData(data):
        newData = []
 
        for i in data:
            newData.append(format(ord(i), '08b'))
        return newData

def modifyPixel(pix, data):
 
    datalist = generateData(data)
    lendata = len(datalist)
    imdata = iter(pix)
 
    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]
 
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j]% 2 != 0):
                pix[j] -= 1
 
            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if(pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
 
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1
 
        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]
    
def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)
 
    for pixel in modifyPixel(newimg.getdata(), data):
 
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

def imageEncode():
    img = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter image name (with extension): ")
    try:
        image = Image.open(img, 'r')
    except:
        print(f"{RED}[!]{RESET} Can't find image. {RED}[!]{RESET}")
        return

    data = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter data to be encoded : ")
    if (len(data) == 0):
        raise ValueError('Data is empty')
 
    newimg = image.copy()
    encode_enc(newimg, data)

    new_img_name = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter the name of new image (with extension): ")
    newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))

    print(f"{GREEN}[+]{RESET} Successfully created new image with hidden message. {GREEN}[+]{RESET}")
 
def imageDecode():
    img = input(f"{YELLOW}[{MIDDLE_DOT}]{RESET} Enter image name (with extension): ")
    try:
        image = Image.open(img, 'r')
    except:
        print(f"{RED}[!]{RESET} Can't find image. {RED}[!]{RESET}")
        return
 
    data = ''
    imgdata = iter(image.getdata())
 
    while (True):
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binaryString = ''
 
        for i in pixels[:8]:
            if (i % 2 == 0):
                binaryString += '0'
            else:
                binaryString += '1'
 
        data += chr(int(binaryString, 2))
        if (pixels[-1] % 2 != 0):
            if(data != ""):
                print(f"{GREEN}[+]{RESET} Decoded Message : {data} {GREEN}[+]{RESET}")
                return 
            else:
                print(f"{GREEN}[+]{RESET} Image does not contain any encoded message. {data} {GREEN}[+]{RESET}")
                return 

while True:
    command = input(f"\n{RED}Tartarus: {RESET}")
    cmdSplitted = command.split(' ', 1)

    if(cmdSplitted[0] == "zwc"):
        hiddenMessage()
    if(cmdSplitted[0] == "siEncode"):
        imageEncode()
    if(cmdSplitted[0] == "siCheck"):
        imageDecode()
    if(cmdSplitted[0] == "pipMerge"):
        pipMerge()
    if(cmdSplitted[0] == "pipUnmerge"):
        pipUnmerge()
    if(cmdSplitted[0] == "help"):
        help()