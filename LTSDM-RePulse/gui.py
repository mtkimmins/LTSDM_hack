import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class RePulseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LTSDM RePulse")
        self.geometry("700x180")
        self.minsize(620, 160)

        self.wav_path_var = tk.StringVar()
        self._build_start_screen()

    def _build_start_screen(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text="Select a WAV file to convert",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        row = ttk.Frame(root)
        row.pack(fill="x", pady=(0, 10))

        ttk.Label(row, text="WAV:", width=8).pack(side="left")
        ttk.Entry(row, textvariable=self.wav_path_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        ttk.Button(row, text="Browse", command=self._browse_wav).pack(side="left")

        ttk.Button(root, text="Convert", command=self._convert).pack(anchor="e")

    def _browse_wav(self):
        path = filedialog.askopenfilename(
            title="Select WAV file",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if path:
            self.wav_path_var.set(path)

    def _convert(self):
        wav_path = self.wav_path_var.get().strip()
        if not wav_path:
            messagebox.showerror("No file selected", "Please choose a WAV file first.")
            return

        if not os.path.isfile(wav_path):
            messagebox.showerror("File not found", f"Cannot find file:\n{wav_path}")
            return

        bin_path = os.path.splitext(wav_path)[0] + ".bin"
        try:
            subprocess.run(
                ["a1800_codec", wav_path, bin_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            messagebox.showerror(
                "Converter not found",
                "a1800_codec is not installed or not on PATH.",
            )
            return
        except subprocess.CalledProcessError as exc:
            messagebox.showerror(
                "Conversion failed",
                (exc.stderr or "a1800_codec exited with an error.").strip(),
            )
            return

        messagebox.showinfo("Convert", f"Conversion complete:\n{bin_path}")


def run_gui():
    app = RePulseGUI()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
