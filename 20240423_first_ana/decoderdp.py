#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os
import glob

import argparse

maxevents = 1718

def read_and_write(filename, ch):
    fpy = open(filename,"rb")
    print(f"Writting {filename} of ch {ch} ... ")
    aux=0
    while (True):
        try:
            data = np.load(fpy, allow_pickle=True)
            with open(f'wave{ch}.dat','ab') as f:
                leng = (len(data)*2+24).to_bytes(4,'little')
                for _ in range(6):
                    f.write(leng)
                f.write(bytearray(data))
            aux+=1
            if aux==maxevents:
                break
        except:
            print(f"Broke at {aux}")
            break


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('-ch', '--ch', type=int, nargs='+',
                        help='Channels to decode (default is all)', default = -1) 
    parse.add_argument('-p', '--ch_pattern', type=str, help='Pattern of ch', default='_ch')
    args = vars(parse.parse_args())
    channels = args['ch']
    ch_pattern = args['ch_pattern']
    all_files = sorted(glob.glob("*.npy"))
    if isinstance(channels, list):
        new_list = []
        for f in all_files:
            for ch in sorted(channels):
                if f"{ch_pattern}{ch}" in f:
                    new_list.append(f)
        all_files = [ l for l in new_list ]

    # exit(0)
    fileisthere = False
    datfiles = glob.glob("wave*.dat")
    for dfile in datfiles:
        os.remove(dfile)

    for filename in all_files:
        # if not filename.startswith("np02"): continue
        ch = filename.split("ch")[1]
        ch = int(ch.split(".")[0])
        read_and_write(filename, ch)
