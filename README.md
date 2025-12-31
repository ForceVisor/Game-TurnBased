Game-TurnBased

Game-TurnBased adalah aplikasi permainan edukasi interaktif berbasis Desktop yang menggabungkan keseruan genre _Trading Card Game_ (TCG) dan _Role-Playing Game_ (RPG) dengan latihan mental matematika.
Aplikasi ini dikembangkan menggunakan bahasa pemrograman Python dan library Pygame, dirancang untuk melatih strategi pemain serta interaksi menarik seperti kecepatan berhitung (perkalian) di bawah tekanan permainan.

Fitur Utama

Aplikasi ini memiliki _Main Menu_ terintegrasi yang menghubungkan dua mode permainan utama:

1. Mode PVP (Card Battle Strategy)
Simulasi permainan kartu berbasis giliran (_turn-based_) yang strategis.
  Deck Selection: Pilih satu dari tiga deck unik (Charizard, Pikachu, Blastoise).
  Mekanik Kartu: Manajemen HP, Attack, Defense, dan Energy Cost.
  Fitur "Math Reward": Kuis matematika akan muncul secara berkala.
    -Jawab Benar: Memberikan efek _Healing_ (pemulihan HP) ke seluruh tim.
    -Jawab Salah: Tidak ada bonus yang didapatkan.

2. Mode PVB (RPG Adventure)
  Pertarungan RPG klasik antara Ksatria (_Knight_) melawan Bandit.
  Action System: Pilih antara menyerang (_Attack_) atau menggunakan ramuan (_Potion_).
  Turn-Based Combat: Sistem giliran antara pemain dan musuh (_Bot_).
  Fitur "_Math Penalty_": Kuis matematika muncul sebagai rintangan (peluang 50% atau tiap 4 giliran).
    -Jawab Benar: Permainan berlanjut aman.
    -Jawab Salah/Waktu Habis: Pemain terkena _Direct Damage_ (pengurangan darah signifikan).

3. Sistem Menu & Audio
  Navigasi antarmuka yang intuitif dan interaktif.
  Pengaturan musik latar (_Background Music_) On/Off.
  Transisi mulus antar mode permainan.



_Requirements_

Sebelum menjalankan aplikasi, pastikan komputer Anda telah terinstal:

  Python 3.13.9
  Pygame Library



Cara Instalasi & Menjalankan

1.  Clone Repository ini (atau unduh sebagai ZIP):
    ```bash
    git clone [https://github.com/username-anda/math-battle-hub.git](https://github.com/username-anda/math-battle-hub.git)
    cd Game-TurnBased
    ```

2.  Install Library yang Dibutuhkan:
    Buka terminal/command prompt dan jalankan:
    ```bash
    pip install pygame
    ```

3.  Jalankan Aplikasi:
    Eksekusi file `main.py` yang ada di Menu Pygame untuk membuka menu utama:
    ```bash
    python main.py
    ```

Struktur Folder

Pastikan struktur folder aset Anda sesuai agar gambar dan suara dapat dimuat dengan benar:
├──
```text
Game-TurnBased/
│
├── Menu Pygame/            # Aset untuk Main Menu
|   ├── assetss/            # (Background, font, musik menu, tombol)
|   ├── img/
|   ├── button.py
|   └── main.py
├── pokemon game/           # Aset untuk Mode TCG
|   ├── pocket_tc_assets/   # (Gambar kartu, background, musik battle)
│   └── turn based tcg.py
└── Battle-main/            # Aset untuk Mode RPG
    ├── battle.py
    ├── button.py
    ├── img/                # (Sprite Knight, Bandit, Background)
    ├── sound/              # (Efek suara & musik)
    └── monogram
```

Cara Bermain (_Controls_)
Mouse (Klik Kiri):

  Navigasi menu.
  Memilih kartu/serangan.
  Memilih target musuh.

Keyboard (Numpad/Angka):
  
  Mengetik jawaban saat Kuis Matematika muncul.
  Tekan ENTER untuk mengirim jawaban.
  Tekan BACKSPACE untuk menghapus angka.

Credit Tim

  Ketua Tim: Najwan Farhan Kusuma
  Anggota: Ignatius Geovand Taolin

Catatan untuk Pengguna: 
  Pastikan folder aset (Menu Pygame, pokemon game, Battle-main) berada dalam satu direktori yang sama dengan file .py agar tidak terjadi error file not found




