import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

BASE_URL = "https://api.jolpi.ca/ergast/f1/"
HEADERS = {"User-Agent": "JadwalF1App/1.0"}
ZONA_LOKAL = ZoneInfo("Asia/Jakarta")
NAMA_ZONA = "WIB"

BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}


def ambil_jadwal(tahun):
    url = f"{BASE_URL}{tahun}/races.json?limit=100"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data["MRData"]["RaceTable"]["Races"]


def parse_datetime(date_str, time_str):
    if not date_str:
        return None
    if time_str:
        dt = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H:%M:%SZ")
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return dt


def format_tanggal_id(dt):
    if dt is None:
        return "-"
    dt_lokal = dt.astimezone(ZONA_LOKAL)
    return f"{dt_lokal.day:02d} {BULAN_ID[dt_lokal.month]} {dt_lokal.year}, {dt_lokal.strftime('%H:%M')} {NAMA_ZONA}"


def kumpulkan_semua_jadwal():
    tahun_sekarang = datetime.now(timezone.utc).year
    tahun_target = [tahun_sekarang - 1, tahun_sekarang]
    semua_race = []
    for tahun in tahun_target:
        try:
            races = ambil_jadwal(tahun)
        except requests.exceptions.RequestException:
            continue
        for r in races:
            sesi = {}
            for key, label in [
                ("FirstPractice", "FP1"),
                ("SecondPractice", "FP2"),
                ("ThirdPractice", "FP3"),
                ("SprintQualifying", "Sprint Qualifying"),
                ("Sprint", "Sprint"),
                ("Qualifying", "Kualifikasi"),
            ]:
                if key in r:
                    sesi[label] = parse_datetime(r[key].get("date"), r[key].get("time"))

            race_dt = parse_datetime(r.get("date"), r.get("time"))
            semua_race.append({
                "season": r["season"],
                "round": int(r["round"]),
                "nama": r["raceName"],
                "sirkuit": r["Circuit"]["circuitName"],
                "lokasi": r["Circuit"]["Location"]["locality"],
                "negara": r["Circuit"]["Location"]["country"],
                "tanggal_balapan": race_dt,
                "sesi": sesi,
                "url": r.get("url", "")
            })
    semua_race.sort(key=lambda x: (x["tanggal_balapan"] is None, x["tanggal_balapan"]))
    return semua_race


def tampilkan_ringkas(daftar_race):
    sekarang = datetime.now(timezone.utc)
    musim_terakhir = None
    print("\n" + "=" * 78)
    print("            JADWAL FORMULA 1 — TAHUN LALU s.d. SEKARANG")
    print("=" * 78)
    for race in daftar_race:
        if race["season"] != musim_terakhir:
            musim_terakhir = race["season"]
            print(f"\n--- MUSIM {musim_terakhir} ---")
        status = ""
        if race["tanggal_balapan"]:
            if race["tanggal_balapan"] < sekarang:
                status = "[SELESAI]"
            else:
                status = "[MENDATANG]"
        print(f"R{race['round']:<3} {race['nama']:<32} {race['lokasi']}, {race['negara']:<15} "
              f"{format_tanggal_id(race['tanggal_balapan']):<28} {status}")


def tampilkan_detail(race):
    print("\n" + "=" * 60)
    print(f"{race['nama']} — Musim {race['season']}, Ronde {race['round']}")
    print("=" * 60)
    print(f"Sirkuit  : {race['sirkuit']}")
    print(f"Lokasi   : {race['lokasi']}, {race['negara']}")
    print(f"Balapan  : {format_tanggal_id(race['tanggal_balapan'])}")
    if race["sesi"]:
        print("-" * 60)
        print("Jadwal Sesi:")
        for label, dt in race["sesi"].items():
            print(f"  {label:<20}: {format_tanggal_id(dt)}")
    if race["url"]:
        print("-" * 60)
        print(f"Info lebih lanjut: {race['url']}")
    print(f"Cek/bandingkan dengan situs resmi: https://www.formula1.com/en/racing/{race['season']}")
    print("=" * 60)


def cari_balapan_berikutnya(daftar_race):
    sekarang = datetime.now(timezone.utc)
    mendatang = [r for r in daftar_race if r["tanggal_balapan"] and r["tanggal_balapan"] >= sekarang]
    return mendatang[0] if mendatang else None


def ambil_hasil_musim(tahun):
    url = f"{BASE_URL}{tahun}/results.json?limit=1000"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data["MRData"]["RaceTable"]["Races"]


def ambil_klasemen_pembalap(tahun):
    url = f"{BASE_URL}{tahun}/driverStandings.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    lists = data["MRData"]["StandingsTable"]["StandingsLists"]
    return lists[0]["DriverStandings"] if lists else []


def ambil_klasemen_konstruktor(tahun):
    url = f"{BASE_URL}{tahun}/constructorStandings.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    lists = data["MRData"]["StandingsTable"]["StandingsLists"]
    return lists[0]["ConstructorStandings"] if lists else []


def tampilkan_hasil_musim(races):
    if not races:
        print("Belum ada hasil balapan untuk musim ini.")
        return
    print("\n" + "=" * 90)
    print(f"           HASIL BALAPAN F1 MUSIM {races[0]['season']}")
    print("=" * 90)
    for race in races:
        print(f"\nRonde {race['round']} — {race['raceName']} ({race['Circuit']['Location']['country']})")
        print("-" * 90)
        print(f"{'Pos':<5}{'Pembalap':<25}{'Tim':<25}{'Poin':<8}{'Status'}")
        for r in race["Results"]:
            nama = f"{r['Driver']['givenName']} {r['Driver']['familyName']}"
            tim = r["Constructor"]["name"]
            print(f"{r['positionText']:<5}{nama:<25}{tim:<25}{r['points']:<8}{r['status']}")


def tampilkan_hasil_ronde(races, ronde):
    race = next((r for r in races if str(r["round"]) == str(ronde)), None)
    if not race:
        print("Ronde tidak ditemukan.")
        return
    print("\n" + "=" * 90)
    print(f"{race['raceName']} — Musim {race['season']}, Ronde {race['round']}")
    print(f"Sirkuit: {race['Circuit']['circuitName']}, {race['Circuit']['Location']['locality']}, "
          f"{race['Circuit']['Location']['country']}")
    print("=" * 90)
    print(f"{'Pos':<5}{'No':<5}{'Pembalap':<25}{'Tim':<25}{'Poin':<7}{'Waktu/Status'}")
    for r in race["Results"]:
        nama = f"{r['Driver']['givenName']} {r['Driver']['familyName']}"
        tim = r["Constructor"]["name"]
        waktu = r.get("Time", {}).get("time", r["status"])
        print(f"{r['positionText']:<5}{r['number']:<5}{nama:<25}{tim:<25}{r['points']:<7}{waktu}")
    print(f"Cek/bandingkan dengan situs resmi: https://www.formula1.com/en/racing/{race['season']}")
    print("=" * 90)


def tampilkan_klasemen_pembalap(standings, tahun):
    if not standings:
        print("Klasemen pembalap belum tersedia untuk musim ini.")
        return
    print("\n" + "=" * 75)
    print(f"           KLASEMEN PEMBALAP F1 MUSIM {tahun}")
    print("=" * 75)
    print(f"{'Pos':<5}{'Pembalap':<25}{'Tim':<25}{'Poin':<8}{'Menang'}")
    for s in standings:
        nama = f"{s['Driver']['givenName']} {s['Driver']['familyName']}"
        tim = s["Constructors"][0]["name"] if s["Constructors"] else "-"
        print(f"{s['position']:<5}{nama:<25}{tim:<25}{s['points']:<8}{s['wins']}")
    print("=" * 75)


def tampilkan_klasemen_konstruktor(standings, tahun):
    if not standings:
        print("Klasemen konstruktor belum tersedia untuk musim ini.")
        return
    print("\n" + "=" * 60)
    print(f"           KLASEMEN KONSTRUKTOR F1 MUSIM {tahun}")
    print("=" * 60)
    print(f"{'Pos':<5}{'Tim':<30}{'Poin':<8}{'Menang'}")
    for s in standings:
        print(f"{s['position']:<5}{s['Constructor']['name']:<30}{s['points']:<8}{s['wins']}")
    print("=" * 60)


def menu():
    tahun_ini = datetime.now(timezone.utc).year

    print("Mengambil data jadwal F1 terbaru...")
    daftar_race = kumpulkan_semua_jadwal()

    if not daftar_race:
        print("Gagal mengambil data. Periksa koneksi internet Anda.")
        return

    hasil_musim_ini = None
    klasemen_pembalap = None
    klasemen_konstruktor = None

    while True:
        print(f"""
============================================
        JADWAL & HASIL F1 (LIVE DATA)
============================================
1. Tampilkan semua jadwal (tahun lalu - sekarang)
2. Tampilkan detail satu balapan (jadwal)
3. Tampilkan balapan berikutnya
4. Hasil semua balapan musim {tahun_ini}
5. Hasil satu balapan (per ronde) musim {tahun_ini}
6. Klasemen pembalap musim {tahun_ini}
7. Klasemen konstruktor musim {tahun_ini}
8. Refresh seluruh data dari server
0. Keluar
============================================
""")
        pilihan = input("Pilih menu (0-8): ").strip()

        if pilihan == "1":
            tampilkan_ringkas(daftar_race)

        elif pilihan == "2":
            musim = input("Masukkan musim (contoh 2026): ").strip()
            ronde = input("Masukkan nomor ronde: ").strip()
            found = next((r for r in daftar_race if str(r["season"]) == musim and str(r["round"]) == ronde), None)
            if found:
                tampilkan_detail(found)
            else:
                print("Data balapan tidak ditemukan.")

        elif pilihan == "3":
            next_race = cari_balapan_berikutnya(daftar_race)
            if next_race:
                tampilkan_detail(next_race)
            else:
                print("Tidak ada balapan mendatang yang terjadwal saat ini.")

        elif pilihan == "4":
            if hasil_musim_ini is None:
                print("Mengambil hasil balapan terbaru...")
                hasil_musim_ini = ambil_hasil_musim(tahun_ini)
            tampilkan_hasil_musim(hasil_musim_ini)

        elif pilihan == "5":
            if hasil_musim_ini is None:
                print("Mengambil hasil balapan terbaru...")
                hasil_musim_ini = ambil_hasil_musim(tahun_ini)
            ronde = input("Masukkan nomor ronde: ").strip()
            tampilkan_hasil_ronde(hasil_musim_ini, ronde)

        elif pilihan == "6":
            print("Mengambil klasemen pembalap terbaru...")
            klasemen_pembalap = ambil_klasemen_pembalap(tahun_ini)
            tampilkan_klasemen_pembalap(klasemen_pembalap, tahun_ini)

        elif pilihan == "7":
            print("Mengambil klasemen konstruktor terbaru...")
            klasemen_konstruktor = ambil_klasemen_konstruktor(tahun_ini)
            tampilkan_klasemen_konstruktor(klasemen_konstruktor, tahun_ini)

        elif pilihan == "8":
            print("Mengambil ulang seluruh data dari server...")
            daftar_race = kumpulkan_semua_jadwal()
            hasil_musim_ini = None
            klasemen_pembalap = None
            klasemen_konstruktor = None
            print("Data berhasil diperbarui.")

        elif pilihan == "0":
            print("Sampai jumpa!")
            break

        else:
            print("Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    menu()