title: for1 USB Dump
date: 2014-07-17
author: makefu
tags: crackme, pwnium2014, captcha

 * **Solved by**: momorientes, makefu
 * **Author**: makefu

## Finding the needle in the haystack
We received an dump file which was loadable via wireshark. The dump looks like
some usb-traffic between a computer and a USB-SATA Hard Disk.

Normally it is a good idea to sort traces by size as bigger packets normally
contain *interesing* data. URB\_BULK packages contain actual transfer data from
the disk.
After looking around we remembered that at the beginning of the ctf (the website was still offline) we got told that the flag format is Pwnium{md5}.

A quick `-> ctrl-f -> string -> pwnium -> Packet bytes -> Pwnium` revealed
what we were looking for. 
That was easy!

## Remarks
Besides that, there were quite a lot of nice finds in the dump:

 * *Packet 860*: Mac OS X - This resource fork intentionally blank left
 * *Packet 854*: Riot Games
 * *Packet 116*: EPORT~1PDF

[The original Dump File](data/usb_dump/for1.pcapng)
