title: ROT
date: 2014-07-21
authors: makefu, momorientes
tags: crackme, pwnium2014, captcha

 * **Solved by**: momorientes,exco,ttb,makefu
 * **Author First Part**: momorientes
 * **Author Second Part**: makefu

## Introduction
We got a raw-socket ip and port and when connecting to it we got a big ASCII
blob. After cracking the code you have to send it back within 5 seconds.

The == at the end of the Text hinted towards base64 encoding. 
## Part 1: Decoding the Message

Momo needs to write shitz here about decoding, image stitching and so on

![Retrieved image](data/rot/foo.png)

## Part 2: Automated Text Recognition
As expected, manually cracking the captcha is close to impossible, humans are
pretty bad at cracking captchas quickly. Therefore we needed needed the power
of OCR to crack the code and send it back to the server.

As [PyTesser]( https://pytesser.googlecode.com/ ) seemed to be the most uncomplicated python library to extract text
from an image we tried to throw it directly against the image

    :::python
    from PIL import Image
    img = Image.open("difference.png")
    img = img.convert("RGB")
    from pytesser import *
    passwd = image_to_string(img).replace(" ","").strip()+"\n"

After a few tries it seemed like the text recognition was too bad against the
raw image so we decided to perform some pre-processing of the image:

 1. make the background (true blue and magenta) white 
 2. make the text (every other color) black

We use PIL and load the image into a directly-mapped twodimensional array
This is what we came up with:

    :::python
    pixdata = img.load()
    # Clean the background noise, if color != white, then set to black.
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y] == (0, 0, 255, 255) or pixdata[x, y] == (255, 0, 255, 255):
                pixdata[x, y] = (0, 0, 0, 255)
            else:
                pixdata[x,y] = (255,255,255,255)

After pre-processing, the hit rate was is at close to 100 percent, yay!

## Putting it together

When putting everything together, this is our code:

    #!/usr/bin/env python
    #-*- coding: utf-8 -*-
    
    import telnetlib
    import base64
    import os
    import time 
    tn = telnetlib.Telnet("41.231.53.40", 9090)
    foo = tn.read_until('\n', 2)
    foo = foo.strip()
    foo = base64.b64decode(foo)
    with open('foo.png', 'w') as f:
        f.write(foo)
      
    os.system('convert foo.png -crop 100x200+0+0 left.png')
    os.system('convert foo.png -crop 100x200+100+0 right.png')
    os.system('convert left.png -rotate -90 left_rot.png')
    os.system('convert right.png -rotate 90 right_rot.png')
    os.system('composite left_rot.png right_rot.png -compose difference difference.png')

    from PIL import Image
    import sys

    img = Image.open("difference.png")
    img = img.convert("RGBA")

    pixdata = img.load()
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y] == (0, 0, 255, 255) or pixdata[x, y] == (255, 0, 255, 255):
                pixdata[x, y] = (0, 0, 0, 255)
            else:
                pixdata[x,y] = (255,255,255,255)
    img = img.convert("RGB")
    from pytesser import *
    passwd = image_to_string(img).replace(" ","").strip()+"\n"

    print(passwd)
    tn.write(passwd)
    print(tn.read_all())

After running, the Flag was written to stdout, success!

    Pwnium{b1a371c90da6a1d2deba2f6ebcfe3fc0}
