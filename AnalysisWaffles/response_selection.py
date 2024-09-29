# IMPORT ALL THE LIBRARIES USED IN THE NOTEBOOK
import math
import plotly.subplots as psu
import matplotlib.pyplot as plt

from waffles.data_classes.WaveformSet import WaveformSet
from waffles.data_classes.Waveform import Waveform
from waffles.input.pickle_file_to_WaveformSet import pickle_file_to_WaveformSet
import numpy as np
import ctypes
import yaml
import pickle
import os
import pandas as pd
from memory_profiler import profile

tv1filter = ctypes.cdll.LoadLibrary("/eos/home-h/hvieirad/waffles/waffles/src/waffles/data_classes/tv1ddenoise.o")
tv1filter.TV1D_denoise.argtypes = [ np.ctypeslib.ndpointer(dtype=np.float32), np.ctypeslib.ndpointer(dtype=np.float32), ctypes.c_int , ctypes.c_double ]

numpyoperations = {
    "max": np.max,
    "min": np.min,
}

with open('cuts_response.yaml', 'r') as f:
    cutsdata = yaml.safe_load(f)

runnumbers = np.unique(pd.read_csv('runlists/cosmic_runs.csv')['Run'].to_numpy())

binsbase = np.linspace(0,2**14-1,2**14)
times = np.linspace(0, 1024, 1024, endpoint=False)
threshold = 6
wait = 25
baselinefinish = 112
npts = 0


def filter_waveform(wvf: Waveform.adcs, filter:int = 2):
    response = np.zeros_like(wvf, dtype=np.float32)
    tv1filter.TV1D_denoise(wvf.astype(np.float32), response, npts, filter)
    return response
def compute_base_mean(wvf: Waveform.adcs, res0:int) -> tuple[float, bool]:
    minimumfrac = 1/6.
    i = 0
    res = 0
    counts = 0
    for _ in wvf:
        if (i>=baselinefinish):
            break
        val = wvf[i]
        if ((val > res0+threshold) | (val < res0 - threshold)):
            i+=wait
        else:
            res+=val
            counts+=1
            i+=1
    if (counts>0):
        res /= counts
    if(counts > baselinefinish*minimumfrac):
        return res, True
    else:
        return res0, False

def compute_baseline(wvf_base: Waveform.adcs) -> tuple[float, bool]:
    # # find the MPV so we can estimate the offset
    hist, bin_edges = np.histogram(wvf_base, bins=binsbase)
    # first estimative of baseline
    res0 = bin_edges[np.argmax(hist)]
    return compute_base_mean(wvf_base, res0)


def wfset_baseline(waveform: Waveform) -> tuple[float, bool]:
    wvf: Waveform.adcs = waveform.adcs
    response = filter_waveform(wvf,2)
    wvf_base = response[:baselinefinish]
    res0, optimal = compute_baseline(wvf_base)
    waveform.filtered = response

    return res0, optimal

def applycuts(waveform: Waveform, ch:int) -> bool:
    try:
        cuts = cutsdata[ch]['cuts']
    except Exception as error:
        # print('Yo... you forgot to add cuts for this channel')
        # print(error)
        return True
    for cut in cuts:
        t0 = cut['t0']
        tf = cut['tf']
        thre = cut['threshold']
        cuttype = cut['type']
        filter = cut['filter']
        stop = cut['stop']
        wvfcut = filter_waveform((waveform.adcs-waveform.baseline), filter)*(-1)
        refval = numpyoperations[cut['npop']](wvfcut[t0:tf])
        if cuttype == 'higher':
            if refval < thre:
                return False
        elif cuttype =='lower':
            if refval > thre:
                return False
        if stop:
            break
    return True




def allow_certain_endpoints_channels(waveform: Waveform, allowed_endpoints:list, allowed_channels:list) -> bool:
    global valids
    if valids > 5000:
        return False
    if waveform.endpoint in allowed_endpoints:
        if waveform.channel in allowed_channels:
            base, optimal = wfset_baseline(waveform)
            waveform.baseline = base
            waveform.optimal = optimal
            if not optimal: return False
            outcuts = applycuts(waveform, waveform.channel)
            if outcuts:
                valids+=1
                return True
    return False
import argparse

channels = [11225]
@profile
def do_all():
    print('ok')
    global channels
    global npts
    safemode = True

    global runnumbers
    for runnumber in runnumbers:
        file = f"/eos/home-h/hvieirad/waffles/analysis/rawdata/waffles_tau_slow_protoDUNE_HD/wfset_run0{runnumber}.pkl"
        # if runnumber <= 26152:
        #     continue


        wfset = pickle_file_to_WaveformSet(file)

        npts = wfset.points_per_wf

        wfset_ch:WaveformSet = 0
        try: 
            global valids
            valids = 0
            wfset_ch = WaveformSet.from_filtered_WaveformSet( wfset, allow_certain_endpoints_channels, [112] , channels, show_progress=False)
        except:
            print(f"No waveform for run {runnumber}")
            continue

        mchannels = {}
        for w in wfset_ch.waveforms:
            w:Waveform
            if w.channel in mchannels.keys():
                mchannels[w.channel] += 1
            else:
                mchannels[w.channel] = 0

        print(runnumber)
        for ch in channels:
            print(f'\t {ch}: {mchannels[ch]}')

            wvf_arrays = np.array([(waveform.adcs.astype(np.float32) - waveform.baseline)*-1 for waveform in wfset_ch.waveforms if waveform.channel == ch])


            avgwvf = np.mean(wvf_arrays, axis=0)
            res0, status = compute_baseline(avgwvf[:baselinefinish])
            avgwvf-=res0
            wfset_ch.avgwvf = avgwvf
            pickleavgname = f'responses/response_run0{runnumber}_ch{ch}.pkl'
            if safemode and os.path.isfile(pickleavgname):
                val:str
                val = input('File already there... overwrite? (y/n)\n')
                val = val.lower()
                if val == "y" or val == "yes":
                    pass
                else:
                    continue

            with open(pickleavgname, "wb") as f:
                pickle.dump(wfset_ch, f)
            print('Saved... ')
if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('-runs','--runs', type=int, nargs="+", help="Keep empty for all, or put the runs you want to be processed")
    args = vars(parse.parse_args())

    if args['runs'] is not None:
        runnumbers = [ r for r in runnumbers if r in args['runs'] ]
    do_all()
