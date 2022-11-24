# %load ./header.py
import numpy as np
from scipy import signal
from scipy import linalg
import control
import matplotlib.pyplot as plt

import sys

if '../sdfpy' not in sys.path:
  sys.path.insert(0,'../sdfpy')

import sd_sim
import sdfpy as sdf

OSR = 256      # oversample ratio
fb = 22050     # nyquist
fs = OSR*2*fb  # sampling frequency
ts = 1/fs      # sampling period


Rs = 60
Wn = 2*np.pi*np.array([300, 3000])
ftype = 'bandpass'
N = 4

[z,p,k] = signal.cheby2(N/2,Rs,Wn,ftype, analog=True, output='zpk')
the_filter = signal.zpk2ss(z,p,k)

# %store the_filter

[A,B,C,D] = the_filter
sys = control.ss(A, B, C, D)
# out = control.bode_plot(sys, Hz=True)

# ===========================================================================

# ===========================================================================
[A, T] = linalg.matrix_balance(A)
B = linalg.solve(T, B) 
C = C @ T

# ===========================================================================
OSR = 256      # oversample ratio
fb  = 22050    # nyquist
fs  = OSR*2*fb # sampling frequency
ts  = 1/fs     # sampling period

# # ----------------------------------------------------------
# # Converting from Continuous Time to Sampled Time
# [Ad,Bd,Cd,Dd] = sdf.c2delta(A,B,C,D,ts)
# ===========================================================================
Ad = (linalg.expm(A*ts) - np.eye(A.shape[0])) / ts
Bd = ((linalg.expm(A*ts) - np.eye(A.shape[0]) ) @ B) / ts
Bd = np.linalg.inv(A) @ Bd
Cd = C
Dd = D

# # ----------------------------------------------------------
# # Structural Transformation of Filter
# [Ad_t,Bd_t,Cd_t,Dd_t,T0] = sdf.obsv_cst(Ad,Bd,Cd,Dd)
# ===========================================================================

# ----------------------------------------------------------
# def obsv_cst(A,B,C,D):

# ----------------------------------------------------------
e     = np.zeros((A.shape[1], 1))
e[-1] = 1

O = control.obsv(A, C)
[U, S, Vh] = linalg.svd(O)
V = Vh.T
S = np.diag(S)

S_inv = linalg.solve(S, np.eye(S.shape[0]))
T_inv = V @ S_inv @ U.conj().T
T1 = T_inv @ e;

# ----------------------------------------------------------
n  = A.shape[1]
T0 = np.zeros((n,n))

for i in range(1, n+1):
  column = np.linalg.matrix_power(A, n-i) @ T1
  T0[:, i-1] = column[:,0]

# ----------------------------------------------------------
Ad_t = linalg.solve(T0, A @ T0)
Ad_t[:-1,1:] = np.eye(n-1)
Ad_t[-1,1:] = 0
Bd_t = linalg.solve(T0, B)
Cd_t = C @ T0;
Dd_t = D;

  # return AT,BT,CT,DT,T0

# ----------------------------------------------------------
# Scaling
# [Ts, k] = sdf.dIIR_scaling(Ad,Bd,T0,f,ts)
# self.k = k
# ===========================================================================

# ----------------------------------------------------------
# def dIIR_scaling(Ad,Bd,T0,f,ts):
f = np.logspace(0,np.log10(fb),2**10)
T0_inv = linalg.solve(T0, np.eye(T0.shape[0]))
[f_i, phz] = sdf.delta_bode(Ad,Bd,T0_inv,0,f,ts)

# ----------------------------------------------------------
f_norm = np.zeros(Ad.shape[0])

for i in range(f_norm.shape[0]):
  f_norm[i] = linalg.norm(f_i[i], np.inf, axis=1)

Ts = np.zeros(Ad.shape)
k = np.zeros(f_norm.shape[0])
k_inv = np.zeros(f_norm.shape[0])

for i in range(f_norm.shape[0]):
  if i == 0:
    k[i] = 1/f_norm[i]
  else:
    k[i] = 1/(np.prod(k[:i])*f_norm[i])

  k_inv[i] = 2**np.floor(np.log2(ts/k[i]))/ts
  Ts[i,i] = np.prod(k_inv[0:i+1])

  # return Ts, k_inv

# ===========================================================================
k_inv = np.diag(k_inv)
[num_t, den_t] = signal.ss2tf(Ad_t,Bd_t,Cd_t,Dd_t)
num_ts = num_t.copy()
num_ts[0,1:] /= np.diag(Ts).T
den_ts = den_t.copy()
den_ts[1:] /= np.diag(Ts).T
den_ts[0] = 1

beta  = num_ts[0]
alpha = den_ts
# self.beta  = beta 
# self.alpha = alpha

# ===========================================================================
# ----------------------------------------------------------
# % Calculation of sensitivity matrix
# [S_mag, S_phz] = sdf.SD_dIIR_sensitivity(Ad,Bd,Cd,Dd,T0,Ts,f,ts)

# ----------------------------------------------------------
# def SD_dIIR_sensitivity(Ad,Bd,Cd,Dd,T0,Ts,f,ts):
# %Sensitivity due to feedthrough coefficient
B_beta = np.zeros((1, Ad.shape[1])).T
B_beta[0][0] = 1
B_beta = Ad @ T0 @ B_beta
S_beta0 = control.ss(Ad,B_beta,Cd,1)

# %Sensitivity due to numerator coefficients
S_beta = control.ss(Ad.T,Cd.T,Ts.T @ T0.T,0)

# %Sensitivity due to denominator coefficients
H = control.ss(Ad,Bd,Cd,Dd)
S_alpha = control.series(H, S_beta)
S_bsys = sdf.ss_concat_outputs(S_beta0, S_beta)
null_sys = control.ss(0, 0, 0, 0)
S_asys = sdf.ss_concat_outputs(null_sys, S_alpha)

[S_bmag,S_bphz] = sdf.delta_bode(S_bsys.A,S_bsys.B,S_bsys.C,S_bsys.D,f,ts)
[S_amag,S_aphz] = sdf.delta_bode(S_asys.A,S_asys.B,S_asys.C,S_asys.D,f,ts)
S_mag = np.squeeze(S_bmag + S_amag)
S_phz = np.squeeze(S_bphz + S_aphz)

# return S_mag, S_phz

# ===========================================================================
# % Calculation of quantization noise
# [sig_nom, sig_2_x_sd, H] = sdf.dDFIIt_noise_gain(Ad,Bd,Cd,Dd,k_inv,Ts,T0,f,ts)

# ----------------------------------------------------------
# def dDFIIt_noise_gain(Ad,Bd,Cd,Dd,K_inv,Ts,T0,f,ts):
# K_inv = k_inv
# % Sigma Delta Specifications (2nd Order)
n_sd = ts/3
NTF_num = [ts**2, 0, 0]
NTF_den = [ts**2, 2*ts, 1]
NTF = control.tf(NTF_num, NTF_den)
# print(NTF)
NTF = control.ss(control.tf(NTF_num, NTF_den))

# % noise gain due to input sigma delta
H_sd = control.ss(Ad,Bd,Cd,Dd);
sys_sd1 = control.series(NTF, H_sd)
[g1,phz] = sdf.delta_bode(sys_sd1.A,sys_sd1.B,sys_sd1.C,sys_sd1.D,f,ts)
sig_2_sd1 = n_sd*(np.squeeze(g1)**2)

# % noise gain due to output sigma delta
A = linalg.solve(Ts, linalg.solve(T0, Ad))
z = np.zeros(Ad.shape[1])
z[0] = 1
B = linalg.solve(Ts, linalg.solve(T0, Ad-np.eye(Ad.shape[0])))
B = B @ T0 @ z.T
B = B.reshape((Ad.shape[0],1))
C = Cd @ T0 @ Ts
D = 1
E_sd = control.ss(A, B, C, D)
sys_sd2 = control.series(NTF, E_sd)
[g2,phz] = sdf.delta_bode(sys_sd2.A,sys_sd2.B,sys_sd2.C,sys_sd2.D,f,ts)
sig_2_sd2 = n_sd*(np.squeeze(g2)**2)

# %noise gain due to scaling coefficient multiplication roundoff
sys_g0 = E_sd.copy()
sys_g = control.ss(Ad.T,Cd.T,Ts.T @ T0.T, 0)
sys_g.C[-1,:] = 0
sys_g.D[-1,:] = 0
sys_k = sdf.ss_concat_outputs(sys_g0, sys_g)
[m1,phz] = sdf.delta_bode(sys_k.A,sys_k.B,sys_k.C,sys_k.D,f,ts)
H = np.diag(((2*ts)/3)*np.trapz(np.squeeze(m1**2),f))

# %noise gain from input sigma delta to integrators
C = linalg.solve(Ts, linalg.solve(T0, np.eye(Ad.shape[0])))
C = k_inv @ C
sys_x_sd1 = control.ss(Ad,Bd,C,0)
sys_x_sd1 = control.series(NTF, sys_x_sd1)
[m_sys_x_sd1,phz] = sdf.delta_bode(sys_x_sd1.A,sys_x_sd1.B,sys_x_sd1.C,sys_x_sd1.D,f,ts)
sig_2_x_sd1 = n_sd*(np.squeeze(m_sys_x_sd1)**2)

# %noise gain from output sigma delta to integrators
z = np.zeros(Ad.shape[1])
z[0] = 1
B = Ad @ T0 @ Ts @ z.T
B = B.reshape((Ad.shape[0],1))
C = linalg.solve(Ts, linalg.solve(T0, np.eye(Ad.shape[0])))
C = k_inv @ C
sys_x_sd2 = control.series(NTF, control.ss(Ad, B, C, 0))
[m_sys_x_sd2,phz] = sdf.delta_bode(sys_x_sd2.A,sys_x_sd2.B,sys_x_sd2.C,sys_x_sd2.D,f,ts)
sig_2_x_sd2 = n_sd*(np.squeeze(m_sys_x_sd2)**2)

# % total SD output noise 
sig_2_nom = np.trapz(np.squeeze(sig_2_sd1),f) + np.trapz(np.squeeze(sig_2_sd2),f)
sig_2_x_sd = sig_2_x_sd1 + sig_2_x_sd2

# return sig_2_nom, sig_2_x_sd, H
# [sig_nom, sig_2_x_sd, H] = [sig_2_nom, sig_2_x_sd, H]

# ===========================================================================
SNR = 90
sig_noise = 10**(-(SNR/10))
p = .1*np.ones((1,S_mag.shape[1]))
s = np.sqrt(np.trapz(sig_2_x_sd)*(12*OSR));
S_mag = np.squeeze(S_mag)

# ===========================================================================
# q = sdf.bitwidth_opt(S_mag,p,H,sig_noise,s)
# ----------------------------------------------------------
# def bitwidth_opt(S,p,H,sig2_sd,sig2_x_sd):
# [S,p,H,sig2_sd,sig2_x_sd] = [S_mag,p,H,sig_noise,s]
import cvxpy as cp
n = S_mag.shape[0]
u = np.ones((n,1))
l = np.zeros((n,1))
f = np.ones(n)
f[0] = 3
s = np.append(s, 0).reshape(s.shape[0] + 1, 1)

# Define and solve the CVXPY problem.
q = cp.Variable((n,1))
prob = cp.Problem( cp.Maximize(f @ q),
                   [ cp.quad_form(q,H) <= sig_noise
                   , S_mag.T @ q <= p.T
                   , q >= s
                   ]
                 )
prob.solve()

# return q

# ----------------------------------------------------------
qs = np.log2(q.value)
qs[qs>0] = 0
qs = np.ceil(np.abs(qs)).T
bi = np.ceil(np.log2(np.maximum(np.abs(alpha),np.abs(beta)))) + 1
bw = bi + qs + 1
b_frac = qs

# ----------------------------------------------------------
# # % Simulink Model Bitwidth Parameters
shift = np.round(np.abs(np.log2(ts*k)))
bw_accum = 1 + np.ceil(np.abs(np.log2(ts))) + b_frac
print('q = \n', np.log2(q.value.T))
print('Coefficient bitwidths = \n', bw)


# # % %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
k_ts = k * ts
k_ts = np.append(k_ts, 0)
shift = np.append(shift, 1)

for idx, val in enumerate(alpha):
  print('accum[', idx, '] |' , bw_accum[0,idx] , b_frac[0,idx])
  print('alpha[', idx, '] |' , bw[0,idx]       , qs[0,idx]    )
  print('beta [', idx, '] |' , bw[0,idx]       , qs[0,idx]    )
  print('k_ts [', idx, '] |' , shift[idx] + 1  , shift[idx]   )
  print('-' * 40)

