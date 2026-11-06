# 🕊️ The Kingdom Journal: Daily Gospel Content Automation

> An institutional, automated system that discovers proven-viral gospel ministrations on YouTube, extracts and verifies real spoken punchlines, composites scroll-stopping typography flyers over text-free backgrounds, and delivers ready-to-post copy across Facebook, Instagram, X, Threads, and WhatsApp Status.

---

## 🏛️ System Architecture (Milestones 1 to 7)

```
YouTube Data API v3 (Uploads Playlists + Videos.list < 500 units)
       │
       ▼
1. DISCOVERY (src/discover.py) ──> Top 5 ranked by velocity, outlier ratio & engagement
       │
       ▼
2. TRANSCRIPTS & VERIFY (src/transcripts.py, src/verify.py, src/punchlines.py)
   ├── Pluggable chain: Cache -> Inbox manual -> youtube-transcript-api -> Proxy -> Hosted
   └── Code-level fuzzy matching (ratio >= 0.92). Zero fabricated lines. R1 Fail-Soft.
       │
       ▼
3. WRITE ENGINE (src/write.py) ──> Pydantic Schema, A.W. Tozer voice, verbatim Scripture
       │
       ▼
4. DESIGN ENGINE (src/design/) ──> 6 Templates, 3 Sizes (4:5, 1:1, 9:16), WCAG AA >= 4.5:1
       │
       ▼
5. DELIVERY (src/deliver.py) ───> Responsive HTML Briefing + 4 PNGs + Working Share Intents
       │
       ▼
6. OPERATIONS (src/state.py) ───> Single Source of Truth, Idempotency lock, 36h Watchdog
       │
       ▼
7. LEARNING LOOP (src/learn.py) ─> data/performance.csv, weekly feedback weights
```

---

## 📜 Non-Negotiable Integrity Rules

1. **R1: Zero Fabricated Attribution**: Any line enclosed in quotes with a person's name MUST exist in a retrieved transcript (match ratio $\ge 0.92$). If unverified, the issue is signed strictly as *The Kingdom Journal* and `quote = null`.
2. **R2: Scripture is never an "Author"**: Verbatim Scripture is attributed with chapter, verse, and translation label.
3. **R3: Originality Ratio**: At most ONE quoted line $\le 25$ words; at least 70% of words are original reflection; flyers are custom code-rendered designs.
4. **R4: Canon-Validated Scripture**: All references are validated against the 66-book biblical canon and retrieved from `scripture_engine.py`.
5. **R5: Honest Hashtagging**: Never hashtag or tag a minister unless that minister is quoted in that specific post.
6. **R6: Risk & Guarantee Guard**: Rejects and flags prosperity promises, instant miracle guarantees, or manipulative language.
7. **R7: Fail-Soft, Never Silent**: If any stage degrades, delivers a transparent audit report with clean fallback.
8. **R8: Secrets Security**: All API keys and credentials are kept strictly in `.env` / GitHub Secrets.

---

## 🚀 Quickstart & Commands

### Running Locally

```bash
# 1. Activate virtual environment
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# 2. Run unit tests
python -m unittest discover tests

# 3. Dry-Run Execution (Generates flyers & email in out/issue-<N>/ without sending)
python -m src.main --dry-run

# 4. Live Production Dispatch
python -m src.main

# 5. Bypass Idempotency Lock (to re-send or test today)
python -m src.main --force
```

---

## ☁️ GitHub Actions & Operations

The workflow (`.github/workflows/daily.yml`) runs daily at **04:17 UTC (05:17 AM Lagos / West Africa Time)**.

### GitHub Repository Secrets Required
- `SMTP_USER`: Gmail address
- `SMTP_PASSWORD`: 16-character Google App Password
- `YOUTUBE_API_KEY`: YouTube Data API v3 key
- `GEMINI_API_KEY`: Google Gemini API key
- `RECIPIENT_EMAIL`: (Optional) Defaults to SMTP_USER

### Preventing GitHub 60-Day Inactivity Disablement
In public repositories, GitHub automatically pauses scheduled workflows after 60 days of repository inactivity. To prevent missed runs:
1. Set up a free daily ping on [cron-job.org](https://cron-job.org).
2. Point it to trigger the workflow via the GitHub API:
   `POST https://api.github.com/repos/<OWNER>/<REPO>/actions/workflows/daily.yml/dispatches`
   Headers: `Authorization: Bearer <GITHUB_PAT>`
   Body: `{"ref": "main"}`

---

## 📊 Learning Loop & Weekly Reviews

Every issue registers 5 tracking rows in `data/performance.csv`:
```csv
issue,post_id,platform,template,palette,theme,hook_type,reach,shares,saves,comments
50,TKJ-050-FA,facebook,bold_statement,navy_gold,The Secret Place,curiosity,0,0,0,0
```
Update your weekly reach and shares (5 minutes on Sunday) to train the pipeline's template weights.
