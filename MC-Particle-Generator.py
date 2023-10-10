import tkinter as tk
from tkinter import filedialog, Toplevel
from tkinter.ttk import Button, Label
import cv2
import os
from PIL import Image, ImageTk, ImageGrab
import time


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("圖片/影片轉Minecraft指令")

        self.input_path = ""
        self.output_path = ""
        self.compression_factor = 1  # 初始壓縮因子為1
        self.practical_factor = 1  # 初始粒子因子為1
        self.skip_empty_pixels = False
        self.generate_xy_plane = False
        self.generate_yz_plane = False
        self.generate_xz_plane = False
        self.display_window = None
        self.paused = True
        self.current_frame = None
        self.selected_rgb = None  # 儲存選擇的RGB值
        self.rgb = []  # 初始化 rgb
        self.select_input_btn = tk.Button(root,
                                          text="選擇圖片/影片",
                                          command=self.select_input)
        self.select_input_btn.pack(pady=10)

        self.load_button = tk.Button(root,
                                     text="載入媒體",
                                     command=self.load_media)
        self.load_button.pack(pady=20)

        self.output_path_btn = tk.Button(root,
                                         text="選擇輸出位置",
                                         command=self.select_output_path)
        self.output_path_btn.pack(pady=10)

        self.compression_label = tk.Label(root, text="壓縮因子 (1 = 寬一格):")
        self.compression_label.pack()

        self.compression_entry = tk.Entry(root)
        self.compression_entry.pack()

        self.particle_label = tk.Label(root, text="粒子大小:")
        self.particle_label.pack()

        self.particle_entry = tk.Entry(root)
        self.particle_entry.pack()

        self.particle2_label = tk.Label(root, text="粒子數量:")
        self.particle2_label.pack()

        self.particle2_entry = tk.Entry(root)
        self.particle2_entry.pack()

        self.skip_empty_pixels_var = tk.BooleanVar()
        self.skip_empty_pixels_var.set(False)

        self.skip_empty_pixels_checkbox = tk.Checkbutton(
            root, text="跳過空白像素", variable=self.skip_empty_pixels_var)
        self.skip_empty_pixels_checkbox.pack()

        self.skip_picked_rgb_var = tk.BooleanVar()
        self.skip_picked_rgb_var.set(False)

        self.skip_picked_rgb_checkbox = tk.Checkbutton(
            root, text="跳過選取色值", variable=self.skip_picked_rgb_var)
        self.skip_picked_rgb_checkbox.pack()

        self.xy_plane_var = tk.BooleanVar()
        self.xy_plane_var.set(False)
        self.xy_plane_checkbox = tk.Checkbutton(root,
                                                text="生成在XY平面",
                                                variable=self.xy_plane_var)
        self.xy_plane_checkbox.pack()

        self.yz_plane_var = tk.BooleanVar()
        self.yz_plane_var.set(False)
        self.yz_plane_checkbox = tk.Checkbutton(root,
                                                text="生成在YZ平面",
                                                variable=self.yz_plane_var)
        self.yz_plane_checkbox.pack()

        self.xz_plane_var = tk.BooleanVar()
        self.xz_plane_var.set(False)
        self.xz_plane_checkbox = tk.Checkbutton(root,
                                                text="生成在XZ平面",
                                                variable=self.xz_plane_var)
        self.xz_plane_checkbox.pack()

        self.convert_btn = tk.Button(root, text="轉換", command=self.convert)
        self.convert_btn.pack(pady=10)

    def select_input(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            global display_file
            self.input_path = file_path
            display_file = file_path

    def load_media(self):
        filepath_open = display_file
        if filepath_open:
            if filepath_open.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.display_image(filepath_open)
            elif filepath_open.lower().endswith(('.mp4', '.avi', '.mkv')):
                self.display_video(filepath_open)

    def display_image(self, filepath_open):
        image = Image.open(filepath_open)
        photo = ImageTk.PhotoImage(image)

        if self.display_window:
            self.display_window.destroy()

        self.display_window = Toplevel(self.root)
        label = Label(self.display_window, image=photo)
        label.image = photo
        label.bind('<Button-1>', self.get_rgb_from_position)
        label.pack()

    def display_video(self, filepath_open):
        self.cap = cv2.VideoCapture(filepath_open)

        if self.display_window:
            self.display_window.destroy()

        self.display_window = Toplevel(self.root)
        self.canvas = tk.Canvas(
            self.display_window,
            width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.canvas.pack()

        self.canvas.bind('<Button-1>', self.get_rgb_from_video_position)

        Button(self.display_window, text="暫停/播放",
               command=self.toggle_pause).pack()

        self.paused = False
        self.update_frame()

    def update_frame(self):
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=self.current_frame)

                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas.image = photo
                self.root.after(10, self.update_frame)
            else:
                self.cap.release()

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused:
            self.update_frame()

    def get_rgb_from_position(self, event):
        x, y = event.x_root, event.y_root
        image = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
        rgb_value = image.getpixel((0, 0))
        if rgb_value not in self.rgb:  # 如果RGB值還未被儲存，則添加到列表
            self.rgb.append(rgb_value)
            print(f"選取的RGB值: {rgb_value}")
            print(self.rgb)

    def get_rgb_from_video_position(self, event):
        if self.paused and self.current_frame:
            rgb_value = self.current_frame.getpixel((event.x, event.y))
            if rgb_value not in self.rgb:  # 如果RGB值還未被儲存，則添加到列表
                self.rgb.append(rgb_value)
                print(f"選取的RGB值: {rgb_value}")
                print(self.rgb)

    def select_output_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path = folder_path

    def resize_image(self, img):
        width, height = img.size
        global aspect_ratio
        aspect_ratio = width / height
        new_width = int((16000 * aspect_ratio)**0.5)
        new_height = int(new_width / aspect_ratio)
        return img.resize((new_width, new_height), Image.ANTIALIAS)

    def convert(self):
        if not self.input_path or not self.output_path:
            return

        try:
            self.compression_factor = float(self.compression_entry.get())
        except ValueError:
            print("無效的壓縮因子，請輸入一個有效的數字")
            return

        if self.input_path.lower().endswith(
            ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')):
            # 如果輸入是影片文件，將其轉換為一系列圖片
            self.convert_video_to_images()
        elif self.input_path.lower().endswith(
            ('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            # 如果輸入是圖片文件，直接生成粒子指令
            self.convert_image_to_commands(self.input_path)
        else:
            print("不支援的檔案格式")

    def convert_video_to_images(self):
        # 讀取影片
        cap = cv2.VideoCapture(self.input_path)
        frame_rate = 20  # 目標每秒20幀

        output_images_folder = os.path.join(self.output_path, 'video_frames')
        os.makedirs(output_images_folder, exist_ok=True)

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % int(cap.get(cv2.CAP_PROP_FPS) / frame_rate) >= 0:
                # 每隔一段時間保存一個幀
                output_image_path = os.path.join(output_images_folder,
                                                 f'frame_{frame_count}.png')
                cv2.imwrite(output_image_path, frame)
                self.convert_image_to_commands(output_image_path)

            frame_count += 1
        cap.release()

    def convert_image_to_commands(self, image_path):
        img = Image.open(image_path).convert("RGB")

        self.practical2_factor = float(self.particle2_entry.get())

        if img.size[0] * img.size[1] > self.practical2_factor:
            img = self.resize_image(img)

        width, height = img.size

        self.practical_factor = float(self.particle_entry.get())

        commands = []
        skip_empty_pixels = self.skip_empty_pixels_var.get()  # 獲取勾選框的值
        skip_picked_color = self.skip_picked_rgb_var.get()
        generate_xy_plane = self.xy_plane_var.get()
        generate_yz_plane = self.yz_plane_var.get()
        generate_xz_plane = self.xz_plane_var.get()

        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))

                if skip_empty_pixels and r == g == b == 0:
                    continue  # 如果勾選框選中且像素為全0，跳過該像素
                if skip_picked_color and img.getpixel((x, y)) in self.rgb:
                    continue
                r_norm = round(r / 255, 7)
                g_norm = round(g / 255, 7)
                b_norm = round(b / 255, 7)
                x_comp = round(x / (self.compression_factor * width), 2)
                y_comp = round(
                    y / (self.compression_factor * height * aspect_ratio), 2)

                # 根據平面選項生成相應的指令
                if generate_xy_plane:
                    command_xy = f"particle dust {r_norm} {g_norm} {b_norm} {self.practical_factor} ~{x_comp} ~-{y_comp} ~0 0 0 0 0 0 force @a"
                    commands.append(command_xy)
                if generate_yz_plane:
                    command_yz = f"particle dust {r_norm} {g_norm} {b_norm} {self.practical_factor} ~0 ~{x_comp} ~{y_comp} 0 0 0 0 0 0 force @a"
                    commands.append(command_yz)
                if generate_xz_plane:
                    command_xz = f"particle dust {r_norm} {g_norm} {b_norm} {self.practical_factor} ~{x_comp} ~0 ~{y_comp} 0 0 0 0 0 0 force @a"
                    commands.append(command_xz)

        output_file_name = os.path.splitext(
            os.path.basename(image_path))[0] + "_commands.mcfunction"
        output_file_path = os.path.join(self.output_path, output_file_name)

        with open(output_file_path, "w") as f:
            for cmd in commands:
                f.write(cmd + "\n")

        print(f"轉換完成！已生成指令檔：{output_file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()