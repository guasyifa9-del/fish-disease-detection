# 📋 Checklist Pengujian Manual (Black-Box Testing)
## FishDetect — Sistem Deteksi Penyakit Ikan Air Tawar

---

## Skenario 1: Upload Gambar Ikan Sakit (Positif)
| No | Langkah | Hasil yang Diharapkan | Status |
|----|---------|----------------------|--------|
| 1 | Buka halaman `/upload` | Halaman upload tampil dengan drop zone | ☐ |
| 2 | Upload foto ikan yang sakit (JPG/PNG, < 5MB) | Preview gambar muncul, tombol "Deteksi" aktif | ☐ |
| 3 | Klik "Deteksi Penyakit" | Loading spinner tampil "Sedang menganalisis..." | ☐ |
| 4 | Tunggu proses selesai | Redirect ke halaman `/result/<id>` | ☐ |
| 5 | Cek hasil deteksi | Badge merah/kuning muncul + nama penyakit | ☐ |
| 6 | Cek confidence score | Progress bar + persentase tampil (0-100%) | ☐ |
| 7 | Cek info penyakit | Penyebab, gejala, penanganan, pencegahan tampil | ☐ |
| 8 | Cek probabilitas | Bar chart 7 kelas ditampilkan | ☐ |

---

## Skenario 2: Upload Gambar Ikan Sehat (Negatif)
| No | Langkah | Hasil yang Diharapkan | Status |
|----|---------|----------------------|--------|
| 1 | Upload foto ikan yang sehat | Preview gambar muncul | ☐ |
| 2 | Klik "Deteksi Penyakit" | Proses deteksi berjalan | ☐ |
| 3 | Cek hasil | Badge hijau "Ikan Anda dalam kondisi sehat! 🎉" | ☐ |
| 4 | Cek info | Pesan "Tidak ditemukan tanda penyakit" | ☐ |

---

## Skenario 3: Upload File Tidak Valid (Error Handling)
| No | Langkah | Hasil yang Diharapkan | Status |
|----|---------|----------------------|--------|
| 1 | Upload file PDF | Pesan error "Format file tidak didukung" | ☐ |
| 2 | Upload file GIF | Pesan error format file | ☐ |
| 3 | Upload file > 5MB | Pesan error "Ukuran file terlalu besar" | ☐ |
| 4 | Klik deteksi tanpa pilih file | Tombol disabled, tidak bisa klik | ☐ |
| 5 | Upload file .txt rename jadi .jpg | Pesan error MIME type tidak valid | ☐ |

---

## Skenario 4: Navigasi dan Riwayat
| No | Langkah | Hasil yang Diharapkan | Status |
|----|---------|----------------------|--------|
| 1 | Buka halaman `/` | Landing page tampil dengan hero + 7 penyakit | ☐ |
| 2 | Klik "Mulai Deteksi Sekarang" | Redirect ke `/upload` | ☐ |
| 3 | Setelah deteksi, buka `/history` | Riwayat deteksi tampil dalam card list | ☐ |
| 4 | Klik filter "Sakit" | Hanya tampil deteksi yang teridentifikasi sakit | ☐ |
| 5 | Klik filter "Sehat" | Hanya tampil deteksi sehat | ☐ |
| 6 | Klik salah satu kartu riwayat | Redirect ke halaman result deteksi tsb | ☐ |
| 7 | Cek navbar aktif | Link "Beranda" aktif di halaman index, dll | ☐ |

---

## Skenario 5: Info Penyakit
| No | Langkah | Hasil yang Diharapkan | Status |
|----|---------|----------------------|--------|
| 1 | Buka `/disease-info/bacterial_red_disease` | Info lengkap tampil: penyebab, gejala, penanganan | ☐ |
| 2 | Klik penyakit lain di sidebar | Halaman berubah ke penyakit yang dipilih | ☐ |
| 3 | Cek semua 7 penyakit | Masing-masing punya data yang lengkap | ☐ |
| 4 | Cek pada mobile (< 768px) | Sidebar berubah jadi collapsible button | ☐ |
| 5 | Cek ada deteksi terkait | Thumbnail + confidence ditampilkan | ☐ |

---

## Skenario 6: Responsif dan Performa
| No | Langkah | Hasil yang Diharapkan | Status |
|----|---------|----------------------|--------|
| 1 | Buka di HP (viewport 375px) | Layout responsif, tidak overflow | ☐ |
| 2 | Buka di tablet (768px) | Layout 2 kolom menyesuaikan | ☐ |
| 3 | Cek waktu loading halaman | < 3 detik untuk halaman statis | ☐ |
| 4 | Cek waktu deteksi | < 10 detik dari upload sampai result | ☐ |
| 5 | Drag & drop gambar di upload | Gambar ter-preview dengan benar | ☐ |
| 6 | Health check `/health` | JSON response dengan status komponen | ☐ |

---

## Catatan Tester
- **Browser yang diuji:** Chrome / Firefox / Edge
- **Tanggal pengujian:** _______________
- **Nama penguji:** _______________
- **Total test case:** 35
- **Passed:** ___
- **Failed:** ___
