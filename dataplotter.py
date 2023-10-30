from settings import Settings
import explorepy
import numpy as np
import pylsl
import matplotlib.pyplot as plt

from filter import DataFilter

class DataPlotter:
    def __init__(self, device_name):
        self.settings = Settings()
        self.settings.sensor_settings()
        self.device_name = device_name
        self.device_mode = device_name + self.settings.device_mode

    def _initialise(self):
        explorer = explorepy.Explore()
        explorer.connect(device_name=self.device_name)
        explorer.set_sampling_rate(sampling_rate=self.settings.sampling_rate)
        explorer.set_channels(channel_mask=self.settings.channel_mask)
        explorer.push2lsl()

    def _get_data(self):
        buffer = np.empty((self.settings.buffer_size, self.settings.num_active_channels))
        streams = pylsl.resolve_stream('name', self.device_mode)
        inlet = pylsl.StreamInlet(streams[0])
        idx = 0

        fig, axs = plt.subplots(self.settings.num_active_channels, 2, figsize=(12, 8))
        fig.suptitle("Sensor Readings")

        for row in range(self.settings.num_active_channels):
            raw_ax = axs[row, 0]
            filtered_ax = axs[row, 1]

            raw_ax.set_title(f"Channel {row + 1} (Raw)")
            filtered_ax.set_title(f"Channel {row + 1} (Filtered)")

        while True:
            value_array = inlet.pull_sample()
            for i in range(self.settings.num_active_channels):
                buffer[idx, i] = value_array[0][i]

            idx += 1
            if idx == self.settings.buffer_size:
                idx = 0
                filter = DataFilter(buffer)
                filtered_data = filter.get_output()

                for i in range(self.settings.num_active_channels):
                    raw_ax = axs[i, 0]
                    filtered_ax = axs[i, 1]

                    raw_ax.clear()
                    filtered_ax.clear()

                    raw_ax.plot(buffer[:, i], color='blue')
                    filtered_ax.plot(filtered_data[:, i], color='red')
                    filtered_ax.set_ylim(-400,400)

                    # Calculate ZCR, RMS, and MAV for the filtered data
                    values = self._get_value_dict(filtered_data[int(self.settings.buffer_size*0.4):,i])

                    # Display ZCR, RMS, and MAV values below the filtered data plot
                    filtered_ax.text(0.5, -0.15, f"ZCR: {values['zcr']:.2f} RMS: {values['rms']:.2f} MAV: {values['mav']:.2f}",
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    transform=filtered_ax.transAxes
                                    )

                    # Add a vertical dashed line in the filtered subplot
                    vertical_line_index = self.settings.buffer_size*0.4  # Adjust this index as needed
                    filtered_ax.axvline(x=vertical_line_index, color='black', linestyle='--')

                    # Add a horizontal dashed line at a specified point in the filtered subplot
                    # horizontal_line_value = 0.5  # Adjust this value as needed
                    # filtered_ax.axhline(y=horizontal_line_value, color='black', linestyle='--')

                fig.canvas.flush_events()

                plt.pause(0.1)
    def _get_zero_crossing_rate(self,signal):
        zcr = 0
        for i in range(1,len(signal)):
            if (signal[i-1] > 0) and (signal[i] < 0) or (signal[i-1] < 0) and (signal[i] > 0):
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

if __name__ == '__main__':
    sensor = DataPlotter("Explore_8441")
    sensor._initialise()
    sensor._get_data()
