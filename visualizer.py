import tkinter as tk
import screeninfo

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
        threshold1 = self.settings.data['threshold1']
        threshold2 = self.settings.data['threshold2']
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
            if intensity > threshold2:
                return "red"
            elif intensity > threshold1:
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
