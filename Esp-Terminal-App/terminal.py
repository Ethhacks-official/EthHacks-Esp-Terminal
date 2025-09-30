# terminal_page.py
import tkinter as tk
from tkinter import ttk

PROMPT = "$ "

class TerminalPage(tk.Frame):
    def __init__(self, parent, send_command_fn, **kwargs):
        super().__init__(parent, bg="#1e1e1e", **kwargs)
        self.send_command_fn = send_command_fn

        self.output = None
        self.build_ui()
        self.print_prompt()

    def build_ui(self):
        frame = tk.Frame(self, bg="#1e1e1e")
        frame.pack(expand=True, fill="both")

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar",
            gripcount=0,
            background="#3c3c3c",
            darkcolor="#2e2e2e",
            lightcolor="#2e2e2e",
            troughcolor="#1e1e1e",
            bordercolor="#1e1e1e",
            arrowcolor="#c7c7c7"
        )

        scrollbar = ttk.Scrollbar(frame, style="Vertical.TScrollbar", orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.output = tk.Text(
            frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg="#1e1e1e",
            fg="#c7c7c7",
            insertbackground="white",
            font=("Consolas", 12),
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.output.pack(expand=True, fill="both")
        scrollbar.config(command=self.output.yview)

        # Bindings
        self.output.bind("<Return>", self.run_command)
        self.output.bind("<BackSpace>", self.backspace_handler)
        self.output.bind("<Left>", self.arrow_left_block)
        self.output.bind("<Delete>", self.arrow_left_block)
        self.output.bind("<Button-1>", self.mouse_click_guard)
        self.output.bind("<Key>", self.on_key)

        # Block navigation keys
        self.output.bind("<Up>", self.block_navigation)
        self.output.bind("<Down>", self.block_navigation)
        self.output.bind("<Prior>", self.block_navigation)   # PageUp
        self.output.bind("<Next>", self.block_navigation)    # PageDown

        self.output.focus()

    def run_command(self, event=None):
        line_start = self.output.index("insert linestart")
        full_line = self.output.get(line_start, "end-1c")
        command = full_line[len(PROMPT):].strip() if full_line.startswith(PROMPT) else ""

        if command == "clear":
            self.output.delete("1.0", tk.END)
            self.print_prompt()
            return "break"
        elif command == "exit":
            self.quit()
            return "break"

        try:
            response = self.send_command_fn(command)
            self.output.insert(tk.END, "\n" + response)
        except Exception as e:
            self.output.insert(tk.END, f"\nError: {e}")

        self.print_prompt()
        return "break"

    def print_prompt(self):
        self.output.insert(tk.END, "\n" + PROMPT)
        self.output.mark_set("insert", "end-1c")
        self.output.mark_set("input_start", self.output.index("insert"))
        self.output.see("end")

    def backspace_handler(self, event):
        line_start = self.output.index("insert linestart")
        input_start = line_start + f"+{len(PROMPT)}c"
        if self.output.compare("insert", "<=", input_start):
            return "break"
        self.output.delete("insert-1c", "insert")
        return "break"

    def arrow_left_block(self, event):
        line_start = self.output.index("insert linestart")
        input_start = line_start + f"+{len(PROMPT)}c"
        if self.output.compare("insert", "<", input_start):
            return "break"

    def mouse_click_guard(self, event):
        self.output.after(1, self.force_cursor_after_prompt)

    def force_cursor_after_prompt(self):
        line_start = self.output.index("insert linestart")
        input_start = line_start + f"+{len(PROMPT)}c"
        if self.output.compare("insert", "<", input_start):
            self.output.mark_set("insert", "end-1c")

    def on_key(self, event):
        self.force_cursor_after_prompt()

    def block_navigation(self, event):
        self.force_cursor_after_prompt()
        return "break"
