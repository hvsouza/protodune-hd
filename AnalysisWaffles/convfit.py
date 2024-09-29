# IMPORT ALL THE LIBRARIES USED IN THE NOTEBOOK
import math
import plotly.subplots as psu
import matplotlib.pyplot as plt
from waffles.data_classes.WaveformSet import WaveformSet
from waffles.data_classes.Waveform import Waveform
import numpy as np
from waffles.input.pickle_file_to_WaveformSet import pickle_file_to_WaveformSet

from iminuit import Minuit, cost
from iminuit.util import describe

import pandas as pd
import argparse



def model(t, A, fp, t1, t3):
    y = np.zeros(len(t),dtype=float)
    _t = t[t>0]
    y[t>0] = A*(fp*np.exp(-_t/t1)/t1 + (1-fp)*np.exp(-_t/t3)/t3)
    return np.convolve(y,template,mode='full')[:len(y)]


def process_waveforms(wfsetresponse:Waveform, wfsettemplate:Waveform, offset = 71)
    offset = 71

    template = wfsettemplate.avgwvf.copy()
    data = wfsetresponse.avgwvf.copy()
    data = np.roll(data, offset, axis=0)
    data = data[offset:]
    template = template[offset:]
    return data, template

def minimize(data:np.ndarray, template:ndarray):

    times = np.linspace(0,len(data)*16,len(data),endpoint=False)
    errors = np.ones(len(data))*0.1


    cost = cost.LeastSquares(times, data, errors, model)

    A = 1e3
    fp = 0.3
    t1 = 6
    t3 = 1600

    m = Minuit(cost,A=A,fp=fp,t1=t1,t3=t3)

    m.limits['A'] = (0,None)
    m.limits['fp'] = (0,1)
    m.limits['t1'] = (2,50)
    m.limits['t3'] = (500,2000)


    m.fixed['A'] =True
    m.migrad()
    m.migrad()
    m.migrad()
    m.fixed['A'] = False
    m.migrad()
    m.migrad()
    m.migrad()
    print(m)

    pars = describe(model)[1:]
    vals = [m.values[p] for p in pars]

    plt.errorbar(times,data,errors,fmt='o',alpha=0.3,color='gray')
    plt.plot(times,model(times,*vals),color='r',zorder=100)
    plt.figure()
    plt.errorbar(times,data,errors,fmt='o',alpha=0.3,color='gray')
    plt.plot(times,model(times,*vals),color='r',zorder=100)
    plt.xlim(0,2000)
    plt.show()

if __name__ == __main__:
    
    parse = argparse.ArgumentParser()
    parse.add_argument('-runs','--runs', type=int, nargs="+", help="Keep empty for all, or put the runs you want to be processed")
    parse.add_argument('-ch','--channel', type=int, help="Which channel to analyze", default=11225)
    parse.add_argument('-ft','--fix-template', action="store_true", help="Fix template to run 26261 (or thetemplate)")
    parse.add_argument('-tt', '--thetemplate', type=int, help="If fix-template is set, use this to tell which template to use", default=26261)
    args = vars(parse.parse_args())
    

    if args['runs'] not None:
        print('Please give a cosmic run')
        exit(0)
    runnumbers = [ r for r in runnumbers if r in args['runs'] ]
    ch = args['channel']
    use_fix_template = args['fix-template']
    
    df = pd.read_csv("/eos/home-h/hvieirad/waffles/analysis/runlists/cosmic_runs.csv")
    runs = df['Run'].to_numpy()
    ledruns = df['Run LED'].to_numpy()
    if use_fix_template:
        ledruns = np.ones_like(ledruns)*args['thetemplate']
    
    runpairs = { r:lr for r, lr in zip(runs, ledruns) }

    for run in runnumbers:
        print(run, runpairs[run])

        fileresponse = f'/eos/home-h/hvieirad/waffles/analysis/responses/response_run0{run}_ch{ch}.pkl'
        filetemplate = f'/eos/home-h/hvieirad/waffles/analysis/templates/template_run0{runpairs[run]}_ch{ch}.pkl'

        print(fileresponse)
        print(filetemplate)
        # wfsetresponse = pickle_file_to_WaveformSet(fileresponse)
        # wfsettemplate = pickle_file_to_WaveformSet(filetemplate)

    


