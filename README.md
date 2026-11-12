# CEM Prep — Certified Energy Manager Exam Preparation

A Streamlit study application with **1,120 original practice questions across 14 subject areas**. It includes topic practice, configurable exam simulations, calculation tools, a formula library, and performance tracking.

> This is an independent study aid. It is not affiliated with, sponsored by, or endorsed by the Association of Energy Engineers (AEE). Questions are original practice material—not actual or recalled exam questions. Always use the current AEE candidate handbook and Body of Knowledge as the authority for exam requirements and weighting.

## Run locally

Requires Python 3.10 or newer.

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
python -m venv .venv
```

Activate the environment, then install and launch:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**macOS / Linux**
```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed by Streamlit (usually http://localhost:8501).

## Deploy free with Streamlit Community Cloud

1. Create a GitHub repository and upload the contents of this project so `app.py` is in the repository root.
2. Visit [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
3. Select **Create app**, then choose your repository, branch (`main`), and main file path (`app.py`).
4. Select **Deploy**. Streamlit installs packages from `requirements.txt`.
5. After deployment, use the app URL provided by Streamlit. You can optionally configure a custom subdomain in the app settings.

## Repository layout

```text
.
├── .github/
│   └── workflows/             # Lightweight Python syntax/data validation
├── .streamlit/
│   └── config.toml            # App theme and server settings
├── data/
│   ├── questions.json         # Main question bank
│   ├── questions.csv          # Spreadsheet-friendly question bank
│   └── subjects.json          # Subject-area metadata
├── .gitignore
├── app.py                     # Streamlit application entry point
├── LICENSE
└── requirements.txt
```

## Features

- Dashboard and subject-level progress
- Original multiple-choice questions with explanations
- Study/practice mode and configurable exam simulations
- Electrical, HVAC, thermal, energy/demand, and project-economics calculations
- Searchable formula library
- Performance tracking and study notes
- Local SQLite progress database created automatically at runtime

## Data and privacy

The app does not require user accounts. The current version stores attempts and notes in a local SQLite database at `database/progress.db`, which is created automatically. The database is intentionally excluded from Git by `.gitignore`.

**Hosting note:** Streamlit Community Cloud is designed for app deployment, not durable local-disk storage. Local SQLite data may be lost when an instance restarts, is rebuilt, or is moved. Do not rely on this deployment for permanent or multi-user progress storage. A production multi-user version should use a managed database and authentication, with secrets configured through Streamlit's app settings—not committed to GitHub.

## Updating the question bank

- Edit `data/questions.json` for the app's question content.
- Keep `data/questions.csv` synchronized if you want the downloadable/spreadsheet copy to match.
- Preserve each question's existing field structure and unique ID.
- Validate JSON before committing changes.

## License

The source code and original study content in this repository are provided under the MIT License. See [LICENSE](LICENSE). Third-party marks and AEE certification materials remain the property of their respective owners.
