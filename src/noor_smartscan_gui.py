"""Tkinter interface for Noor SmartScan. Run on Windows with Pillow installed."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from PIL import Image, ImageTk
from noor_smartscan import SUPPORTED_EXTENSIONS, enhance_page, export_pdf, open_page


class SmartScanApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Noor SmartScan — Offline Image to PDF")
        self.root.geometry("900x620")
        self.root.minsize(720, 480)
        self.paths: list[Path] = []
        self.photo = None
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Action.TButton", padding=(10, 7))

    def _build(self):
        shell = ttk.Frame(self.root, padding=16)
        shell.pack(fill="both", expand=True)
        ttk.Label(shell, text="Noor SmartScan", style="Title.TLabel").pack(anchor="w")
        ttk.Label(shell, text="Prepare scanned or photographed pages for an offline PDF.").pack(anchor="w", pady=(2, 12))
        body = ttk.Frame(shell)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=(0, 14))
        self.listbox = tk.Listbox(left, width=42, height=20, activestyle="dotbox", exportselection=False)
        self.listbox.pack(fill="y", expand=True)
        self.listbox.bind("<<ListboxSelect>>", lambda _e: self._preview())
        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=8)
        for text, command in (("Add images", self._add), ("Remove", self._remove),
                              ("Move up", lambda: self._move(-1)), ("Move down", lambda: self._move(1)),
                              ("Rotate 90°", self._rotate)):
            ttk.Button(buttons, text=text, command=command, style="Action.TButton").pack(fill="x", pady=2)
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        self.preview = ttk.Label(right, text="Select an image to preview", anchor="center")
        self.preview.pack(fill="both", expand=True)
        settings = ttk.LabelFrame(shell, text="PDF settings", padding=10)
        settings.pack(fill="x", pady=(12, 0))
        ttk.Label(settings, text="Enhancement").grid(row=0, column=0, sticky="w")
        self.preset = tk.StringVar(value="Original")
        ttk.Combobox(settings, textvariable=self.preset, values=("Original", "Grayscale", "Clear B&W"),
                     state="readonly", width=18).grid(row=0, column=1, padx=(8, 20), sticky="w")
        ttk.Label(settings, text="Resolution (DPI)").grid(row=0, column=2, sticky="w")
        self.dpi = tk.StringVar(value="300")
        ttk.Combobox(settings, textvariable=self.dpi, values=("150", "200", "300", "600"),
                     width=8).grid(row=0, column=3, padx=8, sticky="w")
        ttk.Button(settings, text="Export multi-page PDF", command=self._export,
                   style="Action.TButton").grid(row=0, column=4, padx=(18, 0))
        ttk.Label(shell, text="Local processing only • Original image files are never modified").pack(anchor="w", pady=(8, 0))

    def _add(self):
        types = [("Images", " ".join("*" + ext for ext in sorted(SUPPORTED_EXTENSIONS))), ("All files", "*.*")]
        names = filedialog.askopenfilenames(title="Choose scanned pages", filetypes=types)
        for name in names:
            path = Path(name)
            if path not in self.paths:
                self.paths.append(path)
                self.listbox.insert("end", path.name)
        if self.paths and not self.listbox.curselection():
            self.listbox.selection_set(0)
            self._preview()

    def _selected(self):
        selection = self.listbox.curselection()
        return selection[0] if selection else None

    def _remove(self):
        index = self._selected()
        if index is None:
            return
        self.paths.pop(index)
        self.listbox.delete(index)
        self.preview.configure(image="", text="Select an image to preview")
        if self.paths:
            self.listbox.selection_set(min(index, len(self.paths) - 1))
            self._preview()

    def _move(self, offset):
        index = self._selected()
        if index is None or not 0 <= index + offset < len(self.paths):
            return
        other = index + offset
        self.paths[index], self.paths[other] = self.paths[other], self.paths[index]
        label = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(other, label)
        self.listbox.selection_set(other)
        self._preview()

    def _rotate(self):
        index = self._selected()
        if index is None:
            return
        try:
            with Image.open(self.paths[index]) as im:
                rotated = im.rotate(90, expand=True)
                # Keep edit in memory in a temporary local image; never replace the source.
                from tempfile import NamedTemporaryFile
                with NamedTemporaryFile(prefix="noor-smartscan-", suffix=self.paths[index].suffix, delete=False) as tmp:
                    temp_path = Path(tmp.name)
                rotated.save(temp_path)
            self.paths[index] = temp_path
            self.listbox.delete(index)
            self.listbox.insert(index, self.paths[index].name)
            self.listbox.selection_set(index)
            self._preview()
        except Exception as exc:
            messagebox.showerror("Rotate failed", str(exc))

    def _preview(self):
        index = self._selected()
        if index is None:
            return
        try:
            image = enhance_page(open_page(self.paths[index]), self.preset.get())
            image.thumbnail((560, 440))
            self.photo = ImageTk.PhotoImage(image)
            self.preview.configure(image=self.photo, text="")
        except Exception as exc:
            self.preview.configure(image="", text=f"Cannot preview this file:\n{exc}")

    def _export(self):
        if not self.paths:
            messagebox.showinfo("No pages", "Add at least one image first.")
            return
        name = filedialog.asksaveasfilename(title="Save PDF", defaultextension=".pdf",
                                           filetypes=[("PDF document", "*.pdf")])
        if not name:
            return
        try:
            export_pdf(self.paths, name, int(self.dpi.get()), self.preset.get())
            messagebox.showinfo("Export complete", f"PDF saved successfully:\n{name}")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))


def run_gui():
    root = tk.Tk()
    SmartScanApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
