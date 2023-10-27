import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, sosfreqz, sosfilt

class DataFilter:
    def __init__(self, input_matrix):
        # Initialize  filter parameters here
        self.data = input_matrix
        self.low_cutoff = 2
        self.high_cutoff = 30
        self.sampling_rate = 1000
        self.nyquist = 0.5 * self.sampling_rate
        self.center_freq = 50

    def apply_notch_filter(self, signal, Q=100):
        freq = self.center_freq / self.nyquist
        sos = iirnotch(freq, Q)
        return sosfilt(sos, signal)

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