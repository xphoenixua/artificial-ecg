import numpy as np

class CycleSequence:

    def __init__(self, ecg_cycle, n):
        self.ecg_cycle = ecg_cycle
        self.new_t0 = self.ecg_cycle.time[-1]
        self.n = n
        self.time_seq = np.arange(0, self.new_t0 * self.n + self.ecg_cycle.Ts, self.ecg_cycle.Ts)
        self.amp_seq = np.concatenate((np.tile(self.ecg_cycle.amplitude[:-1], self.n), np.array([0])), axis=0)
    
    def alternate_t(self, alt):
        params = self.ecg_cycle.waves['T']
        a, mu, b1, b2 = params[0], params[1], params[2], params[3]
        lmbd_prev = 1
        for t_i in range(0, self.n):
            t1_1, t1_2 = params[4] + int(t_i * self.new_t0 / self.ecg_cycle.Ts), params[5] + int(t_i * self.new_t0 / self.ecg_cycle.Ts)
            t2_1, t2_2 = params[6] + int(t_i * self.new_t0 / self.ecg_cycle.Ts), params[7] + int(t_i * self.new_t0 / self.ecg_cycle.Ts)
            if lmbd_prev == 1:
                lmbd = 1 + alt / a
            elif lmbd_prev == (1 + alt / a):
                lmbd = 1
            interval_1 = self.time_seq[t1_1:t1_2+1]
            interval_2 = self.time_seq[t2_1+1:t2_2]
            self.amp_seq[t1_1:t1_2+1] = (a * lmbd) * np.exp(-(np.square(interval_1 - (mu + t_i * self.new_t0)) / (2*np.square(b1))))
            self.amp_seq[t2_1+1:t2_2] = (a * lmbd) * np.exp(-(np.square(interval_2 - (mu + t_i * self.new_t0)) / (2*np.square(b2))))
            lmbd_prev = lmbd

    def construct_sequence(self):
        self.amp_seq = np.concatenate((np.tile(self.ecg_cycle.amplitude[:-1], self.n), np.array([0])), axis=0)
