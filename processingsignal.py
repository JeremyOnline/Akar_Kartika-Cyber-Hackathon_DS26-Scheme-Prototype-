import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# ==========================================
# 1. KONFIGURASI PARAMETER (Sesuaikan SDR Anda)
# ==========================================
sample_rate = 2e6  # Contoh: 2 MHz (Sample rate saat perekaman)
file_path = "file_iq_dummy.iq"  # Ganti dengan nama file IQ Anda

# Tipe data umum file IQ:
# - np.complex64 : Format float32 interleave (umum di HackRF / GQRX)
# - np.int16     : Format short integer interleave (umum di BladeRF)
# - np.uint8     : Format unsigned 8-bit (umum di RTL-SDR .cu8 atau .bin)
data_type = np.complex64

# ==========================================
# 2. MEMBACA FILE IQ
# ==========================================
if data_type == np.complex64:
    # Jika file sudah langsung dalam format kompleks 64-bit
    iq_data = np.fromfile(file_path, dtype=np.complex64)
else:
    # Jika formatnya int16 atau uint8, dibaca sebagai data interleave (I, Q, I, Q...)
    raw_data = np.fromfile(file_path, dtype=data_type)

    # Konversi ke float antara -1.0 s/d 1.0 (khusus untuk integer)
    if data_type == np.uint8:
        raw_data = (raw_data.astype(np.float32) - 127.5) / 127.5
    elif data_type == np.int16:
        raw_data = raw_data.astype(np.float32) / 32768.0

    # Gabungkan komponen I (indeks genap) dan Q (indeks ganjil) menjadi bilangan kompleks
    iq_data = raw_data[0::2] + 1j * raw_data[1::2]

# Batasi jumlah sampel yang diproses agar memori tidak penuh (misal: 100.000 sampel awal)
num_samples = min(100000, len(iq_data))
iq_data = iq_data[:num_samples]

print(f"Berhasil memuat {len(iq_data)} sampel kompleks.")

# ==========================================
# 3. PEMROSESAN SIGNAL (Contoh: Low-Pass Filter)
# ==========================================
# Membuat filter untuk membuang noise di luar frekuensi 200 kHz
cutoff_freq = 200e3  # 200 kHz
nyquist = 0.5 * sample_rate
normal_cutoff = cutoff_freq / nyquist

# Membuat koefisien filter FIR menggunakan SciPy
num_taps = 64
fir_coeff = signal.firwin(num_taps, normal_cutoff)

# Mengaplikasikan filter ke data IQ
filtered_iq = signal.lfilter(fir_coeff, 1.0, iq_data)

# ==========================================
# 4. VISUALISASI (Spektrum Frekuensi & Constellation)
# ==========================================
# Hitung FFT (Power Spectral Density)
fft_raw = np.fft.fftshift(np.fft.fft(iq_data))
fft_filtered = np.fft.fftshift(np.fft.fft(filtered_iq))
freqs = np.fft.fftshift(np.fft.fftfreq(len(iq_data), 1 / sample_rate))

psd_raw = 10 * np.log10(np.abs(fft_raw) ** 2 / len(iq_data))
psd_filtered = 10 * np.log10(np.abs(fft_filtered) ** 2 / len(filtered_iq))

# Plotting
plt.figure(figsize=(14, 6))

# Subplot 1: Spektrum Frekuensi (Sebelum vs Sesudah Filter)
plt.subplot(1, 2, 1)
plt.plot(freqs / 1e6, psd_raw, label="Sinyal Asli (Raw)", alpha=0.5)
plt.plot(freqs / 1e6, psd_filtered, label="Setelah Low-Pass Filter", color="red")
plt.title("Analisis Spektrum (PSD)")
plt.xlabel("Frekuensi (MHz)")
plt.ylabel("Power (dB)")
plt.grid(True)
plt.legend()

# Subplot 2: Constellation Diagram (I vs Q)
plt.subplot(1, 2, 2)
plt.scatter(
    np.real(filtered_iq[::10]),
    np.imag(filtered_iq[::10]),
    s=1,
    color="purple",
    alpha=0.6,
)
plt.title("Diagram Konstelasi (I vs Q)")
plt.xlabel("In-Phase (I)")
plt.ylabel("Quadrature (Q)")
plt.grid(True)
plt.axis("equal")

plt.tight_layout()
plt.show()
