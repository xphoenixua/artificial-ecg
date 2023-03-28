import numpy as np

class CycleSequence:

    def __init__(self, ecg_cycle, n):
        self.Fh = ecg_cycle.Fh
        self.waves = ecg_cycle.waves
        self.n = n
        t0 = (60 * 1000 / self.Fh) * self.n
        self.time_seq = np.arange(0, t0 + ecg_cycle.Ts, ecg_cycle.Ts)
        self.amp_cycle = ecg_cycle.amplitude

    def update_wave(self, w, data):
        self.waves[w] = data

    def construct_cycle(self):
        self.amplitude = np.zeros(self.time.shape[0])
        for w in self.waves:
            params = self.waves[w]
            a, mu, b1, b2 = params[0], params[1], params[2], params[3]
            t1 = (np.abs(self.time - (mu - 3*b1))).argmin()
            t2 = (np.abs(self.time - (mu + 3*b2))).argmin()
            self.waves[w][4], self.waves[w][5] = t1, t2
            interval_1 = self.time[t1:np.floor(mu/self.Ts).astype(int)+1]
            interval_2 = self.time[np.floor(mu/self.Ts).astype(int)+1:t2]
            self.amplitude[t1:np.floor(mu/self.Ts).astype(int)+1] = a * np.exp(-(np.square(interval_1 - mu) / (2*np.square(b1))))
            self.amplitude[np.floor(mu/self.Ts).astype(int)+1:t2] = a * np.exp(-(np.square(interval_2 - mu) / (2*np.square(b2))))
    
    def construct_sequence(self):
        self.amp_seq = np.concatenate((np.tile(self.amp_cycle[:-1], self.n), np.array([0])), axis=0)
