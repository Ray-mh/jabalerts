# Job Radar

Personal alert system: reads job-alert emails (AcademicTransfer / EURAXESS, LinkedIn, Indeed) from a dedicated Gmail inbox, scores every vacancy against my CV with Claude, and

- publishes matches (score ≥ 70) to a three-tab page (PhD · LinkedIn · Indeed) on GitHub Pages,
- sends each match to Telegram, labelled by Dutch-language requirement (🔴 required · 🟡 a plus · 🟢 English only · ⚪ unclear).

Runs every 10 minutes on GitHub Actions. Setup guide (Persian): [SETUP-fa.md](SETUP-fa.md). Settings: `config.json`.
