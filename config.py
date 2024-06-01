import json
import screeninfo
import pyaudio
import re

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_data = {
            "scaling_factor": 1.0,
            "threshold1": 100,
            "threshold2": 500,
            "x_position": 960,
            "y_position": 980,
            "decay_factor": 0.95,
            "opacity_mode": "No Opacity",
            "fixed_opacity": 0.5,
            "dynamic_opacity_scaling": 0.5,
            "audio_device_index": 0,
            "update_interval": 1
        }
        self.data = self.default_data.copy()
        self.load()

    def load(self):
        try:
            with open(self.config_file, 'r') as file:
                self.data.update(json.load(file))
        except FileNotFoundError:
            pass
        # Ensure audio_device_index is present
        if "audio_device_index" not in self.data:
            self.data["audio_device_index"] = 0

    def save(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def reset_all(self):
        self.data = self.default_data.copy()
        self.save()

    def reset_position(self):
        screen = screeninfo.get_monitors()[0]
        self.data["x_position"] = screen.width // 2 - 600
        self.data["y_position"] = screen.height - 150
        self.save()

    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        devices = []
        pattern = re.compile(r"CABLE[-.\s]?Output", re.IGNORECASE)
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0 and pattern.search(dev['name']):
                devices.append((i, dev['name']))
        p.terminate()
        return devices
