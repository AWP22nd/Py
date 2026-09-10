import sqlite3
from datetime import datetime
import os

DB_NAME = "finance.db"


class FinanceManager:
    def __init__(self, db_name=DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transaksi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT NOT NULL,
                    jenis TEXT NOT NULL CHECK(jenis IN ('pemasukan', 'pengeluaran')),
                    kategori TEXT NOT NULL,
                    jumlah REAL NOT NULL,
                    keterangan TEXT
                )
            """)

    def tambah_transaksi(self, jenis, kategori, jumlah, keterangan=""):
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute(
                "INSERT INTO transaksi (tanggal, jenis, kategori, jumlah, keterangan) VALUES (?, ?, ?, ?, ?)",
                (tanggal, jenis, kategori, jumlah, keterangan)
            )
        print("✅ Transaksi berhasil ditambahkan!")

    def ambil_semua(self, kategori=None, bulan=None):
        query = "SELECT * FROM transaksi WHERE 1=1"
        params = []
        if kategori:
            query += " AND kategori LIKE ?"
            params.append(f"%{kategori}%")
        if bulan:
            query += " AND strftime('%Y-%m', tanggal) = ?"
            params.append(bulan)
        query += " ORDER BY tanggal DESC"
        cur = self.conn.execute(query, params)
        return cur.fetchall()

    def tampilkan_transaksi(self, data):
        if not data:
            print("Tidak ada data transaksi.")
            return
        print(f"\n{'ID':<4}{'Tanggal':<18}{'Jenis':<13}{'Kategori':<15}{'Jumlah':>12}  Keterangan")
        print("-" * 80)
        for row in data:
            id_, tanggal, jenis, kategori, jumlah, ket = row
            tanda = "+" if jenis == "pemasukan" else "-"
            print(f"{id_:<4}{tanggal:<18}{jenis:<13}{kategori:<15}{tanda}{jumlah:>10,.0f}  {ket or ''}")

    def edit_transaksi(self, id_, kategori=None, jumlah=None, keterangan=None):
        row = self.conn.execute("SELECT * FROM transaksi WHERE id=?", (id_,)).fetchone()
        if not row:
            print("❌ ID tidak ditemukan.")
            return
        kategori = kategori or row[3]
        jumlah = jumlah if jumlah is not None else row[4]
        keterangan = keterangan if keterangan is not None else row[5]
        with self.conn:
            self.conn.execute(
                "UPDATE transaksi SET kategori=?, jumlah=?, keterangan=? WHERE id=?",
                (kategori, jumlah, keterangan, id_)
            )
        print("✅ Transaksi berhasil diperbarui!")

    def hapus_transaksi(self, id_):
        with self.conn:
            cur = self.conn.execute("DELETE FROM transaksi WHERE id=?", (id_,))
        if cur.rowcount:
            print("🗑️  Transaksi dihapus.")
        else:
            print("❌ ID tidak ditemukan.")

    def ringkasan(self):
        pemasukan = self.conn.execute(
            "SELECT COALESCE(SUM(jumlah),0) FROM transaksi WHERE jenis='pemasukan'"
        ).fetchone()[0]
        pengeluaran = self.conn.execute(
            "SELECT COALESCE(SUM(jumlah),0) FROM transaksi WHERE jenis='pengeluaran'"
        ).fetchone()[0]
        saldo = pemasukan - pengeluaran
        return pemasukan, pengeluaran, saldo

    def laporan_kategori(self):
        cur = self.conn.execute("""
            SELECT kategori, jenis, SUM(jumlah) FROM transaksi
            GROUP BY kategori, jenis
            ORDER BY jenis, SUM(jumlah) DESC
        """)
        return cur.fetchall()

    def cetak_laporan(self, ke_file=False):
        pemasukan, pengeluaran, saldo = self.ringkasan()
        lines = []
        lines.append("=" * 45)
        lines.append("     LAPORAN KEUANGAN PRIBADI")
        lines.append("=" * 45)
        lines.append(f"Total Pemasukan   : Rp {pemasukan:,.0f}")
        lines.append(f"Total Pengeluaran : Rp {pengeluaran:,.0f}")
        lines.append(f"Saldo Akhir       : Rp {saldo:,.0f}")
        lines.append("-" * 45)
        lines.append("Rincian per Kategori:")

        data = self.laporan_kategori()
        max_val = max((jml for _, _, jml in data), default=1)
        for kategori, jenis, jml in data:
            bar_len = int((jml / max_val) * 25) if max_val else 0
            bar = "█" * bar_len
            simbol = "+" if jenis == "pemasukan" else "-"
            lines.append(f"{kategori:<12} ({jenis:<11}) {simbol}Rp{jml:>10,.0f}  {bar}")
        lines.append("=" * 45)

        laporan_text = "\n".join(lines)
        print("\n" + laporan_text)

        if ke_file:
            nama_file = f"laporan_keuangan_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(nama_file, "w", encoding="utf-8") as f:
                f.write(laporan_text)
            print(f"\n📄 Laporan diekspor ke: {os.path.abspath(nama_file)}")

    def close(self):
        self.conn.close()


def input_angka(prompt):
    while True:
        try:
            return float(input(prompt).replace(",", ""))
        except ValueError:
            print("⚠️  Masukkan angka yang valid.")


def input_id(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("⚠️  Masukkan ID berupa angka.")


def menu():
    fm = FinanceManager()
    menu_text = """
============================================
   APLIKASI PENGELOLA KEUANGAN PRIBADI
============================================
1. Tambah Pemasukan
2. Tambah Pengeluaran
3. Lihat Semua Transaksi
4. Cari Transaksi berdasarkan Kategori
5. Edit Transaksi
6. Hapus Transaksi
7. Lihat Ringkasan & Laporan
8. Ekspor Laporan ke File
0. Keluar
============================================
"""
    while True:
        print(menu_text)
        pilihan = input("Pilih menu (0-8): ").strip()

        if pilihan == "1":
            kategori = input("Kategori (misal: Gaji, Bonus): ").strip()
            jumlah = input_angka("Jumlah: Rp ")
            ket = input("Keterangan (opsional): ").strip()
            fm.tambah_transaksi("pemasukan", kategori, jumlah, ket)

        elif pilihan == "2":
            kategori = input("Kategori (misal: Makan, Transport): ").strip()
            jumlah = input_angka("Jumlah: Rp ")
            ket = input("Keterangan (opsional): ").strip()
            fm.tambah_transaksi("pengeluaran", kategori, jumlah, ket)

        elif pilihan == "3":
            data = fm.ambil_semua()
            fm.tampilkan_transaksi(data)

        elif pilihan == "4":
            kata_kunci = input("Masukkan nama kategori: ").strip()
            data = fm.ambil_semua(kategori=kata_kunci)
            fm.tampilkan_transaksi(data)

        elif pilihan == "5":
            id_ = input_id("ID transaksi yang ingin diedit: ")
            kategori = input("Kategori baru (kosongkan jika tidak diubah): ").strip() or None
            jumlah_str = input("Jumlah baru (kosongkan jika tidak diubah): ").strip()
            jumlah = float(jumlah_str) if jumlah_str else None
            ket = input("Keterangan baru (kosongkan jika tidak diubah): ").strip() or None
            fm.edit_transaksi(id_, kategori, jumlah, ket)

        elif pilihan == "6":
            id_ = input_id("ID transaksi yang ingin dihapus: ")
            fm.hapus_transaksi(id_)

        elif pilihan == "7":
            fm.cetak_laporan(ke_file=False)

        elif pilihan == "8":
            fm.cetak_laporan(ke_file=True)

        elif pilihan == "0":
            print("Terima kasih sudah menggunakan aplikasi ini. Sampai jumpa! 👋")
            fm.close()
            break

        else:
            print("⚠️  Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    menu()