import numpy as np

# class of an ECG cycle
class CycleModel:
    # class attributes
    Fs = 2048 # sampling frequency in Hz
    Ts = 1000 / Fs # sampling period in ms

    def __init__(self, Fh, waves):
        # object attributes
        self.Fh = Fh # heart rate in beats/minute
        self.t0 = 60 * 1000 / self.Fh # duration of 1 cycle
        self.time = np.arange(0, self.t0 + self.Ts, self.Ts) # time sequence of a single cycle with a step of sampling period over given duration
        self.waves = waves # wave data (mean, std, amplitude)

    # create amplitude sequence for cycle
    def construct_cycle(self):
        self.amplitude = np.zeros(self.time.shape[0])
        for w in self.waves:
            # getting wave data
            params = self.waves[w]
            a, mu, b1, b2 = params[0], params[1], params[2], params[3]
            # getting bin number for start and end of wave
            t1 = (np.abs(self.time - (mu - 3*b1))).argmin()
            t2 = (np.abs(self.time - (mu + 3*b2))).argmin()
            t1_1, t1_2 = t1, np.floor(mu/self.Ts).astype(int)
            t2_1, t2_2 = np.floor(mu/self.Ts).astype(int), t2
            # saving start and end coordinates as wave data
            self.waves[w][4], self.waves[w][5] = t1_1, t1_2
            self.waves[w][6], self.waves[w][7] = t2_1, t2_2
            interval_1 = self.time[t1_1:t1_2+1]
            interval_2 = self.time[t2_1+1:t2_2]
            # calculating amplitude as a gaussian function using given wave data
            self.amplitude[t1_1:t1_2+1] = a * np.exp(-(np.square(interval_1 - mu) / (2*np.square(b1))))
            self.amplitude[t2_1+1:t2_2] = a * np.exp(-(np.square(interval_2 - mu) / (2*np.square(b2))))

    # getting wave start and end coordinates for defining possible mean or std ranges
    def get_t_lims(self, w):
        temp = list(self.waves)
        if w == 'P':
            t_prev, t_next = 0, self.waves[temp[temp.index(w) + 1]][4]
        elif w == 'T':
            t_prev, t_next = self.waves[temp[temp.index(w) - 1]][7], int(self.time[-1] / self.Ts)
        else:
            t_prev, t_next = self.waves[temp[temp.index(w) - 1]][7], self.waves[temp[temp.index(w) + 1]][4]
        return t_prev, t_next

    # calculate possible slider range for mean of a wave
    def find_range_mu(self, w):
        params = self.waves[w]
        mu, b1, b2 = np.ceil(params[1]).astype(int), np.ceil(params[2]).astype(int), np.ceil(params[3]).astype(int)
        
        t_prev, t_next = self.get_t_lims(w)

        mu_i_prev = mu
        for mu_i in range(mu, 0, -1):
            t1 = (np.abs(self.time - (mu_i - 3*b1))).argmin()
            if w == 'P' and t1 == t_prev:
                break
            if t1 < t_prev:
                break
            mu_i_prev = mu_i
        m_b = mu_i_prev

        mu_i_prev = mu
        for mu_i in range(mu, int(self.time[-1]), 1):
            t2 = (np.abs(self.time - (mu_i + 3*b2))).argmin()
            if w == 'T' and t2 == t_next:
                break
            elif t2 > t_next:
                break
            mu_i_prev = mu_i
        m_e = mu_i_prev
        
        return m_b, m_e
    
    # calculate possible slider range for left std side of a wave
    def find_range_b1(self, w):
        params = self.waves[w]
        mu, b1 = np.ceil(params[1]).astype(int), np.ceil(params[2]).astype(int)
        
        t_prev, _ = self.get_t_lims(w)
        b1_b = 1

        b1_i_prev = b1
        for b1_i in range(b1, int(self.time[-1]), 1):
            t2 = (np.abs(self.time - (mu - 3*b1_i))).argmin()
            if t2 < t_prev:
                break
            if w == 'P' and t2 == t_prev:
                break
            b1_i_prev = b1_i
        b1_e = b1_i_prev
        
        return b1_b, b1_e
        
    # calculate possible slider range for right std side of a wave
    def find_range_b2(self, w):
        params = self.waves[w]
        mu, b2 = np.ceil(params[1]).astype(int), np.ceil(params[3]).astype(int)
        
        _, t_next = self.get_t_lims(w)

        b2_b = 1

        b2_i_prev = b2
        for b2_i in range(b2, int(self.time[-1]), 1):
            t2 = (np.abs(self.time - (mu + 3*b2_i))).argmin()
            if t2 > t_next:
                break
            if w == 'T' and t2 == t_next:
                break
            b2_i_prev = b2_i
        b2_e = b2_i_prev
        
        return b2_b, b2_e

    # calculate new wave data after scaling it with new heart rate value
    def fh_normalization(self, Fh_new):
        for w in self.waves:
            # unpacking wave data
            params = self.waves[w]
            mu, b1, b2, t1_1, t1_2, t2_1, t2_2 = params[1], params[2], params[3], params[4], params[5], params[6], params[7]
            
            self.waves[w][1] = mu * self.Fh / Fh_new
            self.waves[w][2] = b1 * self.Fh / Fh_new
            self.waves[w][3] = b2 * self.Fh / Fh_new
            self.waves[w][4] = t1_1 * self.Fh / Fh_new
            self.waves[w][5] = t1_2 * self.Fh / Fh_new
            self.waves[w][6] = t2_1 * self.Fh / Fh_new
            self.waves[w][7] = t2_2 * self.Fh / Fh_new
