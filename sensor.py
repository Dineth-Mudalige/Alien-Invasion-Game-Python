from settings import Settings
import explorepy
import numpy as np
import pylsl

from filter import DataFilter
from pynput.keyboard import Key,Controller

class Sensor:
    """The class shows the Sensor device"""
    def __init__(self, device_name):
        self.settings = Settings()
        self.settings.sensor_settings()
        self.device_name = device_name
        self.threshold = 1e3
        self.device_mode = device_name+self.settings.device_mode
        
    def _initialise(self):
        explorer = explorepy.Explore()
        explorer.connect(device_name=self.device_name)
        explorer.set_sampling_rate(sampling_rate=self.settings.sampling_rate)
        explorer.set_channels(channel_mask=self.settings.channel_mask)
        explorer.push2lsl()
    
    def _get_data(self):
        buffer = np.empty((self.settings.buffer_size,self.settings.num_active_channels))
        difference_buffer = np.empty((int(self.settings.buffer_size*(1-0.4)),2))
        streams = pylsl.resolve_stream('name',self.device_mode)
        inlet = pylsl.StreamInlet(streams[0])
        idx = 0
        keyboard = Controller()
        while True:
            value_array = inlet.pull_sample()
            for i in range(self.settings.num_active_channels):
                buffer[idx,i] = value_array[0][i]
            idx += 1
            if idx == self.settings.buffer_size:
                idx = 0
                filter = DataFilter(buffer)
                filtered_data = filter.get_output()
                difference_buffer[:,0] = np.abs(filtered_data[int(self.settings.buffer_size*0.4):,0] - filtered_data[int(self.settings.buffer_size*0.4):,1])
                difference_buffer[:,1] = np.abs(filtered_data[int(self.settings.buffer_size*0.4),2] - filtered_data[int(self.settings.buffer_size*0.4):,3])
                left_sum = np.sum(difference_buffer[:,0])
                right_sum = np.sum(difference_buffer[:,1])
                print(f'Left:{left_sum} Right:{right_sum}')
                if left_sum-right_sum > self.threshold:
                    keyboard.release(Key.left)
                    keyboard.press(Key.right)
                    print("Moving Left")
                elif right_sum-left_sum > self.threshold:
                    keyboard.release(Key.right)
                    keyboard.press(Key.left)
                    print("Moving Right")
                else:
                    print("Staying still")

            

if __name__ == '__main__':
    #   Make a game instance
    sensor = Sensor("Explore_8443")
    sensor._initialise()
    sensor._get_data()