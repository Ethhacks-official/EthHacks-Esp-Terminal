# main.py
import tkinter as tk
from tkinter import ttk
import time
import serial
import serial.tools.list_ports
from terminal import TerminalPage


class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Serial Communication")
        self.serial_port = None

        self.page1 = tk.Frame(root)
        self.page2 = None  

        self.build_page1()
        self.page1.pack(fill="both", expand=True)

    def build_page1(self):
        self.page1.configure(bg="#1e1e1e")

        title = ttk.Label(
            self.page1,
            text="Connect to ESP32",
            font=("Helvetica", 18, "bold"),
            foreground="#ffffff",
            background="#1e1e1e"
        )
        title.pack(pady=(40, 20))

        form_frame = tk.Frame(self.page1, bg="#1e1e1e")
        form_frame.pack(pady=10)

        label = ttk.Label(
            form_frame,
            text="Select Port:",
            font=("Consolas", 12),
            foreground="#dddddd",
            background="#1e1e1e"
        )
        label.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="e")

        self.port_combo = ttk.Combobox(
            form_frame,
            values=self.get_serial_ports(),
            font=("Consolas", 12),
            width=35,
            state="readonly"
        )
        self.port_combo.grid(row=0, column=1, padx=(0, 0), pady=10)

        btn_frame = tk.Frame(self.page1, bg="#1e1e1e")
        btn_frame.pack(pady=15)

        refresh_btn = ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_ports)
        refresh_btn.grid(row=0, column=0, padx=10)

        connect_btn = ttk.Button(btn_frame, text="🔌 Connect", command=self.connect_serial)
        connect_btn.grid(row=0, column=1, padx=10)

        # Styling
        style = ttk.Style()
        style.theme_use("default")

        style.configure("TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground="#000000",
            arrowsize=16,
            padding=4,
            relief="solid",
            borderwidth=1
        )

        style.map("TCombobox",
            fieldbackground=[("readonly", "#ffffff")],
            foreground=[("readonly", "#000000")],
            background=[("readonly", "#ffffff")]
        )

        style.configure("TButton",
            font=("Consolas", 11, "bold"),
            foreground="#ffffff",
            background="#3c3c3c",
            borderwidth=1,
            focusthickness=3,
            focuscolor="none",
            padding=6
        )

        style.map("TButton",
            background=[("active", "#555555")],
            foreground=[("disabled", "#777777")]
        )




    def refresh_ports(self):
        ports = self.get_serial_ports()
        self.port_combo['values'] = ports

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        ports_list = []
        for port in ports:
            if "USB" in port.device or "ttyUSB" in port.device:
                try:
                    with serial.Serial(port.device, 115200, timeout=1) as esp_port:
                        ports_list.append(port.device)
                except Exception:
                    continue
        return ports_list

    def connect_serial(self):
        port = self.port_combo.get()
        if port:
            try:
                self.serial_port = serial.Serial(port, 115200, timeout=1)
                self.serial_port.reset_input_buffer()
                self.serial_port.write(b"Want to Connect\n")

                timeout = time.time() + 2
                response = b""
                while time.time() < timeout:
                    if self.serial_port.in_waiting:
                        response += self.serial_port.read(self.serial_port.in_waiting)
                        if b"\n" in response:
                            break
                    time.sleep(0.1)

                decoded = response.decode(errors='ignore').strip()
                if "ESP32" in decoded:
                    self.page1.pack_forget()
                    self.page2 = TerminalPage(self.root, send_command_fn=self.send_uart_command)
                    self.page2.pack(fill="both", expand=True)

            except Exception as e:
                print(f"Connection Error: {e}")

    def send_uart_command(self, msg: str) -> str:
        """Send command to ESP32 and return response."""
        if msg and self.serial_port:
            try:
                self.serial_port.reset_input_buffer()
                self.serial_port.write((msg + "\n").encode())

                timeout = time.time() + 2
                response = b""
                while time.time() < timeout:
                    if self.serial_port.in_waiting:
                        response += self.serial_port.read(self.serial_port.in_waiting)
                        if b"\n" in response:
                            break
                    time.sleep(0.1)

                decoded = response.decode(errors='ignore').strip()
                return decoded if decoded else "[No response]"
            except Exception as e:
                return f"[Error: {e}]"
        return "[Not connected]"

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x500")
    app = SerialApp(root)
    root.mainloop()
