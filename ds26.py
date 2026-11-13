import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

class DS26App:
    def __init__(self, root):
        self.root = root
        self.root.title("DS26 - Tactical Drone Interceptor & Analyzer")
        self.root.geometry("1280x720")
        self.root.configure(bg="#0b0f19")

        # Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Color palette (Cyberpunk / Tactical Dark)
        self.bg_dark = "#0b0f19"
        self.bg_panel = "#111827"
        self.accent_green = "#10b981"
        self.accent_red = "#ef4444"
        self.accent_cyan = "#06b6d4"
        self.text_light = "#f3f4f6"
        self.text_dim = "#9ca3af"

        # Mock Drone Data
        self.drones = [
            {"id": "DRONE-01", "name": "DJI Mavic 3 Enterprise", "fw": "v01.02.0400", "freq": "2.412 GHz", "rssi": "-64 dBm", "dir": "142° SE", "class": "Komersial / Rekayasa", "vulnerable": "Tinggi (Weak Auth)"},
            {"id": "DRONE-02", "name": "FPV Custom Kamikaze", "fw": "ELRS v3.3.0", "freq": "915 MHz", "rssi": "-51 dBm", "dir": "045° NE", "class": "Taktis / Custom FPV", "vulnerable": "Sedang"},
            {"id": "DRONE-03", "name": "Orlan-10 Recon Scout", "fw": "RU-Mil-v4.1", "freq": "5.820 GHz", "rssi": "-82 dBm", "dir": "270° W", "class": "Militer Pengintai", "vulnerable": "Rendah (Secured)"}
        ]
        self.selected_drone = self.drones[0]

        # Show tutorial prompt on startup
        self.show_tutorial_prompt()

        # Build Main UI Layout
        self.create_header()
        self.create_main_content()
        
        # Start Radar Animation Loop
        self.angle = 0
        self.update_radar()

    def show_tutorial_prompt(self):
        self.tut_win = tk.Toplevel(self.root)
        self.tut_win.title("DS26 - Panduan Pemula / Onboarding")
        self.tut_win.geometry("620x480")
        self.tut_win.configure(bg=self.bg_panel)
        self.tut_win.transient(self.root)
        self.tut_win.grab_set()

        lbl_title = tk.Label(self.tut_win, text="SELAMAT DATANG DI SISTEM DS26", font=("Consolas", 15, "bold"), fg=self.accent_cyan, bg=self.bg_panel)
        lbl_title.pack(pady=20)

        tutorial_text = (
            "Panduan Singkat Penggunaan Software DS26:\n\n"
            "1. RADAR REAL-TIME:\n"
            "   Menampilkan posisi target pesawat nirawak di sekitar area operasi.\n"
            "   Klik salah satu titik target pada radar untuk melihat detail spesifikasinya.\n\n"
            "2. INFORMASI PERANGKAT & FIRMWARE:\n"
            "   Panel sebelah kanan menampilkan merek, versi firmware, kekuatan sinyal (RSSI),\n"
            "   frekuensi, estimasi arah, serta klasifikasi perangkat.\n\n"
            "3. TOMBOL EKSEKUSI (HACK & TAKEOVER):\n"
            "   Tekan tombol 'EXECUTE HACK' untuk menyuntikkan perintah (command injection)\n"
            "   pada protokol target, lalu pilih opsi 'Ambil Alih' atau 'Shutdown Paksa'.\n"
        )
        
        lbl_desc = tk.Label(self.tut_win, text=tutorial_text, font=("Consolas", 10), fg=self.text_light, bg=self.bg_panel, justify="left")
        lbl_desc.pack(padx=30, pady=10)

        btn_frame = tk.Frame(self.tut_win, bg=self.bg_panel)
        btn_frame.pack(pady=20)

        btn_start = tk.Button(btn_frame, text="Mulai Eksplorasi (Ikuti Panduan)", command=self.tut_win.destroy, bg=self.accent_cyan, fg="#000", font=("Consolas", 10, "bold"), padx=10, pady=5)
        btn_start.pack(side=tk.LEFT, padx=10)

        btn_skip = tk.Button(btn_frame, text="Lewati (Skip ke Dashboard)", command=self.tut_win.destroy, bg="#374151", fg=self.text_light, font=("Consolas", 10), padx=10, pady=5)
        btn_skip.pack(side=tk.LEFT, padx=10)

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.bg_panel, height=60, relief=tk.RAISED)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        lbl_logo = tk.Label(header_frame, text="🛡️ DS26 [TACTICAL INTERCEPTOR]", font=("Consolas", 14, "bold"), fg=self.accent_cyan, bg=self.bg_panel)
        lbl_logo.pack(side=tk.LEFT, padx=15, pady=15)

        self.lbl_status = tk.Label(header_frame, text="STATUS: SCANNING ACTIVE (RF BAND 2.4/5.8GHz)", font=("Consolas", 10, "bold"), fg=self.accent_green, bg=self.bg_panel)
        self.lbl_status.pack(side=tk.RIGHT, padx=15, pady=15)

    def create_main_content(self):
        content_frame = tk.Frame(self.root, bg=self.bg_dark)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Column: Radar
        left_frame = tk.Frame(content_frame, bg=self.bg_panel, width=420)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))

        lbl_radar_title = tk.Label(left_frame, text="RADAR SINYAL TAKTIS REAL-TIME", font=("Consolas", 11, "bold"), fg=self.text_light, bg=self.bg_panel)
        lbl_radar_title.pack(anchor="w", padx=15, pady=10)

        self.canvas = tk.Canvas(left_frame, width=380, height=380, bg="#030712", highlightthickness=0)
        self.canvas.pack(padx=15, pady=10)
        self.canvas.bind("<Button-1>", self.on_radar_click)

        self.lbl_sig_summary = tk.Label(left_frame, text="Frekuensi Terdeteksi: 3 Saluran Aktif\nDeteksi Sinyal: Stabil (-64 dBm)", font=("Consolas", 9), fg=self.text_dim, bg=self.bg_panel, justify="left")
        self.lbl_sig_summary.pack(anchor="w", padx=15, pady=10)

        # Right Column: Drone Info & Execution Control
        right_frame = tk.Frame(content_frame, bg=self.bg_panel)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        lbl_info_title = tk.Label(right_frame, text="INFORMASI KLASIFIKASI & FIRMWARE DRONE", font=("Consolas", 11, "bold"), fg=self.text_light, bg=self.bg_panel)
        lbl_info_title.pack(anchor="w", padx=20, pady=10)

        self.info_container = tk.Frame(right_frame, bg=self.bg_panel)
        self.info_container.pack(fill=tk.X, padx=20, pady=10)

        self.lbl_id = tk.Label(self.info_container, text="ID Perangkat: -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_id.pack(fill=tk.X, pady=5)
        self.lbl_name = tk.Label(self.info_container, text="Model/Merek: -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_name.pack(fill=tk.X, pady=5)
        self.lbl_fw = tk.Label(self.info_container, text="Firmware: -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_fw.pack(fill=tk.X, pady=5)
        self.lbl_class = tk.Label(self.info_container, text="Klasifikasi: -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_class.pack(fill=tk.X, pady=5)
        self.lbl_freq = tk.Label(self.info_container, text="Frekuensi RF: -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_freq.pack(fill=tk.X, pady=5)
        self.lbl_rssi = tk.Label(self.info_container, text="Signal Strength (RSSI): -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_rssi.pack(fill=tk.X, pady=5)
        self.lbl_dir = tk.Label(self.info_container, text="Estimasi Arah: -", font=("Consolas", 11), fg=self.text_light, bg=self.bg_panel, anchor="w")
        self.lbl_dir.pack(fill=tk.X, pady=5)

        exec_frame = tk.Frame(right_frame, bg=self.bg_panel)
        exec_frame.pack(fill=tk.X, padx=20, pady=25)

        self.btn_exec = tk.Button(exec_frame, text="🚀 EKSEKUSI PERETASAN (DS26 COMMAND INJECTION)", bg=self.accent_red, fg="#fff", font=("Consolas", 11, "bold"), padx=15, pady=12, command=self.execute_hack)
        self.btn_exec.pack(fill=tk.X)

        lbl_term_title = tk.Label(right_frame, text="LOG AKTIVITAS TAKTIS", font=("Consolas", 10, "bold"), fg=self.text_dim, bg=self.bg_panel)
        lbl_term_title.pack(anchor="w", padx=20, pady=(5, 0))

        self.term_box = tk.Text(right_frame, height=7, bg="#030712", fg=self.accent_green, font=("Consolas", 9), relief=tk.FLAT)
        self.term_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.term_box.insert(tk.END, "[SYSTEM] DS26 Core initialized successfully.\n[SCANNER] RF Spectrum monitoring active on 2.4 GHz & 5.8 GHz.\n[INFO] 3 target drones detected within range.\n")
        self.term_box.config(state=tk.DISABLED)

        self.update_drone_info()

    def update_drone_info(self):
        d = self.selected_drone
        self.lbl_id.config(text=f"ID Perangkat     : {d['id']}")
        self.lbl_name.config(text=f"Model/Merek    : {d['name']}")
        self.lbl_fw.config(text=f"Firmware       : {d['fw']}")
        self.lbl_class.config(text=f"Klasifikasi    : {d['class']}")
        self.lbl_freq.config(text=f"Frekuensi RF   : {d['freq']}")
        self.lbl_rssi.config(text=f"Signal RSSI    : {d['rssi']}")
        self.lbl_dir.config(text=f"Estimasi Arah  : {d['dir']}")

    def update_radar(self):
        self.canvas.delete("all")
        cx, cy, r = 190, 190, 170

        for rad in [60, 120, 170]:
            self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad, outline="#1f2937", width=1)
        self.canvas.create_line(cx-r, cy, cx+r, cy, fill="#1f2937")
        self.canvas.create_line(cx, cy-r, cx, cy+r, fill="#1f2937")

        rad_angle = math.radians(self.angle)
        sx = cx + r * math.cos(rad_angle)
        sy = cy + r * math.sin(rad_angle)
        self.canvas.create_line(cx, cy, sx, sy, fill=self.accent_green, width=2)

        blip_coords = [(110, 90, self.drones[0]), (270, 130, self.drones[1]), (140, 270, self.drones[2])]
        for bx, by, drone in blip_coords:
            color = self.accent_cyan if drone == self.selected_drone else self.accent_red
            self.canvas.create_oval(bx-6, by-6, bx+6, by+6, fill=color, outline="#fff")
            self.canvas.create_text(bx, by-15, text=drone['id'], fill=self.text_light, font=("Consolas", 8, "bold"))

        self.angle = (self.angle + 5) % 360
        self.root.after(50, self.update_radar)

    def on_radar_click(self, event):
        blip_coords = [(110, 90, self.drones[0]), (270, 130, self.drones[1]), (140, 270, self.drones[2])]
        for bx, by, drone in blip_coords:
            if math.hypot(event.x - bx, event.y - by) < 15:
                self.selected_drone = drone
                self.update_drone_info()
                self.log_terminal(f"[RADAR] Target selected: {drone['id']} ({drone['name']})")
                break

    def execute_hack(self):
        d = self.selected_drone
        self.log_terminal(f"[HACK] Initiating command injection payload for {d['id']}...")
        
        success = random.choice([True, True, False])
        
        if success:
            self.log_terminal(f"[SUCCESS] Handshake vulnerability exploited on {d['id']}!")
            res = messagebox.askyesnocancel("Peretasan Berhasil", f"Enkripsi {d['name']} ({d['id']}) berhasil ditembus!\n\nPilih Tindakan Taktis:\n- YES: Ambil Alih Kendali (Takeover Control)\n- NO: Shutdown Paksa (Emergency Shutdown)")
            if res is True:
                self.log_terminal(f"[TAKEOVER] {d['id']} navigation hijacked. Forced landing initiated.")
                messagebox.showinfo("Takeover Active", f"Drone {d['id']} berhasil diambil alih. Melakukan pendaratan otomatis.")
            elif res is False:
                self.log_terminal(f"[SHUTDOWN] {d['id']} flight controller disabled. Motor shutdown executed.")
                messagebox.showwarning("Emergency Shutdown", f"Sinyal putus darurat dikirim. {d['id']} dimatikan paksa di udara.")
        else:
            self.log_terminal(f"[FAILED] Protocol armor too strong on {d['id']}. Target rejected injection.")
            messagebox.showerror("Peretasan Gagal", f"Gagal menembus enkripsi {d['name']}. Sinyal target terlindungi.")

    def log_terminal(self, text):
        self.term_box.config(state=tk.NORMAL)
        self.term_box.insert(tk.END, f"{text}\n")
        self.term_box.see(tk.END)
        self.term_box.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = DS26App(root)
    root.mainloop()