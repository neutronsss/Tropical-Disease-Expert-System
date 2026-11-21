# Tanya Jawab Penyakit Tropis

Aplikasi tanya jawab berbahasa Indonesia yang menampilkan informasi awal berdasarkan relasi dalam ontologi OWL/XML. Aplikasi bukan alat diagnosis, tidak menggunakan model generatif, dan tidak menyimpan jawaban konsultasi.

## Teknologi dan struktur

- FastAPI menyediakan REST API dan menyajikan antarmuka statis.
- Ontologi `.owx` dibaca langsung sebagai XML menggunakan pustaka standar Python; tidak dikonversi atau diubah.
- Antarmuka menggunakan HTML, CSS, dan JavaScript tanpa framework tambahan.

```text
app/
  main.py          # REST API dan penyajian frontend
  ontology.py      # Pemuatan dan ekstraksi OWL/XML
  schemas.py       # Validasi request dan response dengan Pydantic
  services.py      # Pertanyaan dan pencocokan berbasis relasi ontologi
  static/          # HTML, CSS, JavaScript
tests/
  test_app.py      # Pengujian unit dan endpoint
```

## Menjalankan di Windows

Gunakan Python 3.10 atau lebih baru. Dari PowerShell pada direktori repository:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Buka `http://127.0.0.1:8000`. Dokumentasi OpenAPI tersedia di `http://127.0.0.1:8000/docs`.

Untuk memakai ontologi lain yang tetap mengikuti format OWL/XML dan relasi yang diharapkan:

```powershell
$env:ONTOLOGY_PATH = "C:\path\ke\ontologi.owx"
python -m uvicorn app.main:app --reload
```

Jika berkas tidak dapat dimuat, endpoint kesehatan akan melaporkan status `degraded` dan endpoint yang memerlukan ontologi mengembalikan HTTP 503. Detail teknis dicatat pada log layanan.

## REST API

Semua endpoint berada pada prefix `/api`.

### `GET /api/health`

Status layanan, pemuatan ontologi, dan jumlah penyakit.

### `GET /api/questions`

Mengembalikan teks disclaimer, tanda bahaya, gejala, pilihan lingkungan dan musim, serta informasi apakah ontologi mempunyai data waktu kemunculan gejala.

### `GET /api/symptoms`

Mengembalikan daftar ID dan label gejala yang tersedia untuk konsultasi.

### `POST /api/consultations`

Contoh request:

```json
{
  "symptoms": ["DemamTinggi", "NyeriSendi"],
  "danger_signs": [],
  "environment": "GenanganAir",
  "season": "Hujan"
}
```

Semua pilihan selain `symptoms` opsional. `symptoms` dan `danger_signs` berupa daftar ID dari `/api/questions`. Respons berisi pesan tanda bahaya, metode pengurutan, dan daftar penyakit dengan gejala pendukung serta informasi penanganan, rujukan, tindakan yang dihindari, atau sumber hanya jika relasi tersebut terdapat di ontologi. ID yang tidak dikenal ditolak dengan HTTP 422.

Pencocokan mengurutkan penyakit berdasarkan jumlah gejala terpilih yang tercatat dalam ontologi. Bila jumlahnya sama, pilihan lingkungan yang cocok lalu musim yang cocok menjadi pemecah seri. Ini bukan probabilitas, skor risiko, atau ukuran akurasi medis. Pengguna dapat mengisi hari mulai untuk setiap gejala; jika tersedia, nilainya ditampilkan berdampingan dengan `mulaiDirasakanHariKe` dari ontologi dan tidak memengaruhi urutan. Data ini adalah hari mulai per manifestasi gejala, bukan durasi total penyakit.

### `GET /api/diseases/{id}`

Mengembalikan rincian satu penyakit yang ditemukan dalam ontologi. ID yang tidak ditemukan menghasilkan HTTP 404.

## Pengujian

```powershell
python -m unittest discover -s tests -v
```

Pengujian mencakup pemuatan dan ekstraksi ontologi, waktu mulai gejala, endpoint pertanyaan dan kesehatan, pengurutan hasil, tanda bahaya, input tanpa gejala, ID tidak dikenal, penyakit tidak ditemukan, dan penyajian halaman web.

## Batasan dan catatan sumber

- Berkas yang tersedia adalah `Project_Advanced_SROIQ_1_8_2.owx` dalam format OWL/XML; aplikasi memakai parser XML standar Python tanpa mengubahnya.
- Ontologi memuat 21 penyakit, 61 manifestasi gejala, data `mulaiDirasakanHariKe`, 5 pilihan lingkungan, 2 musim, serta 11 relasi tanda bahaya.
- Label antarmuka diturunkan dari ID individu ontologi dengan memisahkan huruf kapital; istilah penyakit tetap mengikuti ID sumber.
- Referensi ditampilkan hanya dari anotasi `sumberRujukan` yang ada pada ontologi. PDF di `REFERENSI` tidak diekstrak atau ditafsirkan aplikasi.
- `inject_ontology.py` menggunakan `Project.owx` dan menulis `Project_Reified.owx`; `inject_annotations.py` membaca `Project_Reified.owx`. Nama-nama itu tidak cocok dengan berkas ontologi yang tersedia. Aplikasi ini tidak menjalankan skrip injeksi.
- Hasil hanya menunjukkan kecocokan relasi dalam basis pengetahuan. Jika ada tanda bahaya, cari pertolongan medis segera; jangan menunggu atau mengandalkan hasil aplikasi.
