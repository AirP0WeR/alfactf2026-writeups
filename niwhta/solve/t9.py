#!/usr/bin/env python3
"""Encode ASCII strings into peace.v multi-tap keypad sequences."""
import sys


ENC = {
    "1": "1*1",
    "2": "2*1",
    "3": "3*1",
    "4": "4*1",
    "5": "5*1",
    "6": "6*1",
    "7": "7*1",
    "8": "8*1",
    "9": "9*1",
    "0": "0*1",
    "a": "2*2",
    "b": "2*3",
    "c": "2*4",
    "d": "3*2",
    "e": "3*3",
    "f": "3*4",
    "g": "4*2",
    "h": "4*3",
    "i": "4*4",
    "j": "5*2",
    "k": "5*3",
    "l": "5*4",
    "m": "6*2",
    "n": "6*3",
    "o": "6*4",
    "p": "7*2",
    "q": "7*3",
    "r": "7*4",
    "s": "7*5",
    "t": "8*2",
    "u": "8*3",
    "v": "8*4",
    "w": "9*2",
    "x": "9*3",
    "y": "9*4",
    "z": "9*5",
    " ": "0*1",
    ".": "a*1",
    ",": "a*2",
    "?": "a*3",
    "!": "a*4",
    "'": "b*1",
    '"': "b*2",
    ":": "b*3",
    ";": "b*4",
    "-": "c*1",
    "_": "c*2",
    "/": "c*3",
    "\\": "c*4",
    "@": "d*1",
    "&": "d*2",
    "{": "d*3",
    "}": "d*4",
    "+": "*",
}


def encode(text: str) -> str:
    out = []
    for ch in text:
        if ch in ENC:
            out.append(ENC[ch])
            continue
        lo = ch.lower()
        if lo in ENC and ch != lo:
            out.append("#")
            out.append(ENC[lo])
            continue
        raise KeyError(f"unsupported char: {ch!r}")
    return " ".join(out)


def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = sys.stdin.read()
    text = text.rstrip("\n")
    print(encode(text))


if __name__ == "__main__":
    main()
