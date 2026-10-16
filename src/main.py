from __future__ import annotations

import sqlite3
import re
import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk
from typing import Any

from core.converter import categories, convert
from core.evaluator import CalculationError, ExpressionEvaluator
from storage import DEFAULT_SETTINGS, PortableStorage


PALETTES = {
    "dark": {
        "bg": "#141820", "panel": "#1d232e", "panel_alt": "#252d3a",
        "text": "#f2f4f8", "muted": "#a0a9b8", "accent": "#7188ff",
        "accent_hover": "#8497ff", "operator": "#303949", "danger": "#fa777e",
        "entry": "#171c25", "border": "#303846",
    },
    "light": {
        "bg": "#f2f4f8", "panel": "#ffffff", "panel_alt": "#e8ecf4",
        "text": "#1b1e25", "muted": "#687183", "accent": "#4f6bed",
        "accent_hover": "#3f5bdd", "operator": "#e8ecf5", "danger": "#c93645",
        "entry": "#f8f9fc", "border": "#dce1eb",
    },
}


class CalculatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Arther Smart Calculator")
        self.root.minsize(360, 560)
        self.root.geometry("1000x700")
        self.storage: PortableStorage | None = None
        self.storage_warning = ""
        self.history_cache: list[tuple[int, str, str, str]] = []
        self.last_result: Decimal | None = None
        self.history_position = -1
        self.mode = "standard"
        try:
            self.storage = PortableStorage()
            self.settings = self.storage.load_settings()
            geometry = self.settings.get("window", {})
            self.root.geometry(f"{geometry.get('width', 1000)}x{geometry.get('height', 700)}")
            self.history_cache = self.storage.get_history(self.settings["history_limit"])
        except (OSError, sqlite3.Error, ValueError) as error:
            self.settings = DEFAULT_SETTINGS.copy()
            self.storage_warning = f"Penyimpanan lokal tidak tersedia: {error}. Riwayat tidak akan tersimpan."
        self.expression = tk.StringVar()
        self.preview = tk.StringVar(value="Ketik ekspresi untuk mulai")
        self.status = tk.StringVar(value=self.storage_warning or "Siap")
        self.memory = Decimal(0)
        self.memory_active = False
        self._build_shell()
        self.show_mode("standard")
        self.apply_theme()
        self._refresh_history()
        self.expression.trace_add("write", self._update_preview)
        self.root.bind("<Return>", lambda _event: self.calculate())
        self.root.bind("<KP_Enter>", lambda _event: self.calculate())
        self.root.bind("<KeyPress-equal>", self._calculate_from_key)
        self.root.bind("<Escape>", lambda _event: self.clear_entry())
        self.root.bind("<Control-BackSpace>", lambda _event: self.clear_all())
        self.root.bind("<Delete>", lambda _event: self.clear_all())
        self.root.bind("<Control-c>", lambda _event: self.copy_result())
        self.root.bind("<Control-C>", lambda _event: self.copy_result())
        self.root.bind("<Control-h>", lambda _event: self.toggle_history())
        self.root.bind("<Control-t>", lambda _event: self.toggle_theme())
        self.root.bind("<Control-1>", lambda _event: self.show_mode("standard"))
        self.root.bind("<Control-2>", lambda _event: self.show_mode("scientific"))
        self.root.bind("<Control-3>", lambda _event: self.show_mode("converter"))
        self.root.bind("<Up>", self._history_up)
        self.root.bind("<Down>", self._history_down)
        self.root.bind("<Configure>", self._resize_history)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self.input_entry.focus_set)

    def _build_shell(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.sidebar = ttk.Frame(self.root, width=160, padding=(16, 20))
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.pack_propagate(False)
        self.brand_label = ttk.Label(self.sidebar, text="ARTHER", style="Brand.TLabel")
        self.brand_label.pack(anchor="w", pady=(0, 4))
        self.brand_subtitle = ttk.Label(self.sidebar, text="SMART CALCULATOR", style="Caption.TLabel")
        self.brand_subtitle.pack(anchor="w", pady=(0, 30))
        self._compact_sidebar = False
        self.nav_buttons: dict[str, ttk.Button] = {}
        self.nav_text = {
            "standard": ("▦", "▦  Standar"),
            "scientific": ("∑", "∑  Ilmiah"),
            "converter": ("⇄", "⇄  Konverter"),
            "percent": ("%", "%  Persen"),
        }
        for key, label in (
            ("standard", "▦  Standar"),
            ("scientific", "∑  Ilmiah"),
            ("converter", "⇄  Konverter"),
            ("percent", "%  Persen"),
        ):
            button = ttk.Button(self.sidebar, text=label, style="Nav.TButton", command=lambda item=key: self.show_mode(item))
            button.pack(fill="x", pady=4)
            self.nav_buttons[key] = button
        ttk.Separator(self.sidebar).pack(fill="x", pady=20)
        self.shortcut_title = ttk.Label(self.sidebar, text="PINTASAN", style="Caption.TLabel")
        self.shortcut_title.pack(anchor="w", pady=(0, 8))
        self.shortcut_hint = ttk.Label(self.sidebar, text="Enter   Hitung\nEsc      Hapus entri\nCtrl+H   Riwayat\nCtrl+T   Tema", style="Hint.TLabel", justify="left")
        self.shortcut_hint.pack(anchor="w")
        self.main_area = ttk.Frame(self.root, padding=(22, 18, 18, 16))
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)
        topbar = ttk.Frame(self.main_area)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        topbar.columnconfigure(0, weight=1)
        ttk.Label(topbar, text="Kalkulator", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        tools = ttk.Frame(topbar)
        tools.grid(row=0, column=1, sticky="e")
        self.angle_button = ttk.Button(tools, text="DEG", style="Tool.TButton", command=self.toggle_angle)
        self.angle_button.pack(side="left", padx=4)
        self.theme_button = ttk.Button(tools, text="☼", style="Tool.TButton", command=self.toggle_theme)
        self.theme_button.pack(side="left", padx=4)
        self.format_button = ttk.Button(tools, text="1.234", style="Tool.TButton", command=self.toggle_number_format)
        self.format_button.pack(side="left", padx=4)
        self.pin_button = ttk.Button(tools, text="⌖", style="Tool.TButton", command=self.toggle_pin)
        self.pin_button.pack(side="left", padx=4)

        self.content = ttk.Frame(self.main_area)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)
        self.calculator_view = ttk.Frame(self.content)
        self.calculator_view.columnconfigure(0, weight=1)
        self.calculator_view.rowconfigure(1, weight=1)
        self.display = ttk.Frame(self.calculator_view, padding=20, style="Card.TFrame")
        self.display.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.display.columnconfigure(0, weight=1)
        memory_row = ttk.Frame(self.display, style="Card.TFrame")
        memory_row.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.memory_label = ttk.Label(memory_row, text="", style="Caption.TLabel")
        self.memory_label.pack(side="left")
        for label, action in (("MC", self.memory_clear), ("MR", self.memory_recall), ("M+", lambda: self.memory_add(1)), ("M−", lambda: self.memory_add(-1))):
            ttk.Button(memory_row, text=label, style="Mini.TButton", command=action).pack(side="right", padx=(5, 0))
        self.input_entry = ttk.Entry(self.display, textvariable=self.expression, style="Expression.TEntry", justify="right")
        self.input_entry.grid(row=1, column=0, sticky="ew", ipady=7)
        self.input_entry.bind("<Control-v>", lambda _event: self.root.after(20, self._update_preview))
        self.result_label = ttk.Label(self.display, textvariable=self.preview, style="Result.TLabel", anchor="e")
        self.result_label.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        self.keypad = ttk.Frame(self.calculator_view)
        self.keypad.grid(row=1, column=0, sticky="nsew")
        self.calculator_view.rowconfigure(1, weight=1)
        self._build_keypad()
        self.history_panel = ttk.Frame(self.root, width=280, padding=(14, 20))
        self.history_panel.grid(row=0, column=2, sticky="nsew")
        self.history_panel.grid_propagate(False)
        self.history_panel.rowconfigure(1, weight=1)
        self.history_panel.columnconfigure(0, weight=1)
        history_header = ttk.Frame(self.history_panel)
        history_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(history_header, text="Riwayat", style="Heading.TLabel").pack(side="left")
        ttk.Button(history_header, text="Bersihkan", style="Mini.TButton", command=self.clear_history).pack(side="right")
        self.history_list = tk.Listbox(self.history_panel, activestyle="none", borderwidth=0, highlightthickness=0, font=("Segoe UI", 10))
        self.history_list.grid(row=1, column=0, sticky="nsew")
        self.history_list.bind("<Double-Button-1>", self._use_selected_history)
        history_actions = ttk.Frame(self.history_panel)
        history_actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(history_actions, text="Pakai ekspresi", command=self._use_selected_history).pack(side="left", fill="x", expand=True)
        ttk.Button(history_actions, text="Salin", style="Mini.TButton", command=self._copy_selected_history).pack(side="left", padx=(6, 0))
        ttk.Button(history_actions, text="Hapus", style="Mini.TButton", command=self._delete_selected_history).pack(side="left", padx=(6, 0))
        ttk.Label(self.main_area, textvariable=self.status, style="Status.TLabel", anchor="w").grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.active_view: ttk.Frame | None = None

    def _build_keypad(self) -> None:
        for column in range(4):
            self.keypad.columnconfigure(column, weight=1, uniform="key")
        rows: list[list[tuple[str, str]]] = []
        if self.mode == "scientific":
            rows.extend([
                [("sin", "fn"), ("cos", "fn"), ("tan", "fn"), ("√", "fn")],
                [("log", "fn"), ("ln", "fn"), ("π", "fn"), ("x²", "fn")],
                [("(", "fn"), (")", "fn"), ("^", "fn"), ("!", "fn")],
            ])
        rows.extend([
            [("C", "clear"), ("CE", "clear"), ("⌫", "clear"), ("÷", "operator")],
            [("7", "number"), ("8", "number"), ("9", "number"), ("×", "operator")],
            [("4", "number"), ("5", "number"), ("6", "number"), ("−", "operator")],
            [("1", "number"), ("2", "number"), ("3", "number"), ("+", "operator")],
            [("±", "operator"), ("0", "number"), (",", "number"), ("=", "equals")],
        ])
        for row_index, row in enumerate(rows):
            self.keypad.rowconfigure(row_index, weight=1, uniform="row")
            for column, (label, kind) in enumerate(row):
                button = ttk.Button(self.keypad, text=label, style=f"Key.{kind}.TButton", command=lambda value=label: self._press(value))
                button.grid(row=row_index, column=column, sticky="nsew", padx=4, pady=4)

    def _clear_content(self) -> None:
        if self.active_view is not None:
            self.active_view.grid_forget()

    def show_mode(self, mode: str) -> None:
        self.mode = mode
        self._clear_content()
        if mode in {"standard", "scientific"}:
            self.calculator_view.grid(row=0, column=0, sticky="nsew")
            self.active_view = self.calculator_view
            for child in self.keypad.winfo_children():
                child.destroy()
            self._build_keypad()
            title = "Kalkulator ilmiah" if mode == "scientific" else "Kalkulator"
            self.root.title(f"{title} — Arther")
        elif mode == "converter":
            self.active_view = self._build_converter()
            self.active_view.grid(row=0, column=0, sticky="nsew")
        else:
            self.active_view = self._build_percent()
            self.active_view.grid(row=0, column=0, sticky="nsew")
        for key, button in self.nav_buttons.items():
            if self._compact_sidebar:
                button.configure(style="Nav.Compact.TButton")
            else:
                button.configure(style="Nav.Active.TButton" if key == mode else "Nav.TButton")

    def _build_converter(self) -> ttk.Frame:
        frame = ttk.Frame(self.content, padding=20, style="Card.TFrame")
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text="Konversi satuan", style="Heading.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 20))
        choices = categories()
        category = tk.StringVar(value="Panjang")
        amount = tk.StringVar(value="1")
        from_unit = tk.StringVar(value="km")
        to_unit = tk.StringVar(value="m")
        result = tk.StringVar(value="1000")
        category_box = ttk.Combobox(frame, textvariable=category, values=list(choices), state="readonly")
        category_box.grid(row=1, column=0, sticky="ew", pady=6)
        amount_entry = ttk.Entry(frame, textvariable=amount, style="Expression.TEntry", justify="left")
        amount_entry.grid(row=2, column=0, sticky="ew", ipady=8, pady=6)
        unit_row = ttk.Frame(frame, style="Card.TFrame")
        unit_row.grid(row=3, column=0, sticky="ew", pady=6)
        unit_row.columnconfigure(0, weight=1)
        unit_row.columnconfigure(1, weight=1)
        from_box = ttk.Combobox(unit_row, textvariable=from_unit, state="readonly")
        from_box.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(unit_row, text="⇄", command=lambda: self._swap_units(from_unit, to_unit, update)).grid(row=0, column=1, sticky="e")
        to_box = ttk.Combobox(frame, textvariable=to_unit, state="readonly")
        to_box.grid(row=4, column=0, sticky="ew", pady=6)
        ttk.Label(frame, textvariable=result, style="Result.TLabel").grid(row=5, column=0, sticky="w", pady=(20, 4))
        ttk.Label(frame, text="Hasil konversi", style="Caption.TLabel").grid(row=6, column=0, sticky="w")

        def update_units(*_args: Any) -> None:
            units = choices[category.get()]
            from_box.configure(values=units)
            to_box.configure(values=units)
            if from_unit.get() not in units:
                from_unit.set(units[0])
            if to_unit.get() not in units:
                to_unit.set(units[1] if len(units) > 1 else units[0])
            update()

        def update(*_args: Any) -> None:
            try:
                value = Decimal(amount.get().replace(",", "."))
                converted = convert(value, category.get(), from_unit.get(), to_unit.get())
                result.set(f"{self._format_number(converted)} {to_unit.get()}")
                self.status.set("Konversi diperbarui")
            except (InvalidOperation, ValueError) as error:
                result.set("Periksa nilai dan satuan")
                self.status.set(str(error))

        category_box.bind("<<ComboboxSelected>>", update_units)
        for variable in (amount, from_unit, to_unit):
            variable.trace_add("write", update)
        update_units()
        return frame

    @staticmethod
    def _swap_units(left: tk.StringVar, right: tk.StringVar, update: Any) -> None:
        left_value, right_value = left.get(), right.get()
        left.set(right_value)
        right.set(left_value)
        update()

    def _build_percent(self) -> ttk.Frame:
        frame = ttk.Frame(self.content, padding=20, style="Card.TFrame")
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text="Diskon & pajak", style="Heading.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 20))
        price = tk.StringVar(value="100000")
        discount = tk.StringVar(value="10")
        tax = tk.StringVar(value="11")
        values: dict[str, tk.StringVar] = {}
        for index, (label, variable) in enumerate((("Harga awal", price), ("Diskon (%)", discount), ("Pajak / PPN (%)", tax)), 1):
            ttk.Label(frame, text=label, style="Caption.TLabel").grid(row=index * 2 - 1, column=0, sticky="w")
            entry = ttk.Entry(frame, textvariable=variable, justify="left")
            entry.grid(row=index * 2, column=0, sticky="ew", ipady=7, pady=(4, 12))
        for index, label in enumerate(("Nilai diskon", "Nilai pajak", "Harga akhir")):
            values[label] = tk.StringVar(value="—")
            ttk.Label(frame, text=label, style="Caption.TLabel").grid(row=7 + index * 2, column=0, sticky="w", pady=(8, 0))
            ttk.Label(frame, textvariable=values[label], style="Result.TLabel").grid(row=8 + index * 2, column=0, sticky="w")

        def update(*_args: Any) -> None:
            try:
                base, discount_rate, tax_rate = (Decimal(item.get().replace(",", ".")) for item in (price, discount, tax))
                discount_amount = base * discount_rate / 100
                taxable = base - discount_amount
                tax_amount = taxable * tax_rate / 100
                values["Nilai diskon"].set(self._format_number(discount_amount))
                values["Nilai pajak"].set(self._format_number(tax_amount))
                values["Harga akhir"].set(self._format_number(taxable + tax_amount))
                self.status.set("Perhitungan diperbarui")
            except (InvalidOperation, ArithmeticError):
                for variable in values.values():
                    variable.set("Periksa nilai yang dimasukkan")
        for variable in (price, discount, tax):
            variable.trace_add("write", update)
        update()
        return frame

    def _press(self, value: str) -> None:
        if value == "=":
            self.calculate()
        elif value == "C":
            self.clear_all()
        elif value == "CE":
            self.clear_entry()
        elif value == "⌫":
            self.expression.set(self.expression.get()[:-1])
        elif value == "±":
            text = self.expression.get()
            if text:
                self.expression.set(f"-({text})")
        elif value in {"sin", "cos", "tan", "sqrt", "√", "log", "ln"}:
            shown = "sqrt" if value == "√" else value
            self.expression.set(self.expression.get() + shown + "(")
        elif value == "x²":
            self.expression.set(self.expression.get() + "^2")
        else:
            self.expression.set(self.expression.get() + value)
        self.input_entry.focus_set()
        self.input_entry.icursor("end")

    def _evaluator(self) -> ExpressionEvaluator:
        return ExpressionEvaluator(self.settings.get("angle_unit", "deg"), self.settings.get("number_format", "id"))

    def _update_preview(self, *_args: Any) -> None:
        expression = self.expression.get()
        if not expression.strip():
            self.preview.set("Ketik ekspresi untuk mulai")
            self.result_label.configure(style="Result.TLabel")
            return
        try:
            result = self._evaluator().evaluate(expression, self.last_result or 0)
            self.preview.set("= " + self._format_number(result))
            self.result_label.configure(style="Result.TLabel")
        except CalculationError as error:
            self.preview.set(str(error) if "nol" in str(error).lower() else "…")
            self.result_label.configure(style="Result.Error.TLabel" if "nol" in str(error).lower() else "Result.TLabel")

    def calculate(self) -> None:
        expression = self.expression.get().strip()
        if not expression:
            return
        try:
            result = self._evaluator().evaluate(expression, self.last_result or 0)
        except CalculationError as error:
            self.preview.set(str(error))
            self.result_label.configure(style="Result.Error.TLabel")
            self.status.set("Ekspresi belum dapat dihitung")
            return
        self.last_result = result
        self.preview.set("= " + self._format_number(result))
        self.result_label.configure(style="Result.TLabel")
        self.status.set("Hasil dihitung")
        try:
            if self.storage:
                self.storage.add_history(expression, str(result), self.mode, self.settings["history_limit"])
                self.history_cache = self.storage.get_history(self.settings["history_limit"])
                self._refresh_history()
        except sqlite3.Error as error:
            self.status.set(f"Hasil dihitung, riwayat gagal disimpan: {error}")

    def _calculate_from_key(self, _event: tk.Event) -> str:
        self.calculate()
        return "break"

    def _format_number(self, value: Decimal) -> str:
        if not value.is_finite():
            return str(value)
        normalized = value.normalize()
        if normalized and (abs(normalized.adjusted()) > 14 or abs(normalized.adjusted()) < -8):
            return f"{normalized:.8E}".replace(".", "," if self.settings.get("number_format") == "id" else ".")
        places = self.settings.get("decimal_places", 10)
        text = f"{value:.{places}f}".rstrip("0").rstrip(".") if "." in f"{value:.{places}f}" else f"{value:.{places}f}"
        if self.settings.get("number_format") == "id":
            integer, separator, fraction = text.partition(".")
            sign = ""
            if integer.startswith("-"):
                sign, integer = "-", integer[1:]
            grouped = f"{int(integer):,}".replace(",", ".") if integer else "0"
            return sign + grouped + ("," + fraction if separator else "")
        integer, separator, fraction = text.partition(".")
        try:
            grouped = f"{int(integer):,}"
        except ValueError:
            grouped = integer
        return grouped + (("." + fraction) if separator else "")

    def _refresh_history(self) -> None:
        if not hasattr(self, "history_list"):
            return
        palette = PALETTES[self.settings.get("theme", "dark")]
        self.history_list.configure(bg=palette["panel"], fg=palette["text"], selectbackground=palette["accent"], selectforeground="#ffffff")
        self.history_list.delete(0, tk.END)
        for _item_id, expression, result, _mode in self.history_cache:
            self.history_list.insert(tk.END, f"{expression}\n= {result}")

    def _selected_history(self) -> tuple[int, str, str, str] | None:
        selection = self.history_list.curselection()
        return self.history_cache[selection[0]] if selection and selection[0] < len(self.history_cache) else None

    def _use_selected_history(self, _event: tk.Event | None = None) -> None:
        item = self._selected_history()
        if item:
            self.show_mode("standard")
            self.expression.set(item[1])
            self.input_entry.focus_set()

    def _delete_selected_history(self) -> None:
        item = self._selected_history()
        if not item:
            return
        try:
            if self.storage:
                self.storage.delete_history_item(item[0])
            self.history_cache = [record for record in self.history_cache if record[0] != item[0]]
            self._refresh_history()
            self.status.set("Perhitungan dihapus dari riwayat")
        except sqlite3.Error as error:
            self.status.set(f"Gagal menghapus riwayat: {error}")

    def _copy_selected_history(self) -> None:
        item = self._selected_history()
        if item:
            self._copy(item[2])
            self.status.set("Hasil riwayat disalin")

    def _history_up(self, _event: tk.Event) -> None:
        if not self.history_cache:
            return
        self.history_position = min(self.history_position + 1, len(self.history_cache) - 1)
        self.expression.set(self.history_cache[self.history_position][1])

    def _history_down(self, _event: tk.Event) -> None:
        if self.history_position > 0:
            self.history_position -= 1
            self.expression.set(self.history_cache[self.history_position][1])
        elif self.history_position == 0:
            self.history_position = -1
            self.expression.set("")

    def clear_history(self) -> None:
        if not self.history_cache:
            return
        if messagebox.askyesno("Hapus riwayat", "Hapus seluruh riwayat perhitungan?"):
            try:
                if self.storage:
                    self.storage.clear_history()
                self.history_cache.clear()
                self._refresh_history()
                self.status.set("Riwayat dihapus")
            except sqlite3.Error as error:
                self.status.set(f"Gagal menghapus riwayat: {error}")

    def clear_all(self) -> None:
        self.expression.set("")
        self.status.set("Input dibersihkan")

    def clear_entry(self) -> None:
        text = self.expression.get()
        if text.endswith(")"):
            text = text[:-1]
        match = re.search(r"[A-Za-z0-9.,]+$", text)
        if match:
            text = text[:match.start()]
        self.expression.set(text)

    def copy_result(self, _event: tk.Event | None = None) -> None:
        if self.last_result is not None:
            self._copy(self._format_number(self.last_result))
            self.status.set("Hasil disalin")
        elif self.expression.get():
            self._copy(self.expression.get())
            self.status.set("Ekspresi disalin")

    def _copy(self, value: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(value)

    def memory_clear(self) -> None:
        self.memory = Decimal(0)
        self.memory_active = False
        self.memory_label.configure(text="")

    def memory_recall(self) -> None:
        if self.memory_active:
            self.expression.set(self.expression.get() + str(self.memory))

    def memory_add(self, sign: int) -> None:
        value = self.last_result if not self.expression.get().strip() else None
        if value is None:
            try:
                value = self._evaluator().evaluate(self.expression.get(), self.last_result or 0)
            except CalculationError:
                self.status.set("Hitung ekspresi sebelum memakai memori")
                return
        self.memory += value * sign
        self.memory_active = True
        self.memory_label.configure(text="M")
        self.status.set("Nilai memori diperbarui")

    def toggle_theme(self) -> None:
        self.settings["theme"] = "light" if self.settings.get("theme") == "dark" else "dark"
        self.apply_theme()
        self._save_settings()

    def toggle_angle(self) -> None:
        self.settings["angle_unit"] = "rad" if self.settings.get("angle_unit") == "deg" else "deg"
        self.angle_button.configure(text=self.settings["angle_unit"].upper())
        self._update_preview()
        self._save_settings()

    def toggle_number_format(self) -> None:
        self.settings["number_format"] = "international" if self.settings.get("number_format") == "id" else "id"
        self.format_button.configure(text="1,234" if self.settings["number_format"] == "international" else "1.234")
        self._update_preview()
        self._save_settings()

    def toggle_pin(self) -> None:
        self.settings["always_on_top"] = not self.settings.get("always_on_top", False)
        self.root.attributes("-topmost", self.settings["always_on_top"])
        self.pin_button.configure(text="📌" if self.settings["always_on_top"] else "⌖")
        self._save_settings()

    def toggle_history(self) -> None:
        if self.history_panel.winfo_viewable():
            self.history_panel.grid_remove()
        elif self.root.winfo_width() >= 700:
            self.history_panel.grid()

    def _resize_history(self, event: tk.Event) -> None:
        if event.widget is self.root and hasattr(self, "history_panel"):
            if event.width < 1000:
                self.history_panel.grid_remove()
            else:
                self.history_panel.grid()
            compact = event.width < 700
            if compact != self._compact_sidebar:
                self._compact_sidebar = compact
                self.sidebar.configure(width=62 if compact else 160, padding=(8 if compact else 16, 20))
                self.brand_label.configure(text="A" if compact else "ARTHER")
                if compact:
                    self.brand_subtitle.pack_forget()
                    self.shortcut_title.pack_forget()
                    self.shortcut_hint.pack_forget()
                else:
                    self.brand_subtitle.pack(anchor="w", pady=(0, 30))
                    self.shortcut_title.pack(anchor="w", pady=(0, 8))
                    self.shortcut_hint.pack(anchor="w")
                for key, button in self.nav_buttons.items():
                    button.configure(
                        text=self.nav_text[key][0 if compact else 1],
                        style="Nav.Compact.TButton" if compact else (
                            "Nav.Active.TButton" if self.mode == key else "Nav.TButton"
                        ),
                    )

    def apply_theme(self) -> None:
        name = self.settings.get("theme", "dark")
        if name not in PALETTES:
            name = "dark"
            self.settings["theme"] = name
        palette = PALETTES[name]
        style = ttk.Style(self.root)
        style.theme_use("clam")
        self.root.configure(bg=palette["bg"])
        style.configure(".", background=palette["bg"], foreground=palette["text"], font=("Segoe UI", 10))
        style.configure("TFrame", background=palette["bg"])
        style.configure("Card.TFrame", background=palette["panel"])
        style.configure("TLabel", background=palette["bg"], foreground=palette["text"])
        style.configure("Brand.TLabel", font=("Segoe UI", 17, "bold"), foreground=palette["accent"])
        style.configure("Caption.TLabel", font=("Segoe UI", 9), foreground=palette["muted"])
        style.configure("Hint.TLabel", font=("Segoe UI", 9), foreground=palette["muted"], justify="left")
        style.configure("Heading.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground=palette["muted"])
        style.configure("Expression.TEntry", fieldbackground=palette["entry"], foreground=palette["text"], bordercolor=palette["border"], insertcolor=palette["text"], font=("Cascadia Mono", 18))
        style.configure("Result.TLabel", background=palette["panel"], foreground=palette["text"], font=("Cascadia Mono", 25, "bold"))
        style.configure("Result.Error.TLabel", background=palette["panel"], foreground=palette["danger"], font=("Cascadia Mono", 14, "bold"))
        style.configure("TButton", background=palette["panel_alt"], foreground=palette["text"], borderwidth=0, padding=(10, 8))
        style.map("TButton", background=[("active", palette["border"])])
        style.configure("Nav.TButton", background=palette["bg"], anchor="w", padding=(12, 11))
        style.configure("Nav.Active.TButton", background=palette["accent"], foreground="#ffffff", anchor="w", padding=(12, 11))
        style.configure("Nav.Compact.TButton", background=palette["bg"], anchor="center", padding=(8, 11))
        style.configure("Tool.TButton", padding=(9, 6))
        style.configure("Mini.TButton", padding=(7, 4), font=("Segoe UI", 9))
        style.configure("Key.number.TButton", background=palette["panel"], font=("Segoe UI", 16, "bold"), padding=9)
        style.configure("Key.operator.TButton", background=palette["operator"], foreground=palette["accent"], font=("Segoe UI", 16, "bold"))
        style.configure("Key.clear.TButton", background=palette["operator"], font=("Segoe UI", 12, "bold"))
        style.configure("Key.fn.TButton", background=palette["panel_alt"], foreground=palette["accent"], font=("Segoe UI", 12, "bold"))
        style.configure("Key.equals.TButton", background=palette["accent"], foreground="#ffffff", font=("Segoe UI", 17, "bold"))
        style.map("Key.equals.TButton", background=[("active", palette["accent_hover"])])
        self.theme_button.configure(text="☾" if name == "dark" else "☼")
        self.format_button.configure(text="1,234" if self.settings.get("number_format") == "international" else "1.234")
        self.angle_button.configure(text=self.settings.get("angle_unit", "deg").upper())
        self.pin_button.configure(text="📌" if self.settings.get("always_on_top") else "⌖")
        self.root.attributes("-topmost", self.settings.get("always_on_top", False))
        self._refresh_history()

    def _save_settings(self) -> None:
        if self.storage:
            try:
                self.storage.save_settings(self.settings)
            except OSError as error:
                self.status.set(f"Pengaturan gagal disimpan: {error}")

    def close(self) -> None:
        if self.storage:
            try:
                self.settings["window"] = {"width": self.root.winfo_width(), "height": self.root.winfo_height()}
                self.storage.save_settings(self.settings)
                self.storage.close()
            except (OSError, sqlite3.Error) as error:
                messagebox.showwarning("Penyimpanan", f"Sebagian data tidak dapat disimpan:\n{error}")
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
