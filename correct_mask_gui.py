import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import glob
import sys
from io import StringIO

class MaskCorrectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mask修正工具")
        self.root.geometry("1800x1000")  # 增大整体窗口
        
        # 变量初始化
        self.image_folder = ""
        self.mask_folder = ""
        self.image_files = []
        self.mask_files = []
        self.current_index = 0
        
        self.original_image = None
        self.mask_image = None
        self.display_image = None
        self.display_mask = None
        self.current_mask_path = None  # 当前mask文件路径
        
        self.canvas_width = 550  # 增大canvas尺寸
        self.canvas_height = 500
        
        # 绘制相关变量
        self.drawing = False
        self.brush_size = 10
        self.drawing_mode = "add"  # "add" or "remove"
        
        # 叠加显示相关变量
        self.overlay_alpha = 0.5
        self.show_overlay = True
        
        self.setup_ui()
        self.redirect_stdout()
    
    def redirect_stdout(self):
        """重定向标准输出到GUI日志框"""
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget
            
            def write(self, message):
                if message.strip():  # 只显示非空消息
                    self.text_widget.insert(tk.END, message)
                    self.text_widget.see(tk.END)
                    self.text_widget.update()
            
            def flush(self):
                pass
        
        # 保存原始stdout
        self.original_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.log_text)
    
    def safe_imread(self, filepath, flags=cv2.IMREAD_COLOR):
        """安全读取图像，支持中文路径"""
        try:
            # 使用numpy读取，支持中文路径
            with open(filepath, 'rb') as f:
                image_data = f.read()
            
            # 将字节数据转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            
            # 解码图像
            image = cv2.imdecode(nparr, flags)
            return image
        except Exception as e:
            print(f"读取图像失败: {filepath}, 错误: {e}")
            return None
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件夹选择
        ttk.Button(control_frame, text="选择图像文件夹", 
                  command=self.select_image_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="选择Mask文件夹", 
                  command=self.select_mask_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        # 图像导航
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="上一张", command=self.prev_image).pack(side=tk.LEFT)
        self.image_label = ttk.Label(nav_frame, text="0/0")
        self.image_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="下一张", command=self.next_image).pack(side=tk.LEFT)
        
        # 跳转功能
        jump_frame = ttk.Frame(nav_frame)
        jump_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(jump_frame, text="跳转到:").pack(side=tk.LEFT)
        self.jump_entry = ttk.Entry(jump_frame, width=6)
        self.jump_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.jump_entry.bind("<Return>", self.jump_to_image)
        ttk.Button(jump_frame, text="跳转", command=self.jump_to_image).pack(side=tk.LEFT)
        
        # 主显示区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图像显示区域
        image_frame = ttk.Frame(content_frame)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 中间显示区域
        display_frame = ttk.Frame(image_frame)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 原始图像显示
        left_frame = ttk.LabelFrame(display_frame, text="原始图像")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        self.image_canvas = tk.Canvas(left_frame, width=self.canvas_width, 
                                     height=self.canvas_height, bg="white")
        self.image_canvas.pack(padx=5, pady=5)
        
        # Mask显示和编辑
        middle_frame = ttk.LabelFrame(display_frame, text="Mask (可编辑)")
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 3))
        
        self.mask_canvas = tk.Canvas(middle_frame, width=self.canvas_width, 
                                    height=self.canvas_height, bg="black")
        self.mask_canvas.pack(padx=5, pady=5)
        
        # 叠加显示
        right_frame = ttk.LabelFrame(display_frame, text="叠加显示")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        
        self.overlay_canvas = tk.Canvas(right_frame, width=self.canvas_width, 
                                       height=self.canvas_height, bg="white")
        self.overlay_canvas.pack(padx=5, pady=5)
        
        # 绑定鼠标事件到mask canvas
        self.mask_canvas.bind("<Button-1>", self.start_draw)
        self.mask_canvas.bind("<B1-Motion>", self.draw)
        self.mask_canvas.bind("<ButtonRelease-1>", self.stop_draw)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(content_frame, text="系统日志")
        log_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=40, height=25, 
                                                 wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # 清除日志按钮
        ttk.Button(log_frame, text="清除日志", command=self.clear_log).pack(pady=5)
        
        # 底部工具栏
        tool_frame = ttk.Frame(image_frame)
        tool_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 第一行工具
        tool_row1 = ttk.Frame(tool_frame)
        tool_row1.pack(fill=tk.X, pady=(0, 5))
        
        # 绘制工具
        ttk.Label(tool_row1, text="笔刷大小:").pack(side=tk.LEFT)
        self.brush_scale = tk.Scale(tool_row1, from_=1, to=50, orient=tk.HORIZONTAL, 
                                   variable=tk.IntVar(value=10))
        self.brush_scale.pack(side=tk.LEFT, padx=5)
        
        # 绘制模式
        self.mode_var = tk.StringVar(value="add")
        ttk.Radiobutton(tool_row1, text="添加", variable=self.mode_var, 
                       value="add").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tool_row1, text="擦除", variable=self.mode_var, 
                       value="remove").pack(side=tk.LEFT, padx=5)
        
        # 第二行工具 - 叠加控制
        tool_row2 = ttk.Frame(tool_frame)
        tool_row2.pack(fill=tk.X)
        
        # 叠加透明度控制
        ttk.Label(tool_row2, text="透明度:").pack(side=tk.LEFT)
        self.alpha_scale = tk.Scale(tool_row2, from_=0.1, to=1.0, resolution=0.1,
                                   orient=tk.HORIZONTAL, command=self.update_overlay)
        self.alpha_scale.set(0.5)
        self.alpha_scale.pack(side=tk.LEFT, padx=5)
        
        # 叠加开关
        self.overlay_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tool_row2, text="显示叠加", variable=self.overlay_var,
                       command=self.toggle_overlay).pack(side=tk.LEFT, padx=10)
        
        # 操作按钮
        ttk.Button(tool_row2, text="重置Mask", command=self.reset_mask).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tool_row2, text="保存修改", command=self.save_mask).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tool_row2, text="自动保存", command=self.toggle_auto_save).pack(side=tk.RIGHT, padx=5)
        
        # 自动保存状态
        self.auto_save = False
        
    def clear_log(self):
        """清除日志内容"""
        self.log_text.delete(1.0, tk.END)
        print("日志已清除")
    
    def select_image_folder(self):
        folder = filedialog.askdirectory(title="选择图像文件夹")
        if folder:
            self.image_folder = folder
            self.load_image_files()
            
    def select_mask_folder(self):
        folder = filedialog.askdirectory(title="选择Mask文件夹")
        if folder:
            self.mask_folder = folder
            self.load_mask_files()
            
    def load_image_files(self):
        if not self.image_folder:
            return
            
        # 支持常见图像格式
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        self.image_files = []
        
        for ext in extensions:
            # 只搜索小写扩展名，glob会自动匹配大小写不敏感的文件系统
            files = glob.glob(os.path.join(self.image_folder, ext))
            self.image_files.extend(files)
            
        # 去重并排序
        self.image_files = list(set(self.image_files))
        self.image_files.sort()
        self.current_index = 0
        
        print(f"图像文件夹: 找到 {len(self.image_files)} 个文件")
        
        if self.image_files:
            self.update_display()
        else:
            print("警告: 未找到支持的图像文件")
        
    def load_mask_files(self):
        if not self.mask_folder:
            return
            
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        self.mask_files = []
        
        for ext in extensions:
            # 只搜索小写扩展名，glob会自动匹配大小写不敏感的文件系统
            files = glob.glob(os.path.join(self.mask_folder, ext))
            self.mask_files.extend(files)
            
        # 去重并排序
        self.mask_files = list(set(self.mask_files))
        self.mask_files.sort()
        
        print(f"Mask文件夹: 找到 {len(self.mask_files)} 个文件")
        
        if self.image_files:  # 只有在有图像文件时才更新显示
            self.update_display()

    def get_corresponding_mask(self, image_path):
        """根据图像文件名找到对应的mask文件"""
        if not self.mask_files:
            return None
            
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        
        for mask_path in self.mask_files:
            mask_name = os.path.splitext(os.path.basename(mask_path))[0]
            if image_name == mask_name or image_name in mask_name or mask_name in image_name:
                return mask_path
        return None
        
    def update_display(self):
        if not self.image_files:
            return
            
        # 确保索引在有效范围内
        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1
            
        # 更新图像计数标签
        self.image_label.config(text=f"{self.current_index + 1}/{len(self.image_files)}")
        
        # 加载当前图像
        image_path = self.image_files[self.current_index]
        print(f"[{self.current_index + 1}/{len(self.image_files)}] {os.path.basename(image_path)}")
        
        # 使用安全读取方法
        self.original_image = self.safe_imread(image_path)
        
        if self.original_image is None:
            print(f"错误: 无法读取图像")
            return
            
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        
        # 加载对应的mask
        mask_path = self.get_corresponding_mask(image_path)
        if mask_path and os.path.exists(mask_path):
            self.current_mask_path = mask_path
            self.mask_image = self.safe_imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if self.mask_image is None:
                # 如果读取失败，创建空mask
                h, w = self.original_image.shape[:2]
                self.mask_image = np.zeros((h, w), dtype=np.uint8)
                print("警告: mask文件损坏，已创建空mask")
            else:
                print(f"加载mask: {os.path.basename(mask_path)}")
        else:
            # 如果没有对应的mask，创建一个空的mask并设置保存路径
            h, w = self.original_image.shape[:2]
            self.mask_image = np.zeros((h, w), dtype=np.uint8)
            if self.mask_folder:
                image_name = os.path.splitext(os.path.basename(image_path))[0]
                self.current_mask_path = os.path.join(self.mask_folder, f"{image_name}.png")
                print("创建新mask")
            else:
                self.current_mask_path = None
                print("警告: 未设置mask文件夹")
            
        self.display_images()

    def display_images(self):
        if self.original_image is None:
            return
            
        # 调整图像大小以适应canvas
        h, w = self.original_image.shape[:2]
        scale = min(self.canvas_width/w, self.canvas_height/h)
        new_w, new_h = int(w*scale), int(h*scale)
        
        # 显示原始图像
        resized_image = cv2.resize(self.original_image, (new_w, new_h))
        self.display_image = Image.fromarray(resized_image)
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        self.image_canvas.delete("all")
        self.image_canvas.create_image(self.canvas_width//2, self.canvas_height//2, 
                                      image=self.photo_image)
        
        # 显示mask
        resized_mask = cv2.resize(self.mask_image, (new_w, new_h))
        self.display_mask = Image.fromarray(resized_mask)
        self.photo_mask = ImageTk.PhotoImage(self.display_mask)
        
        self.mask_canvas.delete("all")
        self.mask_canvas.create_image(self.canvas_width//2, self.canvas_height//2, 
                                     image=self.photo_mask)
        
        # 显示叠加图像
        self.update_overlay_display(resized_image, resized_mask)
        
        # 保存缩放比例用于绘制
        self.scale_factor = scale
        
    def update_overlay_display(self, resized_image, resized_mask):
        """更新叠加显示"""
        if not self.overlay_var.get():
            # 如果不显示叠加，只显示原始图像
            self.photo_overlay = ImageTk.PhotoImage(Image.fromarray(resized_image))
        else:
            # 创建彩色mask
            colored_mask = np.zeros_like(resized_image)
            colored_mask[:,:,0] = resized_mask  # 红色通道显示mask
            
            # 混合图像和mask
            alpha = self.alpha_scale.get()
            overlay_image = cv2.addWeighted(resized_image, 1-alpha, colored_mask, alpha, 0)
            
            # 在mask区域添加轮廓
            contours, _ = cv2.findContours(resized_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay_image, contours, -1, (0, 255, 0), 2)  # 绿色轮廓
            
            self.photo_overlay = ImageTk.PhotoImage(Image.fromarray(overlay_image))
        
        self.overlay_canvas.delete("all")
        self.overlay_canvas.create_image(self.canvas_width//2, self.canvas_height//2, 
                                        image=self.photo_overlay)
    
    def update_overlay(self, value=None):
        """更新叠加透明度"""
        if self.original_image is not None and self.mask_image is not None:
            self.display_images()
    
    def toggle_overlay(self):
        """切换叠加显示"""
        if self.original_image is not None and self.mask_image is not None:
            self.display_images()
        
    def start_draw(self, event):
        self.drawing = True
        self.draw(event)
        
    def draw(self, event):
        if not self.drawing or self.mask_image is None:
            return
            
        # 获取绘制参数
        brush_size = self.brush_scale.get()
        mode = self.mode_var.get()
        
        # 转换画布坐标到图像坐标
        canvas_x = event.x
        canvas_y = event.y
        
        # 计算图像在canvas中的位置
        h, w = self.mask_image.shape
        scaled_w = int(w * self.scale_factor)
        scaled_h = int(h * self.scale_factor)
        
        offset_x = (self.canvas_width - scaled_w) // 2
        offset_y = (self.canvas_height - scaled_h) // 2
        
        # 转换到缩放后图像坐标
        img_x = int((canvas_x - offset_x) / self.scale_factor)
        img_y = int((canvas_y - offset_y) / self.scale_factor)
        
        # 检查坐标是否在图像范围内
        if 0 <= img_x < w and 0 <= img_y < h:
            # 在原始mask上绘制
            color = 255 if mode == "add" else 0
            cv2.circle(self.mask_image, (img_x, img_y), brush_size, color, -1)
            
            # 更新显示
            self.display_images()
            
            # 自动保存
            if self.auto_save:
                self.save_mask(show_message=False)
    
    def stop_draw(self, event):
        self.drawing = False
        mode_text = "添加" if self.mode_var.get() == "add" else "擦除"
        # 只在有实际绘制时才输出日志
        
    def reset_mask(self):
        if self.mask_image is not None:
            self.mask_image.fill(0)
            self.display_images()
            print("mask已重置")

    def save_mask(self, show_message=True):
        if self.mask_image is None or not self.current_mask_path:
            if show_message:
                print("警告: 无法保存mask")
            return False
            
        try:
            # 确保保存目录存在
            save_dir = os.path.dirname(self.current_mask_path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 使用PIL保存，支持中文路径
            mask_pil = Image.fromarray(self.mask_image)
            mask_pil.save(self.current_mask_path)
            
            if show_message:
                print(f"保存成功: {os.path.basename(self.current_mask_path)}")
            return True
        except Exception as e:
            print(f"保存失败: {str(e)}")
            return False

    def toggle_auto_save(self):
        """切换自动保存模式"""
        self.auto_save = not self.auto_save
        status = "开启" if self.auto_save else "关闭"
        print(f"自动保存: {status}")

    def save_all_masks(self):
        if not self.mask_folder:
            print("警告: 请先选择mask文件夹")
            return
            
        print("提示: 保存所有功能需要您逐张检查并保存")
        
    def prev_image(self):
        if not self.image_files:
            print("错误: 没有加载图像文件")
            return
            
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
        else:
            print("提示: 已经是第一张图像")
            
    def next_image(self):
        if not self.image_files:
            print("错误: 没有加载图像文件")
            return
            
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.update_display()
        else:
            print("提示: 已经是最后一张图像")
    
    def jump_to_image(self, event=None):
        """跳转到指定的图像"""
        if not self.image_files:
            print("错误: 没有加载图像文件")
            return
            
        try:
            target_index = int(self.jump_entry.get()) - 1  # 用户输入从1开始，内部索引从0开始
            
            if 0 <= target_index < len(self.image_files):
                self.current_index = target_index
                self.update_display()
                print(f"跳转到第 {target_index + 1} 张图像")
            else:
                print(f"错误: 请输入1到{len(self.image_files)}之间的数字")
                
        except ValueError:
            print("错误: 请输入有效的数字")
        
        # 清空输入框
        self.jump_entry.delete(0, tk.END)

    def __del__(self):
        """恢复标准输出"""
        if hasattr(self, 'original_stdout'):
            sys.stdout = self.original_stdout

def main():
    root = tk.Tk()
    app = MaskCorrectionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()




























































