import numpy as np
from scipy.signal import butter, filtfilt

class DataFilter:
    def __init__(self, input_matrix):
        # Initialize  filter parameters here
        self.data = input_matrix
        self.low_cutoff = 20
        self.high_cutoff = 100
        self.sampling_rate = 1000

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
            empty_array[:,i] = self.apply_filter(self.data[:,i])
        return empty_array