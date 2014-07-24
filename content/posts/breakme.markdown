title: Crack me 
date: 2014-07-17
authors: momorientes
tags: crackme, pwnium2014

 * **Solved by**: exco, ttb, makefu
 * **Author**: momorientes

`QlpoOTFBWSZTWTxSmOAAAAsJAF/gOwAgADEAAAiZMNT0JbKzhCQcyQtA2gNbvXgSvxdyRThQkDxSmOA=` was the only information avaliable.  
The trailing `=` is always a good hint for base64, so we'll try that:

    :::bash
    echo -n QlpoOTFBWSZTWTxSmOAAAAsJAF/gOwAgADEAAAiZMNT0JbKzhCQcyQtA2gNbvXgSvxdyRThQkDxSmOA= | base64 -d                                
    BZh91AY&SY<Rà
                    _à; 0Ôô%²³$É
                                @Ú[½x¿rE8P<R

While this might look like complete crap the `BZ` in the header is the magic number of bzip. The `h` tells us that is Huffman coding we're dealing with and therefore `bzip2`. The `9` shows us the uncompressed block-size in 100kB (here:900kB).

Easy enough all we have to do is pipe our base64 decoded string into bunzip2:

    :::bash
    echo QlpoOTFBWSZTWTxSmOAAAAsJAF/gOwAgADEAAAiZMNT0JbKzhCQcyQtA2gNbvXgSvxdyRThQkDxSmOA= | base64 -d | bunzip2 -d
    9afa828748387b6ac0a393c00e542079

That's it, no Pwnium{} flag format needed (that did cost us quite some time)!
