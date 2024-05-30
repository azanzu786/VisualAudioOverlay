import ctypes
import win32gui
import win32con
import win32api
import pyaudio
import numpy as np
import tkinter as tk
from tkinter import ttk
import screeninfo
import json
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from scipy.ndimage import uniform_filter1d

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_data = {
            "scaling_factor": 1,
            "footstep_threshold": 50,
            "gunshot_threshold": 200,
            "x_position": None,
            "y_position": None,
            "decay_factor": 0.95,
            "opacity_mode": "No Opacity",
            "fixed_opacity": 0.5,
            "dynamic_opacity_scaling": 0.5
        }
        self.data = self.default_data.copy()
        self.load()

    def load(self):
        try:
            with open(self.config_file, 'r') as file:
                self.data.update(json.load(file))
        except FileNotFoundError:
            pass

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

class AudioVisualizer(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.update_geometry()

        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.overrideredirect(True)
        
        self.canvas = tk.Canvas(self, width=1200, height=100, bg='black', highlightthickness=0)
        self.canvas.pack()
        
        self.left_rect = self.canvas.create_rectangle(595, 30, 600, 70, fill='blue')
        self.right_rect = self.canvas.create_rectangle(600, 30, 605, 70, fill='red')
        
        self.left_intensity_smoothed = 0
        self.right_intensity_smoothed = 0

    def update_geometry(self):
        screen = screeninfo.get_monitors()[0]
        if self.settings.data['x_position'] is None or self.settings.data['y_position'] is None:
            x_position = screen.width // 2 - 600
            y_position = screen.height - 150
            self.settings.data['x_position'] = x_position
            self.settings.data['y_position'] = y_position
        else:
            x_position = self.settings.data['x_position']
            y_position = self.settings.data['y_position']
        self.geometry(f"1200x100+{x_position}+{y_position}")

    def update_visual(self, left_intensity, right_intensity):
        scaling_factor = self.settings.data['scaling_factor']
        footstep_threshold = self.settings.data['footstep_threshold']
        gunshot_threshold = self.settings.data['gunshot_threshold']
        decay_factor = self.settings.data['decay_factor']
        opacity_mode = self.settings.data['opacity_mode']
        fixed_opacity = self.settings.data['fixed_opacity']
        dynamic_opacity_scaling = self.settings.data['dynamic_opacity_scaling']

        max_width = 595

        self.left_intensity_smoothed = max(left_intensity, self.left_intensity_smoothed * decay_factor)
        self.right_intensity_smoothed = max(right_intensity, self.right_intensity_smoothed * decay_factor)

        left_width = min(self.left_intensity_smoothed * scaling_factor, max_width)
        right_width = min(self.right_intensity_smoothed * scaling_factor, max_width)

        def get_color(intensity):
            if intensity > gunshot_threshold:
                return "red"
            elif intensity > footstep_threshold:
                return "yellow"
            else:
                return "blue"

        left_color = get_color(self.left_intensity_smoothed)
        right_color = get_color(self.right_intensity_smoothed)

        if opacity_mode == "Fixed Opacity":
            if self.left_intensity_smoothed > self.right_intensity_smoothed:
                right_color = self.apply_opacity(right_color, fixed_opacity)
            else:
                left_color = self.apply_opacity(left_color, fixed_opacity)
        elif opacity_mode == "Dynamic Opacity":
            if self.left_intensity_smoothed > self.right_intensity_smoothed:
                opacity = 1.0 - dynamic_opacity_scaling * (self.left_intensity_smoothed - self.right_intensity_smoothed) / max(self.left_intensity_smoothed, 1)
                right_color = self.apply_opacity(right_color, opacity)
            else:
                opacity = 1.0 - dynamic_opacity_scaling * (self.right_intensity_smoothed - self.left_intensity_smoothed) / max(self.right_intensity_smoothed, 1)
                left_color = self.apply_opacity(left_color, opacity)

        self.canvas.itemconfig(self.left_rect, fill=left_color)
        self.canvas.itemconfig(self.right_rect, fill=right_color)
        self.canvas.coords(self.left_rect, 600 - left_width, 30, 600, 70)
        self.canvas.coords(self.right_rect, 600, 30, 600 + right_width, 70)

    def apply_opacity(self, color, opacity):
        rgb = self.winfo_rgb(color)
        rgb = (rgb[0] // 256, rgb[1] // 256, rgb[2] // 256)
        return f"#{int(rgb[0] * opacity):02x}{int(rgb[1] * opacity):02x}{int(rgb[2] * opacity):02x}"

    def update_settings(self, settings):
        self.settings = settings
        self.update_geometry()

class ConfigPanel(tk.Toplevel):
    def __init__(self, parent, settings, callback):
        super().__init__(parent)
        self.settings = settings
        self.callback = callback
        self.screen = screeninfo.get_monitors()[0]

        self.title("Configuration")
        self.geometry("400x600")

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        self.scaling_factor_label = ttk.Label(self, text="Scaling Factor:")
        self.scaling_factor_label.pack(pady=5)
        self.scaling_factor_slider = ttk.Scale(self, from_=0.1, to=10, orient=tk.HORIZONTAL, command=self.update_scaling_factor)
        self.scaling_factor_slider.pack(pady=5)
        self.scaling_factor_value = tk.Entry(self, justify='center')
        self.scaling_factor_value.pack(pady=5)
        self.scaling_factor_value.bind("<Return>", self.manual_scaling_factor)

        self.footstep_threshold_label = ttk.Label(self, text="Footstep Threshold:")
        self.footstep_threshold_label.pack(pady=5)
        self.footstep_threshold_slider = ttk.Scale(self, from_=0, to=1000, orient=tk.HORIZONTAL, command=self.update_footstep_threshold)
        self.footstep_threshold_slider.pack(pady=5)
        self.footstep_threshold_value = tk.Entry(self, justify='center')
        self.footstep_threshold_value.pack(pady=5)
        self.footstep_threshold_value.bind("<Return>", self.manual_footstep_threshold)

        self.gunshot_threshold_label = ttk.Label(self, text="Gunshot Threshold:")
        self.gunshot_threshold_label.pack(pady=5)
        self.gunshot_threshold_slider = ttk.Scale(self, from_=0, to=5000, orient=tk.HORIZONTAL, command=self.update_gunshot_threshold)
        self.gunshot_threshold_slider.pack(pady=5)
        self.gunshot_threshold_value = tk.Entry(self, justify='center')
        self.gunshot_threshold_value.pack(pady=5)
        self.gunshot_threshold_value.bind("<Return>", self.manual_gunshot_threshold)

        self.x_position_label = ttk.Label(self, text="X Position:")
        self.x_position_label.pack(pady=5)
        self.x_position_slider = ttk.Scale(self, from_=0, to_=self.screen.width - 1200, orient=tk.HORIZONTAL, command=self.update_x_position)
        self.x_position_slider.pack(pady=5)
        self.x_position_value = tk.Entry(self, justify='center')
        self.x_position_value.pack(pady=5)
        self.x_position_value.bind("<Return>", self.manual_x_position)

        self.y_position_label = ttk.Label(self, text="Y Position:")
        self.y_position_label.pack(pady=5)
        self.y_position_slider = ttk.Scale(self, from_=0, to_=self.screen.height - 100, orient=tk.HORIZONTAL, command=self.update_y_position)
        self.y_position_slider.pack(pady=5)
        self.y_position_value = tk.Entry(self, justify='center')
        self.y_position_value.pack(pady=5)
        self.y_position_value.bind("<Return>", self.manual_y_position)

        self.decay_factor_label = ttk.Label(self, text="Decay Factor:")
        self.decay_factor_label.pack(pady=5)
        self.decay_factor_slider = ttk.Scale(self, from_=0.1, to=1, orient=tk.HORIZONTAL, command=self.update_decay_factor)
        self.decay_factor_slider.pack(pady=5)
        self.decay_factor_value = tk.Entry(self, justify='center')
        self.decay_factor_value.pack(pady=5)
        self.decay_factor_value.bind("<Return>", self.manual_decay_factor)

        self.opacity_mode_label = ttk.Label(self, text="Opacity Mode:")
        self.opacity_mode_label.pack(pady=5)
        self.opacity_mode = ttk.Combobox(self, values=["No Opacity", "Fixed Opacity", "Dynamic Opacity"], state="readonly")
        self.opacity_mode.pack(pady=5)
        self.opacity_mode.bind("<<ComboboxSelected>>", self.update_opacity_mode)

        self.fixed_opacity_label = ttk.Label(self, text="Fixed Opacity Value:")
        self.fixed_opacity_label.pack(pady=5)
        self.fixed_opacity_slider = ttk.Scale(self, from_=0.1, to=1, orient=tk.HORIZONTAL, command=self.update_fixed_opacity)
        self.fixed_opacity_slider.pack(pady=5)
        self.fixed_opacity_value = tk.Entry(self, justify='center')
        self.fixed_opacity_value.pack(pady=5)
        self.fixed_opacity_value.bind("<Return>", self.manual_fixed_opacity)

        self.dynamic_opacity_scaling_label = ttk.Label(self, text="Dynamic Opacity Scaling:")
        self.dynamic_opacity_scaling_label.pack(pady=5)
        self.dynamic_opacity_scaling_slider = ttk.Scale(self, from_=0.1, to=1, orient=tk.HORIZONTAL, command=self.update_dynamic_opacity_scaling)
        self.dynamic_opacity_scaling_slider.pack(pady=5)
        self.dynamic_opacity_scaling_value = tk.Entry(self, justify='center')
        self.dynamic_opacity_scaling_value.pack(pady=5)
        self.dynamic_opacity_scaling_value.bind("<Return>", self.manual_dynamic_opacity_scaling)

        self.reset_all_button = ttk.Button(self, text="Reset All Settings", command=self.reset_all)
        self.reset_all_button.pack(pady=10)

        self.reset_position_button = ttk.Button(self, text="Reset Position Settings", command=self.reset_position)
        self.reset_position_button.pack(pady=10)

        self.save_button = ttk.Button(self, text="Save", command=self.save_config)
        self.save_button.pack(pady=20)

    def load_config(self):
        self.scaling_factor_slider.set(self.settings.data["scaling_factor"])
        self.scaling_factor_value.delete(0, tk.END)
        self.scaling_factor_value.insert(0, self.settings.data["scaling_factor"])

        self.footstep_threshold_slider.set(self.settings.data["footstep_threshold"])
        self.footstep_threshold_value.delete(0, tk.END)
        self.footstep_threshold_value.insert(0, self.settings.data["footstep_threshold"])

        self.gunshot_threshold_slider.set(self.settings.data["gunshot_threshold"])
        self.gunshot_threshold_value.delete(0, tk.END)
        self.gunshot_threshold_value.insert(0, self.settings.data["gunshot_threshold"])

        self.x_position_slider.set(self.settings.data["x_position"] or 0)
        self.x_position_value.delete(0, tk.END)
        self.x_position_value.insert(0, self.settings.data["x_position"] or 0)

        self.y_position_slider.set(self.settings.data["y_position"] or 0)
        self.y_position_value.delete(0, tk.END)
        self.y_position_value.insert(0, self.settings.data["y_position"] or 0)

        self.decay_factor_slider.set(self.settings.data["decay_factor"])
        self.decay_factor_value.delete(0, tk.END)
        self.decay_factor_value.insert(0, self.settings.data["decay_factor"])

        self.opacity_mode.set(self.settings.data["opacity_mode"])

        self.fixed_opacity_slider.set(self.settings.data["fixed_opacity"])
        self.fixed_opacity_value.delete(0, tk.END)
        self.fixed_opacity_value.insert(0, self.settings.data["fixed_opacity"])

        self.dynamic_opacity_scaling_slider.set(self.settings.data["dynamic_opacity_scaling"])
        self.dynamic_opacity_scaling_value.delete(0, tk.END)
        self.dynamic_opacity_scaling_value.insert(0, self.settings.data["dynamic_opacity_scaling"])

        self.update_values()

    def update_values(self):
        self.scaling_factor_value.delete(0, tk.END)
        self.scaling_factor_value.insert(0, float(self.scaling_factor_slider.get()))

        self.footstep_threshold_value.delete(0, tk.END)
        self.footstep_threshold_value.insert(0, int(self.footstep_threshold_slider.get()))

        self.gunshot_threshold_value.delete(0, tk.END)
        self.gunshot_threshold_value.insert(0, int(self.gunshot_threshold_slider.get()))

        self.x_position_value.delete(0, tk.END)
        self.x_position_value.insert(0, int(self.x_position_slider.get()))

        self.y_position_value.delete(0, tk.END)
        self.y_position_value.insert(0, int(self.y_position_slider.get()))

        self.decay_factor_value.delete(0, tk.END)
        self.decay_factor_value.insert(0, float(self.decay_factor_slider.get()))

        self.fixed_opacity_value.delete(0, tk.END)
        self.fixed_opacity_value.insert(0, float(self.fixed_opacity_slider.get()))

        self.dynamic_opacity_scaling_value.delete(0, tk.END)
        self.dynamic_opacity_scaling_value.insert(0, float(self.dynamic_opacity_scaling_slider.get()))

    def update_scaling_factor(self, _):
        self.settings.data["scaling_factor"] = float(self.scaling_factor_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_scaling_factor(self, event):
        self.settings.data["scaling_factor"] = float(self.scaling_factor_value.get())
        self.scaling_factor_slider.set(self.settings.data["scaling_factor"])
        self.callback(self.settings)

    def update_footstep_threshold(self, _):
        self.settings.data["footstep_threshold"] = int(self.footstep_threshold_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_footstep_threshold(self, event):
        self.settings.data["footstep_threshold"] = int(self.footstep_threshold_value.get())
        self.footstep_threshold_slider.set(self.settings.data["footstep_threshold"])
        self.callback(self.settings)

    def update_gunshot_threshold(self, _):
        self.settings.data["gunshot_threshold"] = int(self.gunshot_threshold_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_gunshot_threshold(self, event):
        self.settings.data["gunshot_threshold"] = int(self.gunshot_threshold_value.get())
        self.gunshot_threshold_slider.set(self.settings.data["gunshot_threshold"])
        self.callback(self.settings)

    def update_x_position(self, _):
        self.settings.data["x_position"] = int(self.x_position_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_x_position(self, event):
        self.settings.data["x_position"] = int(self.x_position_value.get())
        self.x_position_slider.set(self.settings.data["x_position"])
        self.callback(self.settings)

    def update_y_position(self, _):
        self.settings.data["y_position"] = int(self.y_position_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_y_position(self, event):
        self.settings.data["y_position"] = int(self.y_position_value.get())
        self.y_position_slider.set(self.settings.data["y_position"])
        self.callback(self.settings)

    def update_decay_factor(self, _):
        self.settings.data["decay_factor"] = float(self.decay_factor_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_decay_factor(self, event):
        self.settings.data["decay_factor"] = float(self.decay_factor_value.get())
        self.decay_factor_slider.set(self.settings.data["decay_factor"])
        self.callback(self.settings)

    def update_opacity_mode(self, event):
        self.settings.data["opacity_mode"] = self.opacity_mode.get()
        self.callback(self.settings)

    def update_fixed_opacity(self, _):
        self.settings.data["fixed_opacity"] = float(self.fixed_opacity_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_fixed_opacity(self, event):
        self.settings.data["fixed_opacity"] = float(self.fixed_opacity_value.get())
        self.fixed_opacity_slider.set(self.settings.data["fixed_opacity"])
        self.callback(self.settings)

    def update_dynamic_opacity_scaling(self, _):
        self.settings.data["dynamic_opacity_scaling"] = float(self.dynamic_opacity_scaling_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_dynamic_opacity_scaling(self, event):
        self.settings.data["dynamic_opacity_scaling"] = float(self.dynamic_opacity_scaling_value.get())
        self.dynamic_opacity_scaling_slider.set(self.settings.data["dynamic_opacity_scaling"])
        self.callback(self.settings)

    def save_config(self):
        self.settings.save()

    def reset_all(self):
        self.settings.reset_all()
        self.load_config()
        self.callback(self.settings)

    def reset_position(self):
        self.settings.reset_position()
        self.load_config()
        self.callback(self.settings)

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
    
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']} - Input Channels: {dev['maxInputChannels']}, Output Channels: {dev['maxOutputChannels']}")
        if 'CABLE Output' in dev['name']:
            device_index = i
            channels = dev['maxInputChannels']
            break
    
    if device_index is None:
        raise ValueError("Virtual Audio Cable output not found. Ensure it is installed and set as the default output device.")
    
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

    settings = Config()
    app = AudioVisualizer(settings)

    def show_config_panel():
        ConfigPanel(app, settings, app.update_settings)

    def quit_app(icon, item):
        icon.stop()
        app.quit()

    def create_image():
        image = Image.new('RGB', (64, 64), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, 64, 64), fill="blue")
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
        app.after(1, update)
    
    update()
    app.mainloop()
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()
