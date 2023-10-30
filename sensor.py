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
        self.device_mode = device_name+self.settings.device_mode
        self.thresholds = {'zcr':10,'mav':50,'rms':10} # Tested thresholds : {'zcr':10,'mav':50,'rms':10}
        
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
                ## Classify the single channel(Uncomment if commented to work with 1 channel, Always keep one commented)
                self._comparator(filtered_data[int(self.settings.buffer_size*0.4):,:],keyboard,channels=[0,2])
                # ## Classify the second channel(Uncomment if commented to work with 2 channel, Always keep one commented)
                # self._comparator(difference_buffer,keyboard,channels=[0,1])
    
    def _get_zero_crossing_rate(self,signal):
        zcr = 0
        for i in range(1,len(signal)):
            if (signal[i-1] >= 0) and (signal[i] < 0) or (signal[i-1] < 0) and (signal[i] >= 0):
                zcr += 1
        return zcr
    
    def root_mean_square(self,signal):
        rms = np.sqrt(np.mean(np.square(signal)))
        return rms
    
    def mean_absolute_value(self,signal):
        mav = np.mean(np.abs(signal))
        return mav
    
    def _get_value_dict(self,signal):
        return {'zcr':self._get_zero_crossing_rate(signal),'rms':self.root_mean_square(signal),'mav':self.mean_absolute_value(signal)}

    def _comparator(self,input_matrix,keyboard,params =['rms','mav'],channels = [0,1]):
        left_dict = self._get_value_dict(input_matrix[:,channels[0]])
        right_dict = self._get_value_dict(input_matrix[:,channels[1]])
        conditions_fulfiled = 0
        for val in params:
            if left_dict[val] - right_dict[val] >= self.thresholds[val]:
                conditions_fulfiled+=1
            elif right_dict[val] - left_dict[val] >= self.thresholds[val]:
                conditions_fulfiled-=1
        if conditions_fulfiled == len(params):
            keyboard.release(Key.right)
            keyboard.press(Key.left)
            # keyboard.tap(Key.left)
            print("Moving Left")
        elif conditions_fulfiled == -1*len(params):
            keyboard.release(Key.left)
            keyboard.press(Key.right)
            # keyboard.tap(Key.right)
            print("Moving Right")
        else:
            keyboard.release(Key.right)
            keyboard.release(Key.left)
            print("Standing Still")

if __name__ == '__main__':
    #   Make a game instance
    sensor = Sensor("Explore_8441")
    sensor._initialise()
    sensor._get_data()