<p align=center>
  <img src="./images/logo.png"/>
  <br>
  <span>Hide messages using Steganography</span>
  <br>
  <a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.6-green.svg"></a>
  <a target="_blank" href="LICENSE" title="License: GPL-3.0"><img src="https://img.shields.io/badge/License-GMT3.0-blue.svg"></a>
 </p>
 
## Steganography

Let’s understand what is steganography.

### What is steganography?

> [Steganography](https://en.wikipedia.org/wiki/Steganography) is the practice of concealing a file, message, image, or video within another file, message, image, or video.

### What is the advantage of steganography over cryptography?
> The advantage of steganography over [cryptography](https://en.wikipedia.org/wiki/Cryptography) alone is that the intended secret message does not attract attention to itself as an object of scrutiny. Plainly visible encrypted messages, no matter how unbreakable they are, arouse interest and may in themselves be incriminating in countries in which [encryption](https://en.wikipedia.org/wiki/Encryption) is illegal.

In other words, steganography is more discreet than cryptography when we want to send a secret information. On the other hand, the hidden message is easier to extract.

## Installation

```console
# clone the repo
$ git clone https://github.com/Loiuy123/Tartarus.git

# change the working directory to tartarus
# cd tartarus
```

## Usage

```console
$python tartarus.py
commands:
  help - List of all commands with descriptions
  zwc - Hidden messages using Zero Width Characters
  siEncode - Steganography; Hide message in image
  siCheck - Steganography Check; Look for hidden message in image
  pipMerge - Merge two images into one
  pipUnmerge - Unmerge images
```

## Zero Width Characters

Hide or extract hidden message made out of zero with characters:
```
Message before: 
Hey I contain top secret message!

After running zwc decode:
Hey I contain top secret message! It's me - secret message
```

## Contributing
We would love to have you help me with the development of Tartarus. Each and every contribution is greatly valued! Contact me via Discord - Theos#2613
