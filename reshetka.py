import random
import string
import tkinter as tk
from tkinter import simpledialog, messagebox


class AlphabetManager:
    """
    Класс для управления алфавитом и выбора подходящего набора символов (латиница или кириллица).
    """
    def __init__(self):
        """Инициализация класса. Создание атрибута для хранения алфавита."""
        self.alphabet = None

    def detect_alphabet(self, text):
        """
        Определяет тип алфавита в заданном тексте.

        Параметры:
        text (str): Входной текст для анализа.

        Возвращает:
        str: Тип алфавита ('cyrillic', 'latin', 'mixed' или 'unknown').
        """
        has_cyrillic = any('А' <= char <= 'Я' or 'а' <= char <= 'я' for char in text)
        has_latin = any('A' <= char <= 'Z' or 'a' <= char <= 'z' for char in text)

        if has_cyrillic and has_latin:
            return 'mixed'
        elif has_cyrillic:
            return 'cyrillic'
        elif has_latin:
            return 'latin'
        return 'unknown'

    def choose_alphabet(self, parent, text):
        """
        Выбирает алфавит на основе текста или позволяет пользователю выбрать, если алфавиты смешаны.

        Параметры:
        parent (tk.Tk): Родительское окно для диалога.
        text (str): Текст для анализа.
        """
        alphabet_type = self.detect_alphabet(text)

        if alphabet_type == 'cyrillic':
            self.alphabet = list('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        elif alphabet_type == 'latin':
            self.alphabet = list(string.ascii_letters)
        elif alphabet_type == 'mixed':
            result = AlphabetSelectionDialog(parent).show()
            if result == 'latin':
                self.alphabet = list(string.ascii_letters)
            else:
                self.alphabet = list('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        else:
            self.alphabet = list(string.digits + string.punctuation)

    def get_alphabet(self):
        """Возвращает текущий алфавит."""
        return self.alphabet


class AlphabetSelectionDialog(tk.Toplevel):
    """
    Диалоговое окно для выбора алфавита (латиница или кириллица).
    """
    def __init__(self, parent):
        """Инициализация диалога. Создание кнопок выбора алфавита."""
        super().__init__(parent)
        self.result = None
        self.title("Choose Alphabet")
        self.geometry("250x100")

        label = tk.Label(self, text="Please choose the alphabet:")
        label.pack(pady=10)

        latin_button = tk.Button(self, text="Latin", command=self.choose_latin)
        latin_button.pack(side=tk.LEFT, padx=10)

        cyrillic_button = tk.Button(self, text="Cyrillic", command=self.choose_cyrillic)
        cyrillic_button.pack(side=tk.RIGHT, padx=10)

    def choose_latin(self):
        """Выбирает латинский алфавит."""
        self.result = 'latin'
        self.destroy()

    def choose_cyrillic(self):
        """Выбирает кириллический алфавит."""
        self.result = 'cyrillic'
        self.destroy()

    def show(self):
        """Отображает диалоговое окно и ожидает выбора пользователя."""
        self.grab_set()
        self.wait_window()
        return self.result


class GridCipherApp:
    """
    Приложение для реализации шифра на основе поворачивающейся решетки.
    """
    def __init__(self, master):
        """Инициализация основного окна и создание элементов интерфейса."""
        self.encrypted_canvases = None
        self.output_text = None
        self.input_text = None
        self.encrypted_scroll = None
        self.encrypted_canvas_frame = None
        self.canvas = None
        self.encrypted_canvases_frame = None
        self.alphabet_manager = AlphabetManager()
        self.master = master
        self.master.title("Turning Grid Cipher")

        self.grid_rows = 20  # По умолчанию 20x20
        self.grid_cols = 20
        self.cell_size = 35
        self.cells = {}
        self.holes = []
        self.max_length = 0
        self.step_grid = None
        self.current_holes = []
        self.create_ui()

    def create_ui(self):
        """
        Создает пользовательский интерфейс приложения с полями ввода, кнопками и сеткой.
        """
        # Frame для шифруемой решетки (левая часть)
        grid_frame = tk.Frame(self.master)
        grid_frame.pack(side=tk.LEFT, padx=18, pady=18)

        self.canvas = tk.Canvas(grid_frame, width=self.grid_cols * self.cell_size,
                                height=self.grid_rows * self.cell_size)
        self.canvas.pack()

        # Frame для отображения зашифрованных решеток (с прокруткой справа от шифровальной решетки)
        encrypted_grid_frame = tk.Frame(self.master)
        encrypted_grid_frame.pack(side=tk.LEFT, padx=18, pady=18)

        # Добавляем скроллинг
        self.encrypted_scroll = tk.Scrollbar(encrypted_grid_frame, orient=tk.VERTICAL)
        self.encrypted_canvas_frame = tk.Canvas(encrypted_grid_frame, width=self.grid_cols * self.cell_size + 20,
                                                height=self.grid_rows * self.cell_size + 20,
                                                yscrollcommand=self.encrypted_scroll.set)

        self.encrypted_scroll.config(command=self.encrypted_canvas_frame.yview)
        self.encrypted_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.encrypted_canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.encrypted_canvases_frame = tk.Frame(self.encrypted_canvas_frame)
        self.encrypted_canvas_frame.create_window((0, 0), window=self.encrypted_canvases_frame, anchor='nw')

        # Frame для элементов управления (правая часть)
        controls_frame = tk.Frame(self.master)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.Y)

        # Поле для шифруемого текста с прокруткой
        tk.Label(controls_frame, text="Text to encrypt:").pack(anchor=tk.W)
        input_text_frame = tk.Frame(controls_frame)
        input_text_frame.pack()

        input_text_scroll = tk.Scrollbar(input_text_frame, orient=tk.VERTICAL)
        self.input_text = tk.Text(input_text_frame, height=5, width=30, yscrollcommand=input_text_scroll.set)
        input_text_scroll.config(command=self.input_text.yview)
        input_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH)

        # Кнопки управления
        tk.Button(controls_frame, text="Set grid size", command=self.set_grid_size).pack(anchor=tk.W, pady=5)
        tk.Button(controls_frame, text="Generate random grid", command=self.generate_random_grid).pack(anchor=tk.W,
                                                                                                       pady=5)
        tk.Button(controls_frame, text="Clear selected cells", command=self.clear_holes).pack(anchor=tk.W, pady=5)
        tk.Button(controls_frame, text="Encrypt text", command=self.encrypt_text).pack(anchor=tk.W, pady=5)
        tk.Button(controls_frame, text="Decrypt text", command=self.decrypt_text).pack(anchor=tk.W,
                                                                                       pady=5)

        # Поле для зашифрованного текста с прокруткой
        tk.Label(controls_frame, text="Encrypted text:").pack(anchor=tk.W, pady=10)
        output_text_frame = tk.Frame(controls_frame)
        output_text_frame.pack()

        output_text_scroll = tk.Scrollbar(output_text_frame, orient=tk.VERTICAL)
        self.output_text = tk.Text(output_text_frame, height=5, width=30, yscrollcommand=output_text_scroll.set)
        output_text_scroll.config(command=self.output_text.yview)
        output_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH)

        # Добавляем поле для расшифрованного текста с прокруткой
        tk.Label(controls_frame, text="Decrypted text:").pack(anchor=tk.W, pady=10)
        decrypted_text_frame = tk.Frame(controls_frame)
        decrypted_text_frame.pack()

        decrypted_text_scroll = tk.Scrollbar(decrypted_text_frame, orient=tk.VERTICAL)
        self.decrypted_text = tk.Text(decrypted_text_frame, height=5, width=30,
                                      yscrollcommand=decrypted_text_scroll.set)
        decrypted_text_scroll.config(command=self.decrypted_text.yview)
        decrypted_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.decrypted_text.pack(side=tk.LEFT, fill=tk.BOTH)

        self.create_grid()

    def set_grid_size(self):
        """
        Устанавливает размер сетки на основе ввода пользователя. Проверяет ввод на корректность.
        """
        self.current_holes.clear()
        self.holes.clear()
        while True:
            rows = simpledialog.askinteger("Input", "Enter number of rows (2-20):", parent=self.master)
            if rows is None:  # Пользователь закрыл окно
                return
            if rows < 2 or rows > 20:
                messagebox.showerror("Error", "Rows must be between 2 and 20.")
                continue  # Повторяем запрос, если введены неправильные данные
            cols = simpledialog.askinteger("Input", "Enter number of columns (2-20):", parent=self.master)
            if cols is None:  # Пользователь закрыл окно
                return
            if cols < 2 or cols > 20:
                messagebox.showerror("Error", "Columns must be between 2 and 20.")
                continue  # Повторяем запрос, если введены неправильные данные
            self.grid_rows = rows
            self.grid_cols = cols
            self.create_grid()
            break  # Если ввод корректен, выходим из цикла

    def generate_random_grid(self):
        """
        Генерирует случайную сетку с заданными параметрами и случайными дырками (отверстиями).
        Учитывает наложения дырок при повороте, отражении и повороте после отражения.
        """
        self.current_holes.clear()

        while True:
            rows = simpledialog.askinteger("Input", "Enter number of rows (2-20):", parent=self.master)
            if rows is None:  # Пользователь закрыл окно
                return
            if rows < 2 or rows > 20:  # Проверка минимального и максимального значения
                messagebox.showerror("Error", "Rows must be between 2 and 20.")
                continue
            cols = simpledialog.askinteger("Input", "Enter number of columns (2-20):", parent=self.master)
            if cols is None:  # Пользователь закрыл окно
                return
            if cols < 2 or cols > 20:  # Проверка минимального и максимального значения
                messagebox.showerror("Error", "Columns must be between 2 and 20.")
                continue
            self.grid_rows = rows
            self.grid_cols = cols
            break

        # Создаем решетку с случайными дырками
        self.holes = []
        total_cells = self.grid_rows * self.grid_cols
        if self.grid_rows % 2 != 0 or self.grid_cols % 2 != 0:
            num_holes = max(1, min((total_cells/1.5) // 4, total_cells - 1))
        else:
            num_holes = max(1, min(total_cells // 4, total_cells - 1))

        while len(self.holes) < num_holes:
            row = random.randint(0, self.grid_rows - 1)
            col = random.randint(0, self.grid_cols - 1)
            # Проверяем, нет ли наложений при поворотах и отражениях
            if (row, col) not in self.holes and not self.check_overlap(row, col):
                self.holes.append((row, col))

        self.holes.sort(key=lambda x: (x[0], x[1]))  # Сортируем дырки построчно, слева направо
        self.create_grid()

    def create_grid(self):
        """
        Создает сетку на основе текущих параметров (размеры и дырки).
        """
        self.canvas.delete("all")
        self.cells = {}

        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cell_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")
                self.cells[(i, j)] = cell_id
                self.canvas.tag_bind(cell_id, "<Button-1>", lambda event, row=i, col=j: self.toggle_hole(row, col))

        # Отображаем дырки, если они есть
        for hole in self.holes:
            row, col = hole
            self.canvas.itemconfig(self.cells[(row, col)], fill="black")

    def toggle_hole(self, row, col):
        """
        Добавляет или удаляет дырку в указанной ячейке. Проверяет на наличие перекрытий после поворота.

        Параметры:
        row (int): Строка ячейки.
        col (int): Колонка ячейки.
        """
        cell_id = self.cells[(row, col)]
        current_color = self.canvas.itemcget(cell_id, "fill")
        new_color = "black" if current_color == "white" else "white"
        self.canvas.itemconfig(cell_id, fill=new_color)

        if new_color == "black":
            if self.check_overlap(row, col):
                self.canvas.itemconfig(cell_id, fill="white")  # Возвращаем цвет в белый
                messagebox.showerror("Error", "This hole overlaps with another after rotation!")
                return
            self.holes.append((row, col))
            self.holes.sort(key=lambda x: (x[0], x[1]))
        else:
            self.holes.remove((row, col))

        print(self.holes)

    def clear_holes(self):
        """Очищает выбранные дырки из сетки."""
        for hole in self.holes:
            row, col = hole
            self.canvas.itemconfig(self.cells[(row, col)], fill="white")
        self.holes.clear()
        self.current_holes.clear()
        print("Cleared holes:", self.holes)

    def check_overlap(self, r, c):
        """
        Проверяет, будет ли добавленная дырка перекрываться с существующими
        дырками на любом этапе поворота или отражения решетки.

        Параметры:
        row (int): Строка новой ячейки (дырки).
        col (int): Колонка новой ячейки (дырки).

        Возвращает:
        bool: True, если новая дырка перекрывается с существующими.
        """
        # Список для координат новой дырки
        new_hole = (r, c)

        # Создаем копию текущего списка дырок
        #current_holes = self.holes[:]
        print(new_hole)
        print("current holes", self.current_holes)
        new_r_rotate, new_c_rotate = self.grid_rows - 1 - r, self.grid_cols - 1 - c
        if (new_r_rotate, new_c_rotate) not in self.current_holes:
            self.current_holes.append((new_r_rotate, new_c_rotate))
        new_r_reflect, new_c_reflect = r, self.grid_cols - 1 - c
        if (new_r_reflect, new_c_reflect) not in self.current_holes:
            self.current_holes.append((new_r_reflect, new_c_reflect))
        new_r_reflect_rotate, new_c_reflect_rotate = self.grid_rows - 1 - r, c
        if (new_r_reflect_rotate, new_c_reflect_rotate) not in self.current_holes:
            self.current_holes.append((new_r_reflect_rotate, new_c_reflect_rotate))
        if (r, c) in self.current_holes:
            print("наложение")
            return True
        return False


    def decrypt_text(self):
        """
        Дешифрует текст, введенный пользователем, используя текущую решетку и алфавит.
        """
        encrypted_text = self.output_text.get("1.0", tk.END).strip()
        if not encrypted_text:
            messagebox.showerror("Error", "No encrypted text to decrypt!")
            return

        original_message_length = len(self.input_text.get("1.0", tk.END).strip())
        if original_message_length == 0:
            messagebox.showerror("Error", "No original message length available for decryption!")
            return



        self.max_length = len(self.holes) * 4  # для 4-х поворотов

        # Разделение текста на подстроки для дешифрования
        substrings = [encrypted_text[i:i + self.grid_rows * self.grid_cols] for i in
                      range(0, len(encrypted_text), self.grid_rows * self.grid_cols)]


        self.encrypted_canvases = []  # Список для холстов каждой дешифрованной решетки

        # Дешифруем каждую подстроку отдельно
        all_decrypted_text = ''
        for substring in substrings:
            grid, decrypted_text = self.decrypt_substring(substring, original_message_length)
            all_decrypted_text += decrypted_text

        self.decrypted_text.delete("1.0", tk.END)
        self.decrypted_text.insert("1.0", all_decrypted_text[:original_message_length])  # Ограничиваем длину

    def decrypt_substring(self, substring, original_message_length):
        """
        Дешифрует подстроку текста и возвращает решетку и расшифрованный текст.

        Параметры:
        substring (str): Подстрока для дешифрования.
        alphabet (list): Алфавит для случайных символов.
        original_message_length (int): Длина исходного сообщения.

        Возвращает:
        list, str: Сетка с дешифрованными символами и расшифрованный текст.
        """
        grid = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        index = 0

        # Заполнение сетки зашифрованными символами
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if index < len(substring):
                    grid[row][col] = substring[index]
                    index += 1

        decrypted_chars = []

        # Дешифрование в обратном порядке шифрования
        for step in range(2):
            for hole in self.holes:
                row, col = hole
                if grid[row][col] is not None:
                    decrypted_chars.append(grid[row][col])
                    grid[row][col] = None
                    if len(decrypted_chars) >= original_message_length:
                        return grid, ''.join(decrypted_chars)  # Прерываем, если собрали достаточно символов

            # Поворот решетки в обратном направлении
            self.rotate_grid()

        # Выполняем обратное отражение по оси X
        for step in range(2):
            for hole in self.holes:
                row, col = hole
                if grid[row][col] is not None:
                    decrypted_chars.append(grid[row][col])
                    grid[row][col] = None
                    if len(decrypted_chars) >= original_message_length:
                        return grid, ''.join(decrypted_chars)  # Прерываем, если собрали достаточно символов
            self.reflect_grid_on_x()

        # Возвращаем повороты и отражения решетки в обратном направлении
        for step in range(2):
            for hole in self.holes:
                row, col = hole
                if grid[row][col] is not None:
                    decrypted_chars.append(grid[row][col])
                    grid[row][col] = None
                    if len(decrypted_chars) >= original_message_length:
                        return grid, ''.join(decrypted_chars)  # Прерываем, если собрали достаточно символов
            self.rotate_reflected_grid()

        decrypted_text = ''.join(decrypted_chars)
        return grid, decrypted_text

    def encrypt_text(self):
        """
        Шифрует текст, вводимый пользователем, используя выбранный алфавит и текущую решетку.
        """
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "No encrypted text to decrypt!")
            return
        if not self.holes:
            messagebox.showerror("Error", "The grid is empty. No holes selected!")
            return

        # Выбор алфавита для шифрования
        self.alphabet_manager.choose_alphabet(self.master, text)
        alphabet = self.alphabet_manager.get_alphabet()

        self.max_length = len(self.holes) * 4  # для 4-х поворотов

        # Разделение текста на подстроки
        substrings = [text[i:i + self.max_length] for i in range(0, len(text), self.max_length)]

        if len(substrings) > 1:
            messagebox.showinfo("Information", f"Text is too long. It will be divided into {len(substrings)} grids.")

        # Удаляем старые решетки перед отображением новых
        for canvas in self.encrypted_canvases_frame.winfo_children():
            canvas.destroy()

        self.encrypted_canvases = []  # Список для холстов каждой зашифрованной решетки

        # Зашифровываем каждую подстроку отдельно
        all_encrypted_text = ''
        for substring in substrings:
            grid, encrypted_text = self.encrypt_substring(substring, alphabet)
            self.visualize_encrypted_grid(grid)
            all_encrypted_text += encrypted_text

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", all_encrypted_text)

        # Обновляем высоту холста после создания всех решеток
        self.encrypted_canvas_frame.update_idletasks()  # Обновляем состояние виджетов

        # Задаем область прокрутки (scrollregion) для холста, чтобы она охватывала все созданные зашифрованные решетки
        self.encrypted_canvas_frame.config(scrollregion=self.encrypted_canvas_frame.bbox("all"))



    def encrypt_substring(self, substring, alphabet):
        """
        Шифрует подстроку текста и возвращает зашифрованную сетку и текст.

        Параметры:
        substring (str): Подстрока для шифрования.
        alphabet (list): Алфавит для случайных символов.

        Возвращает:
        list, str: Сетка с зашифрованными символами и зашифрованный текст.
        """
        grid = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        index = 0

        for hole in self.holes:
            if index < len(substring):
                row, col = hole
                if grid[row][col] is None:
                    grid[row][col] = substring[index]
                    index += 1

        for step in range(2):
            self.rotate_grid()
            for hole in self.holes:
                if index < len(substring):
                    row, col = hole
                    if grid[row][col] is None:
                        grid[row][col] = substring[index]
                        index += 1

        for step in range(2):
            self.reflect_grid_on_x()
            for hole in self.holes:
                if index < len(substring):
                    row, col = hole
                    if grid[row][col] is None:
                        grid[row][col] = substring[index]
                        index += 1

        for step in range(2):
            self.rotate_reflected_grid()
            for hole in self.holes:
                if index < len(substring):
                    row, col = hole
                    if grid[row][col] is None:
                        grid[row][col] = substring[index]
                        index += 1

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if grid[row][col] is None:
                    grid[row][col] = random.choice(alphabet)

        encrypted_text = ''.join([grid[row][col] for row in range(self.grid_rows)
                                  for col in range(self.grid_cols) if grid[row][col] is not None])

        return grid, encrypted_text

    def visualize_encrypted_grid(self, grid):
        """
        Визуализирует зашифрованную сетку на холсте.

        Параметры:
        grid (list): Сетка с зашифрованными символами.
        """
        # Устанавливаем размеры для холста зашифрованной решетки аналогично шифруемой
        encrypted_canvas = tk.Canvas(self.encrypted_canvases_frame, width=self.grid_cols * self.cell_size,
                                     height=self.grid_rows * self.cell_size)
        encrypted_canvas.pack(side=tk.TOP, padx=20, pady=20)
        self.encrypted_canvases.append(encrypted_canvas)  # Добавляем новый холст для отображения

        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "white"
                if grid[i][j] is not None:
                    color = "lightgreen"
                encrypted_canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                if grid[i][j] is not None:
                    encrypted_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=grid[i][j], fill="black")

    def rotate_grid(self):
        """
        Поворачивает сетку и обновляет положение дырок.
        """
        self.holes = [(self.grid_rows - 1 - row, self.grid_cols - 1 - col) for row, col in self.holes]
        new_holes = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if (row, col) in self.holes:
                    new_holes.append((row, col))
        self.holes = new_holes
        return self.holes

    def rotate_reflected_grid(self):
        """
        Отражает сетку относительно оси X и обновляет дырки.
        """
        self.holes = [(row, self.grid_cols - 1 - col) for row, col in self.holes]
        new_holes = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if (row, col) in self.holes:
                    new_holes.append((row, col))
        self.holes = new_holes
        self.holes.sort(key=lambda x: (x[0], x[1]))
        return self.holes

    def reflect_grid_on_x(self):
        self.holes = [(self.grid_rows - 1 - row, col) for row, col in self.holes]
        new_holes = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if (row, col) in self.holes:
                    new_holes.append((row, col))
        self.holes = new_holes
        return self.holes


root = tk.Tk()
app = GridCipherApp(root)
root.mainloop()
