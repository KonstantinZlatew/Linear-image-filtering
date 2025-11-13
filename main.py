import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class LinearFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Линейна филтрация на изображения")
        self.root.geometry("1200x800")
        
        self.original_image = None
        self.filtered_image = None
        self.photo_original = None
        self.photo_filtered = None
        
        # Инициализация на филтърните параметри
        self.kernel = np.zeros((5, 5), dtype=int)
        self.scale = tk.IntVar(value=1)
        self.offset = tk.IntVar(value=0)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основен контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация на grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Ляв панел - контроли
        control_frame = ttk.LabelFrame(main_frame, text="Контроли", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.N, tk.S, tk.W), padx=5)
        
        # Бутон за зареждане на изображение
        ttk.Button(control_frame, text="Зареди изображение", 
                   command=self.load_image).grid(row=0, column=0, columnspan=5, pady=5, sticky=(tk.W, tk.E))
        
        # Предефинирани филтри
        ttk.Label(control_frame, text="Предефинирани филтри:").grid(row=1, column=0, columnspan=5, pady=(10,5))
        
        presets = [
            ("Identity", self.preset_identity),
            ("Blur", self.preset_blur),
            ("Sharpen", self.preset_sharpen),
            ("Edge Detect", self.preset_edge),
            ("Emboss", self.preset_emboss),
            ("Gaussian", self.preset_gaussian)
        ]
        
        for i, (name, command) in enumerate(presets):
            row = 2 + i // 2
            col = i % 2
            ttk.Button(control_frame, text=name, command=command, width=12).grid(
                row=row, column=col*2, columnspan=2, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        # Таблица с тегла 5x5
        ttk.Label(control_frame, text="Филтърно ядро (5x5):").grid(
            row=5, column=0, columnspan=5, pady=(15,5))
        ttk.Label(control_frame, text="(Жълто = текущ пиксел)", 
                  font=('Arial', 8)).grid(row=6, column=0, columnspan=5)
        
        self.kernel_entries = []
        for i in range(5):
            row_entries = []
            for j in range(5):
                entry = ttk.Entry(control_frame, width=5, justify='center')
                entry.grid(row=7+i, column=j, padx=2, pady=2)
                entry.insert(0, "0")
                
                # Маркиране на централния елемент
                if i == 2 and j == 2:
                    entry.configure(style='Central.TEntry')
                
                row_entries.append(entry)
            self.kernel_entries.append(row_entries)
        
        # Scale и Offset
        ttk.Label(control_frame, text="Scale:").grid(row=12, column=0, pady=(15,5), sticky=tk.W)
        scale_entry = ttk.Entry(control_frame, textvariable=self.scale, width=10)
        scale_entry.grid(row=12, column=1, columnspan=2, pady=(15,5), sticky=tk.W)
        
        ttk.Label(control_frame, text="Offset:").grid(row=13, column=0, pady=5, sticky=tk.W)
        offset_entry = ttk.Entry(control_frame, textvariable=self.offset, width=10)
        offset_entry.grid(row=13, column=1, columnspan=2, pady=5, sticky=tk.W)
        
        # Бутони за действия
        ttk.Button(control_frame, text="Приложи филтър", 
                   command=self.apply_filter).grid(row=14, column=0, columnspan=5, pady=(15,5), sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Нулирай", 
                   command=self.reset_filter).grid(row=15, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Запази резултат", 
                   command=self.save_image).grid(row=15, column=3, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Десен панел - изображения
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        image_frame.rowconfigure(1, weight=1)
        
        # Оригинално изображение
        original_frame = ttk.LabelFrame(image_frame, text="Оригинално изображение", padding="5")
        original_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), pady=(0,5))
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(0, weight=1)
        
        self.original_canvas = tk.Canvas(original_frame, bg='gray', width=600, height=350)
        self.original_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Филтрирано изображение
        filtered_frame = ttk.LabelFrame(image_frame, text="Филтрирано изображение", padding="5")
        filtered_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        filtered_frame.columnconfigure(0, weight=1)
        filtered_frame.rowconfigure(0, weight=1)
        
        self.filtered_canvas = tk.Canvas(filtered_frame, bg='gray', width=600, height=350)
        self.filtered_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
    def load_image(self):
        filepath = filedialog.askopenfilename(
            title="Изберете изображение",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.original_image = Image.open(filepath).convert('RGB')
                self.display_image(self.original_image, self.original_canvas, 'original')
                self.filtered_image = None
                self.filtered_canvas.delete("all")
            except Exception as e:
                messagebox.showerror("Грешка", f"Не може да се зареди изображението: {str(e)}")
    
    def display_image(self, image, canvas, img_type):
        # Мащабиране на изображението да пасва в canvas
        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 600
        canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 350
        
        img_copy = image.copy()
        img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        
        if img_type == 'original':
            self.photo_original = photo
        else:
            self.photo_filtered = photo
        
        canvas.delete("all")
        canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor=tk.CENTER)
    
    def get_kernel_values(self):
        kernel = np.zeros((5, 5), dtype=int)
        try:
            for i in range(5):
                for j in range(5):
                    value = self.kernel_entries[i][j].get()
                    kernel[i][j] = int(value) if value else 0
            return kernel
        except ValueError:
            messagebox.showerror("Грешка", "Всички стойности в ядрото трябва да са цели числа!")
            return None
    
    def set_kernel_values(self, kernel):
        for i in range(5):
            for j in range(5):
                self.kernel_entries[i][j].delete(0, tk.END)
                self.kernel_entries[i][j].insert(0, str(kernel[i][j]))
    
    def apply_filter(self):
        if self.original_image is None:
            messagebox.showwarning("Внимание", "Моля, заредете изображение първо!")
            return
        
        kernel = self.get_kernel_values()
        if kernel is None:
            return
        
        try:
            scale = self.scale.get()
            if scale == 0:
                messagebox.showerror("Грешка", "Scale не може да бъде 0!")
                return
            offset = self.offset.get()
        except:
            messagebox.showerror("Грешка", "Scale и Offset трябва да са цели числа!")
            return
        
        # Прилагане на филтъра
        self.filtered_image = self.linear_filter(self.original_image, kernel, scale, offset)
        self.display_image(self.filtered_image, self.filtered_canvas, 'filtered')
        
    def linear_filter(self, image, kernel, scale, offset):
        # Конвертиране на изображението в numpy масив
        img_array = np.array(image, dtype=np.float32)
        height, width, channels = img_array.shape
        
        # Падиране на изображението за обработка на ръбовете
        padded = np.pad(img_array, ((2, 2), (2, 2), (0, 0)), mode='edge')
        
        # Създаване на изходен масив
        output = np.zeros_like(img_array)
        
        # Прилагане на конволюция с оптимизирани NumPy операции
        for ky in range(5):
            for kx in range(5):
                # Извличане на съответната част от изображението
                shifted = padded[ky:ky+height, kx:kx+width, :]
                # Умножаване по съответното тегло от ядрото
                output += shifted * kernel[ky, kx]
        
        # Прилагане на scale и offset
        output = output / scale + offset
        output = np.clip(output, 0, 255)
        
        # Конвертиране обратно в изображение
        return Image.fromarray(output.astype(np.uint8))
    
    def save_image(self):
        if self.filtered_image is None:
            messagebox.showwarning("Внимание", "Няма филтрирано изображение за запазване!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.filtered_image.save(filepath)
                messagebox.showinfo("Успех", "Изображението е запазено успешно!")
            except Exception as e:
                messagebox.showerror("Грешка", f"Не може да се запази изображението: {str(e)}")
    
    def reset_filter(self):
        for i in range(5):
            for j in range(5):
                self.kernel_entries[i][j].delete(0, tk.END)
                self.kernel_entries[i][j].insert(0, "0")
        self.scale.set(1)
        self.offset.set(0)
    
    # Предефинирани филтри
    def preset_identity(self):
        kernel = np.zeros((5, 5), dtype=int)
        kernel[2, 2] = 1
        self.set_kernel_values(kernel)
        self.scale.set(1)
        self.offset.set(0)
    
    def preset_blur(self):
        kernel = np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0]
        ])
        self.set_kernel_values(kernel)
        self.scale.set(9)
        self.offset.set(0)
    
    def preset_sharpen(self):
        kernel = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, -1, 0, 0],
            [0, -1, 5, -1, 0],
            [0, 0, -1, 0, 0],
            [0, 0, 0, 0, 0]
        ])
        self.set_kernel_values(kernel)
        self.scale.set(1)
        self.offset.set(0)
    
    def preset_edge(self):
        kernel = np.array([
            [0, 0, 0, 0, 0],
            [0, -1, -1, -1, 0],
            [0, -1, 8, -1, 0],
            [0, -1, -1, -1, 0],
            [0, 0, 0, 0, 0]
        ])
        self.set_kernel_values(kernel)
        self.scale.set(1)
        self.offset.set(0)
    
    def preset_emboss(self):
        kernel = np.array([
            [0, 0, 0, 0, 0],
            [0, -2, -1, 0, 0],
            [0, -1, 1, 1, 0],
            [0, 0, 1, 2, 0],
            [0, 0, 0, 0, 0]
        ])
        self.set_kernel_values(kernel)
        self.scale.set(1)
        self.offset.set(128)
    
    def preset_gaussian(self):
        kernel = np.array([
            [0, 0, 1, 0, 0],
            [0, 1, 2, 1, 0],
            [1, 2, 4, 2, 1],
            [0, 1, 2, 1, 0],
            [0, 0, 1, 0, 0]
        ])
        self.set_kernel_values(kernel)
        self.scale.set(16)
        self.offset.set(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = LinearFilterApp(root)
    root.mainloop()