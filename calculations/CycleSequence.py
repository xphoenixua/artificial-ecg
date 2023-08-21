import numpy as np

class CycleSequence:
    def __init__(self, ecg_cycle=None, n=None, time_seq=None, amp_seq=None):
        # this condition is needed when initializing ECG sequence from single ECG cylce
        if time_seq is None:
            self.ecg_cycle = ecg_cycle
            self.new_t0 = self.ecg_cycle.time[-1]
            self.n = n
            self.time_seq = np.arange(0, self.new_t0 * self.n + self.ecg_cycle.Ts, self.ecg_cycle.Ts)
            # np.tile is used here for pasting same cycle n times in 
            self.amp_seq = np.concatenate((np.tile(self.ecg_cycle.amplitude[:-1], self.n), np.array([0])), axis=0)
        # this condition is needed when initializing ECG sequence with passing only time and amplitude sequences
        # e.g. composing filtered or noisy ECG from processed raw ECG sequence
        else:
            self.time_seq = time_seq
            self.amp_seq = amp_seq
    
    # add alternation of T waves to sequence
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

    # add noise to sequence
    def generate_noise(self, noise_level):
        h0 = np.max(self.amp_seq)
        amp_size = self.amp_seq.shape
        noise = noise_level * np.random.uniform(low=-h0, high=h0, size=amp_size)
        return noise
