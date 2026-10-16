# PRD: Arther Smart Application Calculator

**Versi:** 1.0 (Draft)\
**Tanggal:** 16 Oktober 2026\
**Platform:** Windows 10/11 (64-bit), aplikasi desktop portable\
**Bahasa Pemrograman:** Python\
**Status:** Draft untuk keperluan belajar

## 1. Ringkasan (Overview)

**Arther Smart Application Calculator** adalah aplikasi kalkulator desktop untuk Windows yang minimalis, modern, dan responsif. Selain operasi hitung dasar, aplikasi ini "pintar": pengguna dapat mengetik ekspresi matematika secara bebas (misalnya `15% * 2.500.000 + sqrt(144)`), melihat hasil secara langsung sebelum menekan Enter, menyimpan riwayat perhitungan, serta memakai mode ilmiah, programmer, dan konverter satuan.

Aplikasi dikemas menjadi **satu file `.exe` portable** yang dapat dijalankan langsung tanpa instalasi dan tanpa perlu menginstal Python di komputer pengguna.

## 2. Latar Belakang dan Problem Statement

Kalkulator bawaan sistem operasi sudah cukup untuk hitungan sederhana, tetapi sering kali:

- Mengharuskan pengguna menekan tombol satu per satu, tidak nyaman untuk ekspresi panjang.
- Riwayat perhitungan terbatas dan tidak mudah dipakai ulang.
- Berpindah antara hitungan biasa, ilmiah, dan konversi satuan terasa terpisah.
- Tidak bisa dibawa dalam flashdisk dan dijalankan di komputer mana pun tanpa instalasi.

**Problem statement:** Pengguna membutuhkan kalkulator yang cepat, mendukung input ketikan bebas dengan hasil langsung, tampil rapi, dan bisa dijalankan secara portable di Windows.

Selain itu, proyek ini berfungsi sebagai sarana belajar pengembangan aplikasi desktop dengan Python, mulai dari desain UI, logika aplikasi, pengujian, hingga pengemasan menjadi executable.

## 3. Tujuan dan Success Metrics

### Tujuan Produk

1. Menyediakan kalkulator dengan antarmuka minimalis, menarik, dan nyaman dipakai.
2. Mendukung input lewat klik tombol maupun keyboard dengan hasil langsung (*live preview*).
3. Menyediakan fitur "smart": riwayat, memori, konversi satuan, dan penanganan kesalahan yang ramah.
4. Dapat dijalankan secara portable dari satu file `.exe`.
5. Menjadi proyek belajar Python desktop yang terstruktur dan mudah dikembangkan.

### Success Metrics

| Metrik | Target |
| --- | --- |
| Waktu buka aplikasi (cold start dari `.exe`) | ≤ 3 detik |
| Latensi hasil *live preview* setelah mengetik | ≤ 100 ms |
| Akurasi hitungan dasar (uji dengan 100+ kasus uji) | 100% lulus |
| Ukuran file `.exe` | ≤ 60 MB |
| Penggunaan RAM saat idle | ≤ 150 MB |
| Aplikasi berjalan di Windows 10/11 tanpa instalasi Python | Ya |
| Skor kepuasan tampilan (uji teman/rekan) | ≥ 4 dari 5 |

## 4. Target Pengguna dan Persona

**Persona 1 – Dimas, 20, mahasiswa teknik**\
Sering menghitung rumus dengan fungsi trigonometri dan logaritma. Ingin mengetik ekspresi langsung dan membawa aplikasi di flashdisk untuk dipakai di komputer laboratorium kampus.

**Persona 2 – Sinta, 28, staf administrasi keuangan**\
Menghitung persentase, pajak, dan total berulang. Membutuhkan riwayat yang bisa disalin dan format angka yang rapi (pemisah ribuan).

**Persona 3 – Pak Arif, 45, wiraswasta**\
Menginginkan tampilan yang jelas, tombol besar, dan konversi satuan sederhana (kg, liter, meter) tanpa pengaturan rumit.

## 5. User Stories

| ID | User Story | Prioritas |
| --- | --- | --- |
| US-01 | Sebagai pengguna, saya ingin menghitung operasi dasar (+, −, ×, ÷) dengan tombol maupun keyboard agar bisa berhitung cepat. | Must |
| US-02 | Sebagai pengguna, saya ingin mengetik ekspresi lengkap dan melihat hasilnya langsung agar tidak perlu menekan banyak tombol. | Must |
| US-03 | Sebagai pengguna, saya ingin melihat riwayat perhitungan agar bisa memakai ulang hasil sebelumnya. | Must |
| US-04 | Sebagai pengguna, saya ingin menjalankan aplikasi dari satu file `.exe` tanpa instalasi agar bisa dibawa ke mana saja. | Must |
| US-05 | Sebagai pengguna, saya ingin mode ilmiah (sin, cos, tan, log, ln, akar, pangkat, faktorial) agar bisa menyelesaikan hitungan lanjutan. | Should |
| US-06 | Sebagai pengguna, saya ingin fungsi memori (MC, MR, M+, M−) agar bisa menyimpan hasil sementara. | Should |
| US-07 | Sebagai pengguna, saya ingin mode gelap dan terang agar nyaman di berbagai kondisi cahaya. | Should |
| US-08 | Sebagai pengguna, saya ingin menyalin hasil dengan satu klik atau pintasan keyboard agar mudah ditempel ke aplikasi lain. | Should |
| US-09 | Sebagai pengguna, saya ingin konverter satuan (panjang, berat, suhu, volume, kecepatan) agar tidak perlu membuka alat lain. | Should |
| US-10 | Sebagai pengguna, saya ingin kalkulator persentase dan diskon/pajak yang mudah agar menghitung kebutuhan sehari-hari. | Could |
| US-11 | Sebagai pengguna, saya ingin mode programmer (HEX, DEC, OCT, BIN, operasi bitwise) agar membantu pekerjaan pemrograman. | Could |
| US-12 | Sebagai pengguna, saya ingin jendela selalu di atas (*always on top*) agar bisa berhitung sambil bekerja di aplikasi lain. | Could |

## 6. Functional Requirements

### 6.1 Kalkulator Inti

- **FR-01** Mendukung operasi tambah, kurang, kali, bagi, persen, tanda kurung, dan pangkat.
- **FR-02** Tombol angka 0–9, titik/koma desimal, `C` (hapus semua), `CE` (hapus entri), `⌫` (hapus satu karakter), dan `±`.
- **FR-03** Pengguna dapat mengetik ekspresi langsung di kolom input memakai keyboard fisik.
- **FR-04** *Live preview*: hasil sementara tampil di bawah ekspresi saat pengguna mengetik, dan final saat menekan `Enter` atau `=`.
- **FR-05** Penanganan kesalahan yang ramah: pembagian dengan nol, tanda kurung tidak seimbang, dan sintaks tidak valid menampilkan pesan singkat (bukan *crash*) dan tidak menghapus input pengguna.
- **FR-06** Presisi tinggi: memakai `Decimal` atau pustaka sejenis untuk menghindari galat floating-point (contoh: `0.1 + 0.2 = 0.3`).
- **FR-07** Format angka dengan pemisah ribuan sesuai pilihan lokal (Indonesia: `1.000.000,5`; Internasional: `1,000,000.5`) dan notasi ilmiah untuk angka sangat besar/kecil.

### 6.2 Fitur Smart

- **FR-08** *Smart expression parser*: memahami kata fungsi (`sqrt`, `sin`, `log`), konstanta (`pi`, `e`), serta perkalian implisit (`2(3+4)` = 14).
- **FR-09** Penghitungan persen kontekstual: `200 + 10%` menghasilkan `220`.
- **FR-10** Variabel `ans` untuk memakai hasil sebelumnya dalam ekspresi baru.
- **FR-11** Riwayat perhitungan: menyimpan ekspresi dan hasil, dapat diklik untuk dipakai ulang, disalin, dihapus satu per satu, atau dibersihkan seluruhnya.
- **FR-12** Memori: MC, MR, M+, M−, dengan indikator `M` saat ada nilai tersimpan.
- **FR-13** Salin hasil (`Ctrl+C` pada hasil atau tombol salin) dan tempel ekspresi (`Ctrl+V`).
- **FR-14** Evaluasi ekspresi dilakukan dengan parser aman, **tidak** memakai `eval()` langsung pada input pengguna.

### 6.3 Mode Kalkulator

- **FR-15** **Standar:** tampilan ringkas dengan tombol dasar.
- **FR-16** **Ilmiah:** menambahkan fungsi trigonometri (derajat/radian), logaritma, akar, pangkat, faktorial, dan konstanta.
- **FR-17** **Konverter Satuan:** panjang, massa, suhu, volume, luas, kecepatan, waktu; konversi dua arah secara langsung.
- **FR-18** **Persentase/Diskon/Pajak:** formulir cepat untuk harga akhir, diskon, dan PPN.
- **FR-19** **Programmer** (opsional): basis HEX/DEC/OCT/BIN dan operasi bitwise.
- **FR-20** Pengguna berpindah mode lewat panel navigasi samping atau menu.

### 6.4 Pengaturan dan Portabilitas

- **FR-21** Pilihan tema: terang, gelap, ikuti sistem.
- **FR-22** Pilihan format angka, jumlah angka desimal, satuan sudut (DEG/RAD), dan bahasa (Indonesia/Inggris).
- **FR-23** Pengaturan dan riwayat disimpan dalam folder `data/` **di samping file `.exe`** (misalnya `settings.json` dan `history.db`) agar benar-benar portable dan tidak menulis ke Registry atau AppData.
- **FR-24** Jika folder tidak dapat ditulis (misalnya pada media *read-only*), aplikasi tetap berjalan tanpa menyimpan riwayat dan memberi tahu pengguna.
- **FR-25** Posisi dan ukuran jendela terakhir diingat.
- **FR-26** Opsi *Always on top*.

### 6.5 Pintasan Keyboard

| Pintasan | Fungsi |
| --- | --- |
| `Enter` atau `=` | Hitung |
| `Esc` | Hapus entri (CE) |
| `Ctrl + Backspace` atau `Delete` | Hapus semua (C) |
| `Ctrl + C` | Salin hasil |
| `Ctrl + V` | Tempel ke input |
| `Ctrl + H` | Tampilkan/sembunyikan riwayat |
| `Ctrl + T` | Ganti tema |
| `Ctrl + 1 / 2 / 3` | Pindah mode (Standar / Ilmiah / Konverter) |
| `↑ / ↓` | Telusuri riwayat |

## 7. Desain UI/UX

### 7.1 Prinsip Desain

- **Minimalis:** Hanya elemen yang diperlukan; ruang kosong cukup; satu fokus utama yaitu layar hasil.
- **Menarik:** Warna aksen konsisten, sudut membulat, transisi halus, tipografi tegas.
- **Responsif:** Tata letak menyesuaikan ukuran jendela.
- **Dapat diakses:** Kontras tinggi, tombol besar, mudah dipakai dengan keyboard maupun mouse.

### 7.2 Palet Warna (usulan)

| Peran | Mode Terang | Mode Gelap |
| --- | --- | --- |
| Latar jendela | `#F5F6F8` | `#16181D` |
| Panel/Layar | `#FFFFFF` | `#1F232B` |
| Tombol angka | `#FFFFFF` | `#2A2F3A` |
| Tombol operator | `#E8ECF5` | `#343B49` |
| Tombol aksi utama (`=`) | `#4F6BED` | `#6C86FF` |
| Teks utama | `#1B1E25` | `#F2F4F8` |
| Teks sekunder | `#6A7180` | `#9AA3B2` |
| Kesalahan | `#D64545` | `#FF7A7A` |

### 7.3 Tipografi dan Bentuk

- Font antarmuka: **Segoe UI Variable** atau **Inter**; angka pada layar hasil memakai font *tabular* agar rapi (misalnya **JetBrains Mono** atau **Cascadia Mono**).
- Ukuran: ekspresi 16–20 pt, hasil 36–48 pt (mengecil otomatis jika angka panjang), tombol 14–18 pt.
- Radius sudut tombol 10–14 px, panel 16 px.
- Efek hover dan tekan yang halus pada tombol (perubahan warna 120 ms).

### 7.4 Tata Letak Layar Utama

```text
+--------------------------------------------------------------+
|  ☰  Arther Smart Application Calculator        ☼/☾   📌   |
+---------+----------------------------------+-----------------+
| Standar |  15% * 2.500.000 + sqrt(144)     |   RIWAYAT       |
| Ilmiah  |                         375.012  |  ---------------|
| Konv.   |  [MC][MR][M+][M-]                |  2+2 = 4        |
| Persen  |  [ C ][ CE][ ⌫ ][ ÷ ]            |  sqrt(9) = 3    |
|         |  [ 7 ][ 8 ][ 9 ][ × ]            |  ...            |
| Setelan |  [ 4 ][ 5 ][ 6 ][ - ]            |  [Bersihkan]    |
|         |  [ 1 ][ 2 ][ 3 ][ + ]            |                 |
|         |  [ ± ][ 0 ][ , ][ = ]            |                 |
+---------+----------------------------------+-----------------+
```

### 7.5 Perilaku Responsif

| Lebar Jendela | Perilaku |
| --- | --- |
| ≥ 1000 px | Panel navigasi, kalkulator, dan riwayat tampil bersamaan. |
| 700–999 px | Riwayat berubah menjadi panel yang bisa dibuka/ditutup (*drawer*). |
| < 700 px | Navigasi menjadi ikon saja; tata letak vertikal ringkas. |
| Ukuran minimum | 360 × 560 px. |

Tombol dan font diskalakan proporsional; layar hasil otomatis mengecilkan ukuran huruf agar angka panjang tetap terbaca. Aplikasi mendukung layar DPI tinggi (*High DPI*) dan skala tampilan Windows (100–200%).

### 7.6 Interaksi dan Animasi

- Transisi antar mode dengan *fade* 150–200 ms.
- Riwayat baru muncul dengan animasi geser lembut.
- Tombol memberi umpan balik visual saat ditekan; kesalahan ditandai dengan efek goyang kecil dan teks berwarna.
- Indikator kedipan kursor pada kolom input.

### 7.7 Alur Utama (User Flow)

**Perhitungan cepat:**\
Buka `.exe` → kursor langsung aktif di kolom input → ketik ekspresi → hasil sementara muncul → tekan `Enter` → hasil final tampil dan masuk ke riwayat.

**Memakai ulang dari riwayat:**\
Tekan `Ctrl+H` → pilih riwayat → ekspresi terisi di input → ubah sesuai kebutuhan → hitung ulang.

**Konversi satuan:**\
Pilih Konverter → pilih kategori (misalnya Panjang) → isi nilai → hasil di satuan lain terhitung otomatis.

## 8. Tech Stack

| Komponen | Pilihan |
| --- | --- |
| Bahasa | Python 3.11+ |
| Pustaka GUI | **CustomTkinter** (ringan dan modern, mudah dipelajari). Alternatif: **PySide6/Qt** untuk UI lebih kaya dan responsif |
| Parser ekspresi | Parser berbasis modul `ast` yang dibatasi, atau pustaka `simpleeval`; hindari `eval()` mentah |
| Presisi angka | `decimal.Decimal` dan modul `math` |
| Penyimpanan | `sqlite3` (riwayat) dan `json` (pengaturan), disimpan di folder `data/` samping `.exe` |
| Pengemasan | **PyInstaller** dengan opsi `--onefile --windowed --icon` |
| Pengujian | `pytest` |
| Kualitas kode | `ruff` / `flake8`, `black`, *type hints* |
| Kontrol versi | Git |

### Struktur Folder (usulan)

```text
arther-calculator/
├── src/
│   ├── main.py            # titik masuk aplikasi
│   ├── core/
│   │   ├── parser.py      # parser dan evaluator ekspresi
│   │   ├── converter.py   # konversi satuan
│   │   └── formatter.py   # format angka
│   ├── storage/
│   │   ├── settings.py
│   │   └── history.py
│   ├── ui/
│   │   ├── app_window.py
│   │   ├── widgets/       # tombol, layar, panel riwayat
│   │   └── themes.py
│   └── utils/paths.py     # penentu path portable
├── assets/                # ikon dan font
├── tests/
├── requirements.txt
└── build.spec             # konfigurasi PyInstaller
```

## 9. Pengemasan dan Distribusi (Portable `.exe`)

1. Kembangkan dan uji di virtual environment (`venv`).
2. Bangun dengan PyInstaller, contoh perintah:

```bash
pyinstaller --onefile --windowed --name "ArtherSmartCalculator" --icon assets/icon.ico src/main.py
```

3. Gunakan fungsi pencari path yang membedakan mode skrip dan mode `.exe` (`sys.frozen` / `sys._MEIPASS`) untuk aset, sedangkan data pengguna selalu ditulis di folder samping `.exe` (`Path(sys.executable).parent / "data"`).
4. Uji `.exe` pada komputer Windows lain yang belum terpasang Python.
5. Uji tambahan: jalankan dari flashdisk dan dari folder dengan spasi pada nama.
6. Catatan: beberapa antivirus dapat memberi *false positive* pada hasil PyInstaller `--onefile`. Mitigasi: gunakan versi terbaru PyInstaller, bangun dari lingkungan bersih, atau tawarkan juga versi `--onedir` dalam bentuk ZIP. Untuk rilis publik, pertimbangkan penandatanganan kode (*code signing*).

## 10. Non-Functional Requirements

| Kategori | Persyaratan |
| --- | --- |
| Performa | Cold start ≤ 3 detik; tidak ada jeda terasa saat mengetik. |
| Keandalan | Tidak crash karena input tidak valid; seluruh kesalahan ditangkap dan ditampilkan ramah. |
| Keamanan | Tidak memakai `eval()` langsung, membatasi panjang ekspresi dan ukuran pangkat/faktorial agar tidak membekukan aplikasi. |
| Privasi | Tidak ada koneksi internet, tidak ada telemetri; semua data lokal. |
| Kompatibilitas | Windows 10 dan 11 (64-bit), mendukung High DPI. |
| Portabilitas | Tanpa instalasi, tanpa Registry, data di folder yang sama dengan `.exe`. |
| Aksesibilitas | Kontras WCAG AA, dapat dioperasikan penuh dengan keyboard, ukuran font dapat diperbesar. |
| Lokalisasi | Bahasa Indonesia dan Inggris, format angka dapat diatur. |
| Pemeliharaan | Kode modular, *type hints*, cakupan uji unit ≥ 80% pada modul `core`. |

## 11. Model Data

```sql
-- history.db
CREATE TABLE history (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  expression  TEXT NOT NULL,
  result      TEXT NOT NULL,
  mode        TEXT NOT NULL DEFAULT 'standard',
  created_at  INTEGER NOT NULL   -- epoch detik
);
CREATE INDEX idx_history_created ON history(created_at DESC);
```

```json
// settings.json
{
  "theme": "system",
  "language": "id",
  "number_format": "id",
  "decimal_places": 10,
  "angle_unit": "deg",
  "always_on_top": false,
  "window": { "x": 120, "y": 80, "width": 900, "height": 640 },
  "history_limit": 500
}
```

## 12. Scope

### In-Scope (MVP)

- Kalkulator standar dan ilmiah dengan input keyboard dan tombol
- *Live preview* hasil dan parser ekspresi aman
- Riwayat dan memori
- Tema terang/gelap dan tata letak responsif
- Konverter satuan dasar
- Penyimpanan pengaturan dan riwayat secara portable
- Pengemasan `.exe` untuk Windows

### Out-of-Scope (Versi Berikutnya)

- Grafik fungsi (*graphing*) dan penyelesaian persamaan simbolik
- Konversi mata uang *real-time* (membutuhkan internet)
- Sinkronisasi cloud
- Versi macOS dan Linux (kode disiapkan, tetapi tidak diuji)
- *Installer* (`.msi`) dan pembaruan otomatis
- Perintah suara

## 13. Asumsi, Dependensi, dan Risiko

### Asumsi

- Pengguna memakai Windows 10/11 64-bit dan dapat menjalankan file `.exe` biasa.
- Pengguna memiliki izin menulis di folder tempat aplikasi diletakkan (jika tidak, riwayat dinonaktifkan).

### Dependensi

- Python 3.11+, CustomTkinter (atau PySide6), PyInstaller.
- Font Inter/JetBrains Mono (disertakan bila lisensinya memperbolehkan) atau font bawaan Windows sebagai cadangan.

### Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Antivirus menandai `.exe` PyInstaller | Pengguna ragu menjalankan aplikasi | Bangun dari lingkungan bersih, sediakan versi `--onedir`, pertimbangkan code signing |
| Start-up `--onefile` lambat karena ekstraksi | Pengalaman awal kurang baik | Kurangi dependensi, gunakan `--onedir` bila perlu, tambahkan splash ringan |
| Tampilan buram pada layar High DPI | UI kurang tajam | Aktifkan *DPI awareness*, uji pada skala 125%–200% |
| Galat floating-point | Hasil hitung tidak akurat | Gunakan `Decimal`, tambahkan uji kasus presisi |
| Input berbahaya atau sangat berat (misalnya `9**9**9`) | Aplikasi membeku | Batasi pangkat, faktorial, dan panjang ekspresi; jalankan evaluasi dengan batas waktu |
| Ukuran `.exe` membengkak | Sulit dibagikan | Hindari pustaka besar yang tidak dipakai, gunakan UPX bila aman |
| Kerumitan UI responsif pada Tkinter | Tampilan tidak rapi | Gunakan tata letak `grid` dengan bobot, atau pertimbangkan PySide6 |

## 14. Timeline dan Milestone (Usulan untuk Belajar)

| Fase | Durasi | Hasil |
| --- | --- | --- |
| 1. Persiapan | Minggu 1 | Setup proyek dan venv, struktur folder, desain di Figma, pemilihan pustaka GUI |
| 2. Logika inti | Minggu 2 | Parser ekspresi, evaluator aman, format angka, uji unit |
| 3. UI dasar | Minggu 3 | Jendela utama, tombol, layar hasil, input keyboard, tema |
| 4. Fitur smart | Minggu 4–5 | Live preview, riwayat (SQLite), memori, mode ilmiah |
| 5. Fitur tambahan | Minggu 6 | Konverter satuan, persen/diskon, pengaturan, tata letak responsif |
| 6. Pengemasan dan uji | Minggu 7 | Build `.exe`, uji portabilitas dan High DPI, perbaikan bug |
| 7. Rilis | Minggu 8 | Dokumentasi, rilis versi 1.0 |

## 15. Acceptance Criteria

- **AC-01** `ArtherSmartCalculator.exe` berjalan di Windows 10/11 yang belum terpasang Python, tanpa instalasi.
- **AC-02** Ekspresi `0.1 + 0.2` menghasilkan `0.3` dan `2(3+4)` menghasilkan `14`.
- **AC-03** Hasil sementara muncul saat mengetik dan menjadi hasil final setelah menekan `Enter`.
- **AC-04** Pembagian dengan nol dan sintaks salah menampilkan pesan kesalahan tanpa menutup aplikasi.
- **AC-05** Riwayat tetap ada setelah aplikasi ditutup dan dibuka kembali, serta tersimpan di folder `data/` samping `.exe`.
- **AC-06** Memindahkan folder aplikasi ke lokasi lain (misalnya flashdisk) tetap membawa pengaturan dan riwayat.
- **AC-07** Mengubah ukuran jendela dari 1200 px sampai 360 px membuat tata letak menyesuaikan tanpa elemen terpotong.
- **AC-08** Pergantian tema terang/gelap langsung berlaku dan tersimpan.
- **AC-09** Seluruh fungsi utama dapat dioperasikan hanya dengan keyboard.
- **AC-10** Ekspresi ekstrem seperti `9**9**9` ditolak atau dibatasi dengan pesan jelas, aplikasi tidak membeku.
- **AC-11** Konversi 1 km ke meter menghasilkan 1000 m dan konversi dua arah konsisten.

## 16. Open Questions

1. CustomTkinter (lebih sederhana) atau PySide6 (lebih kaya fitur dan responsif)?
2. Apakah mode Programmer masuk MVP atau ditunda?
3. Apakah rilis berupa satu `.exe` (`--onefile`) atau ZIP `--onedir` yang lebih cepat dibuka?
4. Apakah perlu bahasa Inggris sejak MVP atau cukup Bahasa Indonesia dahulu?
5. Apakah perlu *code signing* untuk distribusi publik?

## 17. Riwayat Revisi

| Versi | Tanggal | Penulis | Perubahan |
| --- | --- | --- | --- |
| 1.0 | 16 Okt 2026 | Claude | Draft awal PRD |
