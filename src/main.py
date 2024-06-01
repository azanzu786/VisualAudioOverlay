import pyaudio
import numpy as np
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageTk, Image as PILImage
from scipy.ndimage import uniform_filter1d

from config import Config
from visualizer import AudioVisualizer
from config_panel import ConfigPanel

def get_audio_data(stream, channels, frames_per_buffer):
    try:
        data = np.frombuffer(stream.read(frames_per_buffer, exception_on_overflow=False), dtype=np.int16)
        left_channel = data[0::2]
        right_channel = data[1::2] if channels > 1 else data[0::2]
        return left_channel, right_channel
    except Exception as e:
        print(f"Error capturing audio: {e}")
        return np.zeros(frames_per_buffer // 2), np.zeros(frames_per_buffer // 2)

def get_intensities(left_channel, right_channel, smoothing_window=10):
    left_intensity = uniform_filter1d(np.abs(left_channel), size=smoothing_window).mean()
    right_intensity = uniform_filter1d(np.abs(right_channel), size=smoothing_window).mean()
    return left_intensity, right_intensity

def main():
    p = pyaudio.PyAudio()
    
    settings = Config()
    device_index = settings.data.get("audio_device_index", 0)  # Use default index if not found
    channels = p.get_device_info_by_index(device_index)['maxInputChannels']

    if channels == 0:
        raise ValueError("No input channels available on the selected device.")
    
    frames_per_buffer = 128
    sample_rate = 44100
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=frames_per_buffer)

    app = AudioVisualizer(settings)

    def show_config_panel():
        ConfigPanel(app, settings, app.update_settings)

    def quit_app(icon, item):
        icon.stop()
        app.quit()

    def create_image():
        image = PILImage.open("icon.png")
        return image

    def setup_tray():
        icon = pystray.Icon("AudioVisualizer")
        icon.menu = pystray.Menu(
            item('Open Config', lambda: show_config_panel()),
            item('Quit', lambda: quit_app(icon, None))
        )
        icon.icon = create_image()
        icon.run()

    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.daemon = True
    tray_thread.start()
    
    def update():
        left, right = get_audio_data(stream, channels, frames_per_buffer)
        left_intensity, right_intensity = get_intensities(left, right)
        
        app.left_intensity_smoothed = max(left_intensity, app.left_intensity_smoothed * settings.data["decay_factor"])
        app.right_intensity_smoothed = max(right_intensity, app.right_intensity_smoothed * settings.data["decay_factor"])
        
        app.update_visual(app.left_intensity_smoothed, app.right_intensity_smoothed)
        app.after(settings.data["update_interval"], update)
    
    update()
    app.mainloop()
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()
