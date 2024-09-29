import numpy as np
import matplotlib.pyplot as plt
import awkward as ak
import uproot
from tqdm import tqdm
from glob import glob
from scipy import stats as st
from scipy import signal
import numba as nb

import mplhep
mplhep.style.use(mplhep.style.ROOT)
plt.rcParams.update({'font.size': 23,
                     'grid.linestyle': '--',
                     'axes.grid': True,
                     'figure.autolayout': True,
                     'figure.figsize': [14,6]
                     })

# rootfile = f"run0{run}/sphe_waveforms_Ch{ch}.root"
reference = f"run0{run}/analyzed.root:t1"
selftrigger = []
for c in ch:
    selftrigger.append(f"run0{run}/sphe_waveforms_Ch{c}.root:t1")

tref = uproot.open(reference)
tspes = [ uproot.open(st) for st in selftrigger]

class DataClass:
    
    def __init__(self, ttree:uproot.TTree, ch:int):
        self.npts      = ttree[f'Ch{ch}./Ch{ch}.npts'].array(),
        self.peak      = ttree[f'Ch{ch}./Ch{ch}.peak'].array(),
        self.peakpos   = ttree[f'Ch{ch}./Ch{ch}.peakpos'].array(),
        self.charge    = ttree[f'Ch{ch}./Ch{ch}.charge'].array(),
        self.fprompt   = ttree[f'Ch{ch}./Ch{ch}.fprompt'].array(),
        self.event     = ttree[f'Ch{ch}./Ch{ch}.event'].array(),
        self.time      = ttree[f'Ch{ch}./Ch{ch}.time'].array(),
        self.wvf       = ttree[f'Ch{ch}./Ch{ch}.wvf'].array(),
        self.base      = ttree[f'Ch{ch}./Ch{ch}.base'].array(),
        self.selection = ttree[f'Ch{ch}./Ch{ch}.selection'].array(),

        self.npts      = self.npts[0]
        self.peak      = self.peak[0]
        self.peakpos   = self.peakpos[0]
        self.charge    = self.charge[0]
        self.fprompt   = self.fprompt[0]
        self.event     = self.event[0]
        self.time      = self.time[0]
        self.wvf       = self.wvf[0]
        self.base      = self.base[0]
