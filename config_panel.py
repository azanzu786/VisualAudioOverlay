import tkinter as tk
from tkinter import ttk
import screeninfo

#TODO: Make this better
class ConfigPanel(tk.Toplevel):
    def __init__(self, parent, settings, callback):
        super().__init__(parent)
        self.settings = settings
        self.callback = callback
        self.screen = screeninfo.get_monitors()[0]

        self.title("Configuration")
        self.geometry("400x600")

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.bind_mouse_wheel()

        self.inner_frame = ttk.Frame(self.scrollable_frame)
        self.inner_frame.pack(expand=True, padx=50)

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        self.scaling_factor_label = ttk.Label(self.inner_frame, text="Scaling Factor:")
        self.scaling_factor_label.pack(pady=5, anchor="center")
        self.scaling_factor_slider = ttk.Scale(self.inner_frame, from_=0.1, to=10, orient=tk.HORIZONTAL, command=self.update_scaling_factor)
        self.scaling_factor_slider.pack(pady=5, fill="x")
        self.scaling_factor_value = tk.Entry(self.inner_frame, justify='center')
        self.scaling_factor_value.pack(pady=5, fill="x")
        self.scaling_factor_value.bind("<Return>", self.manual_scaling_factor)

        self.threshold1_label = ttk.Label(self.inner_frame, text="Threshold 1:")
        self.threshold1_label.pack(pady=5, anchor="center")
        self.threshold1_slider = ttk.Scale(self.inner_frame, from_=0, to=1000, orient=tk.HORIZONTAL, command=self.update_threshold1)
        self.threshold1_slider.pack(pady=5, fill="x")
        self.threshold1_value = tk.Entry(self.inner_frame, justify='center')
        self.threshold1_value.pack(pady=5, fill="x")
        self.threshold1_value.bind("<Return>", self.manual_threshold1)

        self.threshold2_label = ttk.Label(self.inner_frame, text="Threshold 2:")
        self.threshold2_label.pack(pady=5, anchor="center")
        self.threshold2_slider = ttk.Scale(self.inner_frame, from_=0, to=5000, orient=tk.HORIZONTAL, command=self.update_threshold2)
        self.threshold2_slider.pack(pady=5, fill="x")
        self.threshold2_value = tk.Entry(self.inner_frame, justify='center')
        self.threshold2_value.pack(pady=5, fill="x")
        self.threshold2_value.bind("<Return>", self.manual_threshold2)

        self.x_position_label = ttk.Label(self.inner_frame, text="X Position:")
        self.x_position_label.pack(pady=5, anchor="center")
        self.x_position_slider = ttk.Scale(self.inner_frame, from_=0, to_=self.screen.width - 1200, orient=tk.HORIZONTAL, command=self.update_x_position)
        self.x_position_slider.pack(pady=5, fill="x")
        self.x_position_value = tk.Entry(self.inner_frame, justify='center')
        self.x_position_value.pack(pady=5, fill="x")
        self.x_position_value.bind("<Return>", self.manual_x_position)

        self.y_position_label = ttk.Label(self.inner_frame, text="Y Position:")
        self.y_position_label.pack(pady=5, anchor="center")
        self.y_position_slider = ttk.Scale(self.inner_frame, from_=0, to_=self.screen.height - 100, orient=tk.HORIZONTAL, command=self.update_y_position)
        self.y_position_slider.pack(pady=5, fill="x")
        self.y_position_value = tk.Entry(self.inner_frame, justify='center')
        self.y_position_value.pack(pady=5, fill="x")
        self.y_position_value.bind("<Return>", self.manual_y_position)

        self.decay_factor_label = ttk.Label(self.inner_frame, text="Decay Factor:")
        self.decay_factor_label.pack(pady=5, anchor="center")
        self.decay_factor_slider = ttk.Scale(self.inner_frame, from_=0.1, to=1, orient=tk.HORIZONTAL, command=self.update_decay_factor)
        self.decay_factor_slider.pack(pady=5, fill="x")
        self.decay_factor_value = tk.Entry(self.inner_frame, justify='center')
        self.decay_factor_value.pack(pady=5, fill="x")
        self.decay_factor_value.bind("<Return>", self.manual_decay_factor)

        self.update_interval_label = ttk.Label(self.inner_frame, text="Update Interval (ms):")
        self.update_interval_label.pack(pady=5, anchor="center")
        self.update_interval_slider = ttk.Scale(self.inner_frame, from_=1, to=100, orient=tk.HORIZONTAL, command=self.update_update_interval)
        self.update_interval_slider.pack(pady=5, fill="x")
        self.update_interval_value = tk.Entry(self.inner_frame, justify='center')
        self.update_interval_value.pack(pady=5, fill="x")
        self.update_interval_value.bind("<Return>", self.manual_update_interval)

        self.opacity_mode_label = ttk.Label(self.inner_frame, text="Opacity Mode:")
        self.opacity_mode_label.pack(pady=5, anchor="center")
        self.opacity_mode = ttk.Combobox(self.inner_frame, values=["No Opacity", "Fixed Opacity", "Dynamic Opacity"], state="readonly")
        self.opacity_mode.pack(pady=5, fill="x")
        self.opacity_mode.bind("<<ComboboxSelected>>", self.update_opacity_mode)

        self.fixed_opacity_label = ttk.Label(self.inner_frame, text="Fixed Opacity Value:")
        self.fixed_opacity_label.pack(pady=5, anchor="center")
        self.fixed_opacity_slider = ttk.Scale(self.inner_frame, from_=0.1, to=1, orient=tk.HORIZONTAL, command=self.update_fixed_opacity)
        self.fixed_opacity_slider.pack(pady=5, fill="x")
        self.fixed_opacity_value = tk.Entry(self.inner_frame, justify='center')
        self.fixed_opacity_value.pack(pady=5, fill="x")
        self.fixed_opacity_value.bind("<Return>", self.manual_fixed_opacity)

        self.dynamic_opacity_scaling_label = ttk.Label(self.inner_frame, text="Dynamic Opacity Scaling:")
        self.dynamic_opacity_scaling_label.pack(pady=5, anchor="center")
        self.dynamic_opacity_scaling_slider = ttk.Scale(self.inner_frame, from_=0.1, to=1, orient=tk.HORIZONTAL, command=self.update_dynamic_opacity_scaling)
        self.dynamic_opacity_scaling_slider.pack(pady=5, fill="x")
        self.dynamic_opacity_scaling_value = tk.Entry(self.inner_frame, justify='center')
        self.dynamic_opacity_scaling_value.pack(pady=5, fill="x")
        self.dynamic_opacity_scaling_value.bind("<Return>", self.manual_dynamic_opacity_scaling)

        self.audio_device_label = ttk.Label(self.inner_frame, text="Audio Device:")
        self.audio_device_label.pack(pady=5, anchor="center")
        self.audio_device = ttk.Combobox(self.inner_frame, state="readonly")
        self.audio_device.pack(pady=5, fill="x")
        self.audio_device.bind("<<ComboboxSelected>>", self.update_audio_device)

        self.reset_all_button = ttk.Button(self.inner_frame, text="Reset All Settings", command=self.reset_all)
        self.reset_all_button.pack(pady=10, fill="x")

        self.reset_position_button = ttk.Button(self.inner_frame, text="Reset Position Settings", command=self.reset_position)
        self.reset_position_button.pack(pady=10, fill="x")

        self.save_button = ttk.Button(self.inner_frame, text="Save", command=self.save_config)
        self.save_button.pack(pady=20, fill="x")

    def bind_mouse_wheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def load_config(self):
        self.scaling_factor_slider.set(self.settings.data["scaling_factor"])
        self.scaling_factor_value.delete(0, tk.END)
        self.scaling_factor_value.insert(0, self.settings.data["scaling_factor"])

        self.threshold1_slider.set(self.settings.data["threshold1"])
        self.threshold1_value.delete(0, tk.END)
        self.threshold1_value.insert(0, self.settings.data["threshold1"])

        self.threshold2_slider.set(self.settings.data["threshold2"])
        self.threshold2_value.delete(0, tk.END)
        self.threshold2_value.insert(0, self.settings.data["threshold2"])

        self.x_position_slider.set(self.settings.data["x_position"] or 0)
        self.x_position_value.delete(0, tk.END)
        self.x_position_value.insert(0, self.settings.data["x_position"] or 0)

        self.y_position_slider.set(self.settings.data["y_position"] or 0)
        self.y_position_value.delete(0, tk.END)
        self.y_position_value.insert(0, self.settings.data["y_position"] or 0)

        self.decay_factor_slider.set(self.settings.data["decay_factor"])
        self.decay_factor_value.delete(0, tk.END)
        self.decay_factor_value.insert(0, self.settings.data["decay_factor"])

        self.update_interval_slider.set(self.settings.data["update_interval"])
        self.update_interval_value.delete(0, tk.END)
        self.update_interval_value.insert(0, self.settings.data["update_interval"])

        self.opacity_mode.set(self.settings.data["opacity_mode"])

        self.fixed_opacity_slider.set(self.settings.data["fixed_opacity"])
        self.fixed_opacity_value.delete(0, tk.END)
        self.fixed_opacity_value.insert(0, self.settings.data["fixed_opacity"])

        self.dynamic_opacity_scaling_slider.set(self.settings.data["dynamic_opacity_scaling"])
        self.dynamic_opacity_scaling_value.delete(0, tk.END)
        self.dynamic_opacity_scaling_value.insert(0, self.settings.data["dynamic_opacity_scaling"])

        audio_devices = self.settings.get_audio_devices()
        self.audio_device['values'] = [f"{i}: {name}" for i, name in audio_devices]
        
        if self.settings.data['audio_device_index'] < len(audio_devices):
            self.audio_device.set(f"{self.settings.data['audio_device_index']}: {audio_devices[self.settings.data['audio_device_index']][1]}")
        else:
            self.settings.data['audio_device_index'] = 0
            if audio_devices:
                self.audio_device.set(f"0: {audio_devices[0][1]}")
            else:
                self.audio_device.set("No compatible devices found")

        self.update_values()

    def update_values(self):
        self.scaling_factor_value.delete(0, tk.END)
        self.scaling_factor_value.insert(0, float(self.scaling_factor_slider.get()))

        self.threshold1_value.delete(0, tk.END)
        self.threshold1_value.insert(0, int(self.threshold1_slider.get()))

        self.threshold2_value.delete(0, tk.END)
        self.threshold2_value.insert(0, int(self.threshold2_slider.get()))

        self.x_position_value.delete(0, tk.END)
        self.x_position_value.insert(0, int(self.x_position_slider.get()))

        self.y_position_value.delete(0, tk.END)
        self.y_position_value.insert(0, int(self.y_position_slider.get()))

        self.decay_factor_value.delete(0, tk.END)
        self.decay_factor_value.insert(0, float(self.decay_factor_slider.get()))

        self.update_interval_value.delete(0, tk.END)
        self.update_interval_value.insert(0, int(self.update_interval_slider.get()))

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

    def update_threshold1(self, _):
        self.settings.data["threshold1"] = int(self.threshold1_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_threshold1(self, event):
        self.settings.data["threshold1"] = int(self.threshold1_value.get())
        self.threshold1_slider.set(self.settings.data["threshold1"])
        self.callback(self.settings)

    def update_threshold2(self, _):
        self.settings.data["threshold2"] = int(self.threshold2_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_threshold2(self, event):
        self.settings.data["threshold2"] = int(self.threshold2_value.get())
        self.threshold2_slider.set(self.settings.data["threshold2"])
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

    def update_update_interval(self, _):
        self.settings.data["update_interval"] = int(self.update_interval_slider.get())
        self.update_values()
        self.callback(self.settings)

    def manual_update_interval(self, event):
        self.settings.data["update_interval"] = int(self.update_interval_value.get())
        self.update_interval_slider.set(self.settings.data["update_interval"])
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

    def update_audio_device(self, event):
        self.settings.data["audio_device_index"] = int(self.audio_device.get().split(":")[0])
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
