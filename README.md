# Kinh Thien Van Thong Minh (STEM)

Ung dung Streamlit ho tro quan sat thien van theo thoi gian thuc, co ban do sao, planner quan sat dem, tong quan du lieu va STEM Lab.

## 1) Cau truc du an

```text
du an stem/
├─ app_balatro.py          # Entrypoint Streamlit
├─ requirements.txt        # Dependencies chuan deploy
├─ core/
│  ├─ constants.py         # Cau hinh/hang so chung
│  ├─ astronomy.py         # Engine tinh toan + cache
│  └─ storage.py           # Doc/ghi profile local
├─ data/
│  └─ catalog.py           # Co so du lieu thien the + fun facts
└─ ui/
   ├─ theme.py             # Theme/CSS
   └─ charts.py            # Ve bieu do/ban do sao
```

## 2) Chay local

Yeu cau: Python 3.10+

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app_balatro.py
```

Neu dung PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app_balatro.py
```

## 3) Deploy len Streamlit Community Cloud

### Buoc A - Day code len GitHub
1. Tao repo GitHub moi.
2. Push toan bo source len nhanh `main`.
3. Dam bao trong root co:
   - `app_balatro.py`
   - `requirements.txt`

### Buoc B - Tao app tren Streamlit Cloud
1. Vao [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in bang GitHub.
3. Chon **New app**.
4. Chon:
   - **Repository**: repo cua ban
   - **Branch**: `main`
   - **Main file path**: `app_balatro.py`
5. Bam **Deploy**.

### Buoc C - Khi update code
- Chi can push commit moi len `main`, Streamlit se tu redeploy.

## 4) Luu y van hanh

- File `observer_profiles.json` la du lieu local tren server (ephemeral), co the reset khi app restart/migrate.
- Nếu can luu profile ben vung, nen dung database nhe (Supabase/Firebase/SQLite managed storage).
- Lan dau app co the tai ephemeris cham hon do can cache du lieu thien van.

## 5) Troubleshooting nhanh

- Loi thieu thu vien: chay lai `pip install -r requirements.txt`
- Loi import `openpyxl`: dam bao dang dung file `requirements.txt` (khong dung `requirements.txt.txt`)
- App load cham: giam `Khung du bao` hoac tang `Buoc lap ke hoach`

## 6) Roadmap tiep

- Tach them `core/planner.py`, `ui/pages/*`
- Them unit tests cho `core/astronomy.py`
- Them CI GitHub Actions de check lint + smoke run
