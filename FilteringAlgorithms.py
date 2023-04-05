import numpy as np
import CycleModel as cm

def exp_filter(ecg_sequence, alpha):
    z0 = ecg_sequence.amp_seq
    K = z0.shape[0]
    z0_tilda = np.zeros(K)
    z0_tilda[0] = z0[0]
    for k in range(1, K):
        z0_tilda[k] = z0_tilda[k-1] + alpha * (z0[k] - z0_tilda[k-1])
    return z0_tilda

def moving_average(ecg_sequence, winwidth):
    z0 = ecg_sequence.amp_seq
    W0_ms = winwidth
    Ts = cm.CycleModel.Ts
    W0_bin = np.ceil(W0_ms / Ts).astype(int)
    K = z0.shape[0]
    lmbd = 1 / W0_bin
    z0_tilda = np.zeros(K)
    z0_tilda[W0_bin-1] = lmbd * np.sum(z0[0:W0_bin])
    for k in range(W0_bin, K):
        z0_tilda[k] = z0_tilda[k-1] + lmbd * (z0[k] - z0[k-1-W0_bin])
    return z0_tilda