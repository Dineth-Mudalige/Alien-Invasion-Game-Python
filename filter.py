import numpy as np
from scipy.signal import butter, filtfilt, iirfilter, sosfreqz, sosfilt

class DataFilter:
    def __init__(self, input_matrix):
        # Initialize  filter parameters here
        self.data = input_matrix
        self.low_cutoff = 60
        self.high_cutoff = 300
        self.sampling_rate = 1000
        self.nyquist = 0.5 * self.sampling_rate
        self.center_freq = 50

    def apply_notch_filter(self, signal, Q=30):
        freq = self.center_freq / self.nyquist
        b,a = iirfilter(N=2,Wn=[freq - Q/(2*self.nyquist), freq + Q/(2*self.nyquist)], btype='bandstop', ftype='butter',fs=self.sampling_rate,output='ba')
        return filtfilt(b,a, signal)

    def apply_filter(self, data,order=5):
        # Implement  data filtering logic here
        nyquist = 0.5 * self.sampling_rate
        low = self.low_cutoff / nyquist
        high = self.high_cutoff / nyquist
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data)
    
    def get_output(self):
        # Get the shape of the existing array
        num_rows, num_cols = self.data.shape

        # Create an empty array of the same size
        empty_array = np.empty((num_rows, num_cols))
        for i in range(num_cols):
            filtered_data = self.apply_notch_filter(self.data[:,i])
            empty_array[:,i] = self.apply_filter(filtered_data)
        return empty_array

if __name__ == '__main__':
    Fs = 1000  # Sampling frequency
    t1 = np.linspace(0, 1, Fs, endpoint=False)  # Time vector
    t,tt = np.meshgrid(t1,t1)
    rows,columns = t.shape
    signal = np.sin(2 * np.pi * 60 * tt) + 0.5 * np.random.randn(rows, columns)
    sensor = DataFilter(signal)
    sensor.get_output()