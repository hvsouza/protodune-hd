import numpy as np
import matplotlib.pyplot as plt
import sys
from iminuit import Minuit, cost
from iminuit.util import describe
import mplhep
mplhep.style.use(mplhep.style.ROOT)

plt.rcParams.update({'font.size': 16,
                     'grid.linestyle': '--',
                     'axes.grid': True,
                     'figure.autolayout': True,
                     'figure.figsize': [14,6]
                     })

path1 = 'lar_response.npy'
path2 = 'spe_response.npy'

data = np.array(np.load(path1,allow_pickle=True))
response = np.array(np.load(path2,allow_pickle=True))

offset = 70

data = np.roll(data, offset, axis=0)
data = data[offset:]
response = response[offset:]


times = np.linspace(0,len(data)*16,len(data),endpoint=False)
errors = np.ones(len(data))*5

def model(t, A, fp, t1, t3):
    offset = 0
    t0 = t - offset
    y = np.zeros(len(t0),dtype=float)
    _t = t0[t0>0]
    y[t0>0] = A*(fp*np.exp(-_t/t1)/t1 + (1-fp)*np.exp(-_t/t3)/t3)
    return np.convolve(y,response,mode='full')[:len(y)]

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

plt.errorbar(times,data,errors, fmt='.', ms=5, color='k')
plt.plot(times,model(times,*vals),color='r',zorder=100)
plt.ylabel("ADC channels")
plt.xlabel("Time [ns]")
fit_info = [
    f"$\\chi^2$/$n_\\mathrm{{dof}}$ = {m.fval:.1f} / {m.ndof:.0f} = {m.fmin.reduced_chi2:.1f}",
]
for p, v, e in zip(m.parameters, m.values, m.errors):
    fit_info.append(f"{p} = ${v:.3f} \\pm {e:.3f}$")

plt.legend(title="\n".join(fit_info), frameon=False)
plt.show()
