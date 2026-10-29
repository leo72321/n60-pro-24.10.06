"""Windows GUI: copy decryption password derived from your private JSON."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from archive_key import derive_archive_password

root = tk.Tk()
root.title("N60 Pro - encrypted firmware password")
root.geometry("740x170")
root.resizable(False, False)

tk.Label(root, text="Choose the saved ROUTER_CONFIG JSON used for this build.").pack(pady=12)
password = tk.StringVar()
tk.Entry(root, textvariable=password, width=92, state="readonly").pack(padx=18, pady=8)


def choose_config():
    path = filedialog.askopenfilename(
        title="Select your saved ROUTER_CONFIG JSON",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )
    if not path:
        return
    try:
        password.set(derive_archive_password(Path(path).read_text(encoding="utf-8-sig")))
        root.clipboard_clear()
        root.clipboard_append(password.get())
        root.update()
        messagebox.showinfo("Copied", "7-Zip password copied to clipboard.")
    except (OSError, ValueError) as exc:
        messagebox.showerror("Error", "Unable to read JSON: " + str(exc))


tk.Button(
    root,
    text="Choose ROUTER_CONFIG.json and copy password",
    command=choose_config,
).pack(pady=10)
root.mainloop()
