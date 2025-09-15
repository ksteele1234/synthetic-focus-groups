
# Synthetic Focus Groups — audience research preview

This bundle adds:
- **apps/persona-preview** — Vite + React + TS app (mocked data) with Evidence, Personas, Prompt/Schema, and Bulk Uploads.
- **apps/research-api** — FastAPI stub for wiring Reddit/Quora scraping + LLM persona generation later.
- **spec/** — starter folder for GitHub **Spec Kit** (optional).

## Local dev

Frontend:
```bash
cd apps/persona-preview
npm i
npm run dev
```

Backend (stub):
```bash
cd apps/research-api
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
uvicorn main:app --reload
```

## Put this into your GitHub repo (ksteele1234/synthetic-focus-groups)

Using GitHub CLI (recommended):
```bash
gh repo clone ksteele1234/synthetic-focus-groups
cd synthetic-focus-groups
# unzip the bundle contents into the repo root (overwrites/adds files into apps/ and spec/)
unzip ../synthetic-focus-groups-bundle.zip -d .
git checkout -b feat/audience-research-preview
git add -A
git commit -m "feat: add audience research preview app + FastAPI stub + spec scaffold"
git push -u origin feat/audience-research-preview
gh pr create --fill
```

Using plain git (no gh):
```bash
git clone https://github.com/ksteele1234/synthetic-focus-groups.git
cd synthetic-focus-groups
unzip ../synthetic-focus-groups-bundle.zip -d .
git checkout -b feat/audience-research-preview
git add -A
git commit -m "feat: add audience research preview app + FastAPI stub + spec scaffold"
git push -u origin feat/audience-research-preview
# then open a PR in GitHub UI
```

## Notes
- Node 18+ recommended.
- Tailwind is preconfigured; no extra UI deps required.
- Bulk Uploads supports URLs, raw quotes, and JSON arrays of quote objects (CSV can be added in the backend).
- The App includes the stricter prompt template + JSON schema you approved.
