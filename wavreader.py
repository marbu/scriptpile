#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import struct
import sys
import wave


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="wav reader")
    ap.add_argument("wavfile")
    ap.add_argument("-v", action="store_true", help="show values")
    ap.add_argument("-s", action="store_true", help="value stats")
    args = ap.parse_args()

    with wave.open(args.wavfile, 'r') as wav:
        n_frames = wav.getnframes()
        # asking for all frames at once, TODO: optimize :)
        frames = wav.readframes(n_frames)
        # unpacking 8 bit frame as little endian char
        iter_values = struct.iter_unpack("<b", frames)

        # set of all frame values
        values = set()

        prev_val = next(iter_values)
        values.add(int(prev_val[0]))
        val_count = 1
        for val in iter_values:
            if val == prev_val:
                val_count += 1
            else:
                if args.v:
                    print("{: } {}".format(int(val[0]), val_count))
                values.add(int(val[0]))
                val_count = 1
            prev_val = val

        if args.s:
            print(values)
