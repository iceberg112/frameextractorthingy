import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import xml.etree.ElementTree as ET

# hex to argebee
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)

# take a lookie at the video
def process_video(video_path, hex_colors, output_folder, tolerance):
    target_colors = [np.array(hex_to_rgb(color), dtype=np.uint8) for color in hex_colors]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open video.")
        return
    
    frame_count = 0
    saved_frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        # convert h
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mask = np.zeros(rgb_frame.shape[:2], dtype=np.uint8)

        for target_color in target_colors:
            lower_bound = np.clip(target_color - tolerance, 0, 255)
            upper_bound = np.clip(target_color + tolerance, 0, 255)
            mask |= cv2.inRange(rgb_frame, lower_bound, upper_bound)
        
        if np.any(mask):
            saved_frame_count += 1
            output_path = os.path.join(output_folder, f"frame_{saved_frame_count:04d}.png")
            cv2.imwrite(output_path, frame)
            print(f"Saved {output_path}")
    
    cap.release()
    messagebox.showinfo("Process Complete", f"Processed {frame_count} frames, saved {saved_frame_count} frames.")

# browse thy video outbith
def browse_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if video_path:
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, video_path)

# browse thy output folder
def browse_output_folder():
    output_folder = filedialog.askdirectory()
    if output_folder:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, output_folder)

# add thy color
def add_color():
    hex_color = color_entry.get()
    if hex_color.startswith('#') and len(hex_color) == 7 and all(c in '0123456789ABCDEFabcdef' for c in hex_color[1:]):
        color_listbox.insert(tk.END, hex_color)
        color_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please provide a valid hex color in the format #RRGGBB.")

# delete thy selected color
def delete_color():
    selected_indices = color_listbox.curselection()
    for index in reversed(selected_indices):
        color_listbox.delete(index)

# DO THE PRIOCESSING
def start_processing():
    video_path = video_path_entry.get()
    hex_colors = list(color_listbox.get(0, tk.END))
    output_folder = output_folder_entry.get()
    tolerance = tolerance_scale.get()
    
    if not video_path or not hex_colors or not output_folder:
        messagebox.showwarning("Input Error", "Please provide all inputs (video file, hex colors, and output folder).")
        return
    
    process_video(video_path, hex_colors, output_folder, tolerance)

# save to the xml
def save_config():
    config_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
    if config_path:
        root = ET.Element("Configuration")
        ET.SubElement(root, "VideoPath").text = video_path_entry.get()
        ET.SubElement(root, "OutputFolder").text = output_folder_entry.get()
        colors = ET.SubElement(root, "Colors")
        for color in color_listbox.get(0, tk.END):
            ET.SubElement(colors, "Color").text = color
        ET.SubElement(root, "Tolerance").text = str(tolerance_scale.get())
        tree = ET.ElementTree(root)
        tree.write(config_path)
        messagebox.showinfo("Save Configuration", "Configuration saved successfully.")

# load from the xml
def load_config():
    config_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
    if config_path:
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        video_path = root.find("VideoPath").text
        output_folder = root.find("OutputFolder").text
        colors = [color.text for color in root.find("Colors").findall("Color")]
        tolerance = int(root.find("Tolerance").text)
        
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, video_path)
        
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, output_folder)
        
        color_listbox.delete(0, tk.END)
        for color in colors:
            color_listbox.insert(tk.END, color)
        
        tolerance_scale.set(tolerance)
        messagebox.showinfo("Load Configuration", "Configuration loaded successfully.")

#  Make gui.
root = tk.Tk()
root.title("frame extractor tool or somethging")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

video_path_label = tk.Label(frame, text="Video File:")
video_path_label.grid(row=0, column=0, sticky="e")

video_path_entry = tk.Entry(frame, width=50)
video_path_entry.grid(row=0, column=1, padx=5, pady=5)

browse_video_button = tk.Button(frame, text="Browse...", command=browse_video)
browse_video_button.grid(row=0, column=2, padx=5, pady=5)

color_label = tk.Label(frame, text="Hex Color (#RRGGBB):")
color_label.grid(row=1, column=0, sticky="e")

color_entry = tk.Entry(frame, width=50)
color_entry.grid(row=1, column=1, padx=5, pady=5)

add_color_button = tk.Button(frame, text="Add Color", command=add_color)
add_color_button.grid(row=1, column=2, padx=5, pady=5)

color_listbox_label = tk.Label(frame, text="Colors to Check:")
color_listbox_label.grid(row=2, column=0, sticky="e")

color_listbox = tk.Listbox(frame, width=50, height=6)
color_listbox.grid(row=2, column=1, padx=5, pady=5, columnspan=2)

delete_color_button = tk.Button(frame, text="Delete Selected Color", command=delete_color)
delete_color_button.grid(row=2, column=3, padx=5, pady=5)

tolerance_label = tk.Label(frame, text="Tolerance:")
tolerance_label.grid(row=3, column=0, sticky="e")

tolerance_frame = tk.Frame(frame)
tolerance_frame.grid(row=3, column=1, padx=5, pady=5)

tolerance_scale = tk.Scale(tolerance_frame, from_=0, to=255, orient=tk.HORIZONTAL, length=200)
tolerance_scale.set(0)
tolerance_scale.pack(side=tk.LEFT)

fine_tune_frame = tk.Frame(tolerance_frame)
fine_tune_frame.pack(side=tk.RIGHT)

fine_tune_minus = tk.Button(fine_tune_frame, text="-", command=lambda: tolerance_scale.set(tolerance_scale.get() - 1))
fine_tune_minus.pack(side=tk.LEFT)

fine_tune_plus = tk.Button(fine_tune_frame, text="+", command=lambda: tolerance_scale.set(tolerance_scale.get() + 1))
fine_tune_plus.pack(side=tk.RIGHT)

output_folder_label = tk.Label(frame, text="Output Folder:")
output_folder_label.grid(row=4, column=0, sticky="e")

output_folder_entry = tk.Entry(frame, width=50)
output_folder_entry.grid(row=4, column=1, padx=5, pady=5)

browse_output_folder_button = tk.Button(frame, text="Browse...", command=browse_output_folder)
browse_output_folder_button.grid(row=4, column=2, padx=5, pady=5)

start_button = tk.Button(frame, text="Start Processing", command=start_processing)
start_button.grid(row=5, column=0, columnspan=3, pady=5)

save_config_button = tk.Button(frame, text="Save Configuration", command=save_config)
save_config_button.grid(row=6, column=0, columnspan=3, pady=5)

load_config_button = tk.Button(frame, text="Load Configuration", command=load_config)
load_config_button.grid(row=7, column=0, columnspan=3, pady=5)

root.mainloop()

