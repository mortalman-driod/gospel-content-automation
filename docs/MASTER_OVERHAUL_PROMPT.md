# 🏛️ MASTER ARCHITECTURAL OVERHAUL PROMPT: THE KINGDOM JOURNAL
## Automated High-Impact Gospel Discovery, Multi-Format Creative Engine & Executive Distribution System

> **Document Type:** Master System Prompt & Technical Specification Directive  
> **Target Audience:** Autonomous Coding Agents, Systems Architects, and Core Maintainers  
> **System Name:** *The Kingdom Journal* (Autonomous Gospel Automation Pipeline)  
> **Repository:** `gospel-content-automation`  
> **Target Production Cadence:** Daily Unattended Execution (06:00 UTC / 07:00 WAT)  
> **Deployment Target:** GitHub Actions (`ubuntu-latest`) + Local Developer Workstation (`Windows 11`)  
> **Recipient Endpoint:** `aondoaseerezekiel@gmail.com`

---

## 1. SYSTEM IDENTITY & STRATEGIC MANDATE

You are the Lead Systems Architect and Principal Graphic/Editorial Engineer for **The Kingdom Journal**—an enterprise-grade autonomous pipeline that discovers trending gospel teachings across global YouTube ministries, verifies theological and transcript integrity, generates humanized pastoral reflections and micro-copy across six distinct storytelling frameworks, renders typography-perfect viral photographic quote flyers across multiple aspect ratios, and delivers a magazine-grade executive newsletter to subscriber inboxes.

### The Problem This Master Prompt Solves
Previous iterations suffered from critical architectural fragility:
1. **Linux Runner Typography Failure:** Fonts hardcoded to Windows OS paths crashed or silently degraded to 10px unscalable bitmap monospace fonts on Ubuntu GitHub Actions runners. Mislabeled fonts corrupted font weights.
2. **Theological Monoculture:** A zero-argument fallback bug caused the pipeline to lock onto `Romans 8:26` for every single issue regardless of the sermon theme.
3. **Ghost Quote Dual-Generation:** Asking the LLM to generate the newsletter headline and flyer text independently caused divergence—the newsletter preached one message while the flyer displayed an entirely different quote.
4. **Email Client Incompatibility & Bloat:** Desktop Microsoft Outlook broke on CSS Flexbox layouts; low-contrast text failed WCAG AA accessibility; uncompressed 6 MB PNG attachments risked spam flags and Gmail clipping.
5. **Frozen Search Queries:** Discovery remained stuck on `queries[0]`, ignoring 80% of configured topics and causing topic stagnation.
6. **Hallucinated Attributes & AI Tropes:** Sermon transcripts leaked raw channel branding (e.g., *"Koinonia Global"*) into human preacher attributions, and narrative reflections repeatedly defaulted to robotic formulas and overused clichés (*"It was 4 a.m., cold wood palms on my kitchen counter..."*).

### The Mandate
Refactor, harden, and elevate the entire repository down to the skeleton framework. Every module must be deterministic, cross-platform compliant, mathematically validated for visual contrast, theologically sound, and strictly protected against AI hallmarks.

---

## 2. NON-NEGOTIABLE CORE LAWS (P0 - P2)

### [P0] Absolute Veracity & Attribution Purity
* **Rule 1.1 (No Channel Attribution):** A YouTube channel name or production company (e.g., `Koinonia Global`, `Celebration Church TV`, `Streams of Joy`, `Doxology Music`, `Selah Media`) MUST NEVER appear as an author or speaker. Every quote must resolve to a recognized human minister (e.g., `Apostle Joshua Selman`, `Pastor Jerry Eze`, `Apostle Emmanuel Iren`, `Pastor Chingtok Ishaku`, `Minister Dunsin Oyekan`, `Minister Theophilus Sunday`, `Minister Nathaniel Bassey`). If the preacher cannot be verified from the transcript or metadata, the attribution MUST default strictly to:
  $$\text{Attribution} = \text{"— The Kingdom Journal"}$$
* **Rule 1.2 (Verbatim Transcript Lock):** When quoting a preacher, the quote MUST match an actual spoken phrase in the ingested transcript with a fuzzy Levenshtein ratio:
  $$\text{FuzzyMatch}(\text{Quote}, \text{Transcript}) \ge 0.92$$
  If the match score is $< 0.92$, the text must be classified as an editorial reflection and signed strictly as *The Kingdom Journal*, NEVER attributed falsely to the preacher.
* **Rule 1.3 (Single Quote Source of Truth):** The core punchline quote extracted from the transcript is the **Single Source of Truth (SSOT)**. The headline in the email newsletter and the text rendered on the viral flyers MUST originate from the identical structured object. Dual-generation of quotes is strictly prohibited.

### [P0] Cross-Platform Typography & Visual Parity
* **Rule 2.1 (Zero OS Font Path Reliance):** NEVER hardcode `C:\Windows\Fonts\` or `/usr/share/fonts/`. All required typography must be committed as genuine TrueType (`.ttf`) or OpenType (`.otf`) files directly in the repository under `assets/fonts/`.
* **Rule 2.2 (Verified Font Metadata):** Every bundled font must be programmatically verified for proper metadata (family, weight, bold flags). Never alias a Thin or Regular font file as Bold.
* **Rule 2.3 (Guaranteed Relative Resolution):** The font loader MUST search:
  1. `Path(__file__).resolve().parent.parent / "assets" / "fonts" / f"{font_name}.ttf"`
  2. Local bundled asset directory fallbacks.
  3. System generic fallback only as a non-breaking safety net.

### [P0] Canonical Scripture Veracity
* **Rule 3.1 (No Romans 8:26 Hardcoded Default):** The system must dynamically select Scripture references that contextually amplify the sermon's central burden.
* **Rule 3.2 (66-Book Protestant Canon Validation):** Every Scripture reference must be validated against the 66 canonical books of the Bible. Apocryphal or malformed references (e.g., *"Hezekiah 3:1"*) must fail validation and trigger automated re-anchoring.
* **Rule 3.3 (Architectural Migration):** All Bible retrieval logic must live in `src/scripture.py` as an official first-class module, deprecating ad-hoc imports from `scripts/`.

### [P1] De-AI Copywriting & 6-Framework Narrative Rotation
* **Rule 4.1 (Negative Constraint Banned Phrases):** The copy generation engine MUST explicitly ban:
  * *"In our fast-paced world"* / *"In today's fast-paced society"*
  * *"Let's unpack this"* / *"Dive deep into"*
  * *"It is not just X, it is Y"* (formulaic antithesis)
  * *"Most people pray for breakthrough. Few prepare their hearts..."*
  * *"4 a.m., cold wood palms on my kitchen counter..."* (and any atmospheric kitchen counter variants)
  * Sterile numbered lists (`1️⃣, 2️⃣, 3️⃣`) applied uniformly across every social micro-copy block.
* **Rule 4.2 (Deterministic Narrative Rotation):** The daily reflection must cycle through 6 distinct theological and literary frameworks based on `issue_number % 6`:
  1. **Framework 0 (Paradigm Shift):** Shatters a common Christian misconception using historical context and biblical exegesis.
  2. **Framework 1 (Visceral Everyday Tension):** Starts inside a real, relatable modern friction (workplace compromise, silent grief, unanswered prayer) without clichés.
  3. **Framework 2 (Spiritual Diagnosis):** Diagnostic clinical examination of the soul, addressing spiritual stagnation and heart posture.
  4. **Framework 3 (Biblical Drama):** Immersive narrative opening inside an Old or New Testament historical scene, bridging ancient covenant to current walk.
  5. **Framework 4 (Prophetic Exhortation):** Urgent, apostolic, authoritative call to consecration and kingdom purpose.
  6. **Framework 5 (Contemplative Sanctuary):** Quiet, reflective, monastic stillness focused on communion, adoration, and the secret place.

### [P1] Email Deliverability & Client Compatibility
* **Rule 5.1 (Outlook MSO Hybrid Tables):** The email template must render flawlessly across Outlook (Word rendering engine), Gmail (iOS/Android/Web), Apple Mail, and Yahoo. CSS Flexbox and CSS Grid in the core newsletter body are banned. Multi-column cards must use `<table role="presentation">` with Outlook MSO conditional comments:
  ```html
  <!--[if mso]>
  <table role="presentation" width="100%"><tr><td width="50%" valign="top">
  <![endif]-->
  ```
* **Rule 5.2 (WCAG AA Contrast Compliance):** All text elements must achieve a minimum contrast ratio of:
  * Body copy ($< 18\text{pt}$): $\ge 4.5:1$
  * Headlines and bold banners ($\ge 18\text{pt}$): $\ge 7.0:1$
  * High-impact flyer text overlays: $\ge 12.0:1$
  * Against the dark luxury background `#0A1128`, subtext must be `#94A3B8` (7.29:1) or `#CBD5E1` (12.59:1). The low-contrast `#64748B` (3.92:1) is strictly forbidden.
* **Rule 5.3 (Progressive JPEG Payload Optimization):** Inline email images must be compressed progressive JPEGs with:
  $$\text{Image Size} \le 180\text{ KB}, \quad \text{Total Email HTML + Assets} \le 600\text{ KB}$$
  Uncompressed multi-megabyte PNG attachments that trigger Gmail clipping (`[Message clipped] View entire message`) or ISP spam throttles are banned.

### [P2] Discovery Rotation & Channel Velocity
* **Rule 6.1 (Dynamic Query Rotation):** The search query must never be static. The discovery engine must rotate through `config/queries.yml` using:
  $$\text{QueryIndex} = \text{issue\_number} \pmod{|\text{queries}|}$$
* **Rule 6.2 (Velocity Scoring Formula):** Videos must be ranked by normalized 24-hour velocity:
  $$V = \frac{\Delta \text{Views}}{\max(\Delta \text{Hours}, 1.0)^{0.85}} \times W_{\text{channel}}$$

### [P2] CI/CD State Concurrency & Self-Healing
* **Rule 7.1 (Rebase-Lock in Automation):** GitHub Actions cron workflows must execute `git pull --rebase origin main` before committing updated `state.json` or `performance.csv` to prevent non-fast-forward push rejections.
* **Rule 7.2 (Archive Pruning):** Historical tracking sets (`used.json`) must prune entries older than 30 days to avoid unbounded file growth while preventing topic repetition.

---

## 3. DETAILED ARCHITECTURAL BLUEPRINT BY MODULE

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        THE KINGDOM JOURNAL PIPELINE GRAPH                         │
└───────────────────────────────────────────────────────────────────────────────────┘
   [1. DISCOVERY]    ──> Rotate queries.yml, calculate velocity, scrape transcripts
         │
   [2. VERIFICATION] ──> Fuzzy-match transcript >= 0.92, validate 66-book canon
         │
   [3. EDITORIAL]    ──> Rotate 6 storytelling models, enforce single quote SSOT
         │
   [4. DESIGN]       ──> 35mm canvases, Montserrat-Bold, brush ribbons, WCAG AA >= 15:1
         │
   [5. DELIVERY]     ──> Outlook MSO hybrid tables, progressive JPEGs, clean headers
         │
   [6. CI/CD & OPS]  ──> Git rebase locks, automated state commit, telemetry CLI
```

---

### MODULE 1: VISUAL & TYPOGRAPHY ENGINE (`src/design/`)

#### 1.1 Canvas Specifications
* The engine renders two mandatory aspect ratios for every issue:
  * **Square / Feed Canvas (`1:1`):** $1080 \times 1080 \text{ px}$ (for Instagram, Facebook, LinkedIn, Twitter/X).
  * **Vertical / Story Canvas (`9:16`):** $1080 \times 1920 \text{ px}$ (for WhatsApp Status, Instagram Stories, Reels cover).
  * **Portrait Canvas (`4:5`):** $1080 \times 1350 \text{ px}$ (for Instagram Portrait Feed).

#### 1.2 Photographic Background Architecture
* Eliminate flat, lifeless synthetic backgrounds.
* Canvas backgrounds must be photorealistic 35mm photographic assets stored in `assets/backgrounds/`:
  1. `viral_cross_sunrise.jpg` (Rugged wooden cross on mountain summit, dawn rays, dramatic cinematic clouds).
  2. `viral_open_bible.jpg` (Vintage leather-bound Bible, aged gilded edges, warm mahogany desk, dramatic soft lighting).
  3. `viral_green_sprout.jpg` (Fresh green seedling pushing through rich dark soil, dew drops, morning sun).
  4. `viral_royal_crown.jpg` (Antique golden royal crown with jewels resting on royal purple/crimson velvet).
  5. `viral_mountain_summit.jpg` (Silhouette of worshipper standing atop high mountain peak facing golden horizon).
  6. `viral_study_desk.jpg` (Open study Bible, journal, pen, warm brass lamp, thoughtful sanctuary environment).

#### 1.3 Photographic Processing & Vignette Math
* Before text rendering, apply an intentional dark radial vignette and directional gradient to ensure text readability:
  $$I_{\text{processed}}(x, y) = I_{\text{base}}(x, y) \times \left(1.0 - \alpha(x, y)\right)$$
  Where $\alpha(x, y)$ provides an extra $40\%\text{--}70\%$ darkening in the upper two-thirds where headlines sit, keeping the dramatic bottom visual intact.
* **Pre-Text Background Copy:** The engine MUST clone the canvas *after* vignette application but *before* drawing text:
  ```python
  pre_text_bg = img.copy()
  ```
  All WCAG luminance and contrast checks MUST sample `pre_text_bg` to eliminate measurement corruption.

#### 1.4 Typographic Hierarchy & Brush Underline Math
* **Word Splitter:** Split the viral punchline into:
  * `viral_headline_pre`: The introductory/contextual clause (rendered in crisp pure white `#FFFFFF` or pale cream `#F8FAFC`, font weight: 700/800).
  * `viral_accent_word`: The 1–2 power punchline words (rendered in high-voltage sunshine yellow `#FACC15` or vivid coral crimson `#EF4444`, font weight: 900 italic or extra-bold).
* **Dynamic Curved Brush Stroke:**
  * When drawing the accent underline, calculate:
    $$x_0 = \text{word\_left} - 8, \quad x_1 = \text{word\_right} + 12$$
    $$y_0 = \text{word\_bottom} + 4, \quad y_1 = \text{word\_bottom} + 16$$
  * Render a dual-pass quadratic Bézier curve with tapering width (8px to 14px to 6px) to emulate authentic acrylic paint brush bristles.
* **Scripture Pill Badge:**
  * Rendered as a solid pill box in golden amber `#FACC15` or crimson `#DC2626` with pure black `#000000` or stark white `#FFFFFF` bold text.
  * Border radius: $6\text{--}8\text{ px}$. Internal padding: $H = 20\text{ px}, V = 8\text{ px}$.

#### 1.5 Font Resolution Engine (`src/design/text_layout.py`)
```python
def resolve_bundled_font(font_family: str, weight: str = "Bold") -> str:
    """
    Deterministically resolves font paths from assets/fonts/ with zero OS dependencies.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
    mapping = {
        ("montserrat", "bold"): "Montserrat-Bold.ttf",
        ("montserrat", "extrabold"): "Montserrat-ExtraBold.ttf",
        ("montserrat", "black"): "Montserrat-Black.ttf",
        ("playfair", "bold"): "PlayfairDisplay-Bold.ttf",
        ("lora", "regular"): "Lora-Regular.ttf",
        ("lora", "bold"): "Lora-Bold.ttf",
    }
    key = (font_family.lower(), weight.lower())
    font_file = mapping.get(key, "Montserrat-Bold.ttf")
    target_path = base_dir / font_file
    
    if target_path.exists():
        return str(target_path)
    
    # Non-breaking fallback with explicit warning
    logger.warning(f"Bundled font {target_path} missing! Falling back to generic sans.")
    return "arial.ttf"
```

---

### MODULE 2: THEOLOGICAL TRUTH & SCRIPTURE ENGINE (`src/scripture.py` & `src/verify.py`)

#### 2.1 Complete Scripture Engine Migration
* Deprecate external scripts. Maintain `src/scripture.py` as the official canonical scripture interface.
* Support offline bundled Bible texts for core translations (KJV, ESV, NIV, NKJV) cached locally in `data/bibles/` or fetched via resilient multi-endpoint fallback.

#### 2.2 Canonical 66-Book Verification Table
Every reference extracted by LLM or user input must match the canonical schema:
$$\text{Reference} = \langle\text{Book}\rangle\ \langle\text{Chapter}\rangle:\langle\text{VerseStart}\rangle[- \langle\text{VerseEnd}\rangle]$$
* Supported books strictly defined in `src/verify.py` (Genesis through Revelation).
* Reject any reference failing canonical regex:
  ```python
  CANONICAL_BOOKS = {
      "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
      "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
      "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
      "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
      "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
      "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
      "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians",
      "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
      "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
  }
  ```

#### 2.3 Elimination of the Monocultural Fallback Bug
* In `src/write.py`, line 282 previously invoked `self._fetch_scripture()` with 0 arguments.
* **Overhaul Requirement:** `_fetch_scripture()` must accept `theme`, `quote`, and `preferred_ref`.
* If `preferred_ref` is provided, validate it against `CANONICAL_BOOKS`.
* If `preferred_ref` is empty, use semantic keyword mapping from the sermon's core punchlines:
  * Faith/Trust $\rightarrow$ *Hebrews 11:1, Proverbs 3:5-6, Mark 11:23*
  * Waiting/Patience $\rightarrow$ *Isaiah 40:31, Lamentations 3:25-26, Psalm 27:14*
  * Prayer/Altar $\rightarrow$ *Luke 18:1, 1 Thessalonians 5:17, James 5:16*
  * Warfare/Victory $\rightarrow$ *2 Corinthians 10:4-5, Romans 8:37, Ephesians 6:11-13*
  * Grace/Mercy $\rightarrow$ *Hebrews 4:16, 2 Corinthians 12:9, Titus 2:11*
  * Purpose/Calling $\rightarrow$ *Jeremiah 29:11, Romans 8:28, 2 Timothy 1:9*
* Only as an ultimate safety net may the engine select from an array of 50 diverse foundational verses—NEVER a single repeated verse.

#### 2.4 Fuzzy Transcript Verification Engine
```python
def verify_preacher_quote(quote: str, transcript_text: str) -> Tuple[bool, float, str]:
    """
    Verifies if quote exists in sermon transcript with fuzzy ratio >= 0.92.
    Returns (is_verified, score, clean_quote).
    """
    clean_quote = normalize_text(quote)
    clean_transcript = normalize_text(transcript_text)
    
    # Substring direct check
    if clean_quote in clean_transcript:
        return True, 1.0, clean_quote
        
    # Sliding window fuzzy ratio
    words = clean_quote.split()
    window_size = len(words)
    transcript_words = clean_transcript.split()
    
    best_ratio = 0.0
    for i in range(len(transcript_words) - window_size + 1):
        window_text = " ".join(transcript_words[i:i + window_size])
        ratio = difflib.SequenceMatcher(None, clean_quote, window_text).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            if best_ratio >= 0.92:
                return True, best_ratio, clean_quote
                
    return best_ratio >= 0.92, best_ratio, clean_quote
```

---

### MODULE 3: EDITORIAL & NARRATIVE SYNTHESIS (`src/write.py` & `src/punchlines.py`)

#### 3.1 Preacher Attribution Sanitizer
* Implement canonical preacher name resolution in `src/punchlines.py`:
```python
CHANNEL_SPEAKER_OVERRIDE = {
    "koinonia global": "Apostle Joshua Selman",
    "koinoniaglobal": "Apostle Joshua Selman",
    "apostle joshua selman": "Apostle Joshua Selman",
    "celebration church international": "Apostle Emmanuel Iren",
    "celebration church tv": "Apostle Emmanuel Iren",
    "streams of joy international": "Pastor Jerry Eze",
    "pastor jerry eze": "Pastor Jerry Eze",
    "chingtok ishakum": "Pastor Chingtok Ishaku",
    "the god life club": "Pastor Chingtok Ishaku",
    "dunsin oyekan": "Minister Dunsin Oyekan",
    "theophilus sunday": "Minister Theophilus Sunday",
    "nathaniel bassey": "Minister Nathaniel Bassey",
    "doxology music": "The Kingdom Journal",
    "gospel hits": "The Kingdom Journal",
}
```
* If title or metadata contains channel handles, cleanse them through `resolve_speaker_name()`.

#### 3.2 Single Quote Source of Truth (SSOT) Architecture
* The LLM prompt in `src/write.py` must return a single unified JSON schema:
```json
{
  "theme": "The Cost of Spiritual Depth",
  "quote": {
    "text": "The secret place is not where you visit God; it is where you die to yourself.",
    "speaker": "Apostle Joshua Selman",
    "is_verbatim": true,
    "source_timestamp": "14:22"
  },
  "headline_visual": {
    "pre_accent": "The secret place is not where you visit God;",
    "accent_word": "IT IS WHERE YOU DIE."
  },
  "scripture": {
    "reference": "Galatians 2:20",
    "text": "I am crucified with Christ: nevertheless I live; yet not I, but Christ liveth in me...",
    "version": "KJV"
  },
  "storytelling_framework_used": "Spiritual Diagnosis",
  "reflection_body": [
    "Paragraph 1 (The Diagnosis)...",
    "Paragraph 2 (The Exegesis)...",
    "Paragraph 3 (The Charge)..."
  ],
  "prayer_point": "Lord, deliver me from the vanity of casual devotion...",
  "social_threads": {
    "twitter": ["1/ ...", "2/ ..."],
    "instagram_caption": "...",
    "whatsapp_broadcast": "..."
  }
}
```
* **Enforcement:** `flyer_engine.render()` MUST receive `headline_visual["pre_accent"]` and `headline_visual["accent_word"]` directly from this validated object. It is strictly forbidden to call a separate generation loop for the flyer.

#### 3.3 The 6 Storytelling Frameworks Engine
* Compute framework index:
  $$\text{FrameworkIndex} = \text{issue\_number} \pmod 6$$
* Prompt injection dynamically selects the exact framework system prompt:
  * **Framework 0 (Paradigm Shift):** "Start by exposing the flaw in modern comfort-theology. Contrast man's convenience with God's covenant."
  * **Framework 1 (Visceral Everyday Tension):** "Open with a relatable moment of frustration, exhaustion, or silent pressure. Connect the tension directly to the cross."
  * **Framework 2 (Spiritual Diagnosis):** "Examine the heart like a physician. Identify where compromise or numbness entered. Prescribe repentance and altar renewal."
  * **Framework 3 (Biblical Drama):** "Transport the reader to the dusty plains of Mamre, the cave of Adullam, or the Roman cell in Philippi. Make the ancient covenant breathe."
  * **Framework 4 (Prophetic Exhortation):** "Write with apostolic fire. Bold, direct declarations of kingdom authority, spiritual alignment, and holiness."
  * **Framework 5 (Contemplative Sanctuary):** "Quiet, gentle, monastic prose. Focus on the beauty of Christ, silence before His presence, and total abandonment to His will."

---

### MODULE 4: DISCOVERY, VELOCITY & QUOTA ENGINE (`src/discover.py`)

#### 4.1 Search Query Dynamic Rotation
* Parse `config/queries.yml`.
* Rotate search terms daily:
```python
query_idx = issue_number % len(self.queries)
current_query = self.queries[query_idx]
logger.info(f"Issue #{issue_number}: Curating with query [{query_idx}]: '{current_query}'")
```

#### 4.2 YouTube Data API Quota Safeguard
* Search endpoint calls cost 100 quota units.
* Video details cost 1 unit.
* Enforce quota budgeting:
  * Maximum 1 search list call per daily run ($100\text{ units}$).
  * Maximum 1 videos list call per daily run ($1\text{ unit}$).
  * Total daily cost $\le 101\text{ units}$ of free $10,000$ daily quota.
* If YouTube API key is missing or quota exhausted ($403$), immediately switch to `yt-dlp` metadata scraper or local curated RSS feeds with zero crash.

#### 4.3 Velocity Scoring & Deduplication
* Exclude videos found in `data/used.json` (videos processed within last 30 days).
* Calculate 24-hour velocity score:
```python
hours_active = max((now - published_at).total_seconds() / 3600.0, 1.0)
velocity_score = (view_count / (hours_active ** 0.85)) * channel_weight
```
* Select the highest velocity video with available English transcript/captions.

---

### MODULE 5: EMAIL CLIENT ENGINEERING & ASSET COMPRESSION (`src/deliver.py`)

#### 5.1 Outlook MSO-Compliant Hybrid Architecture
* All layouts must be table-based with fixed container widths ($600\text{ px}$ max).
* Responsive CSS in `<style>` block for mobile:
```html
<!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <!--[if mso]>
  <xml>
    <o:OfficeDocumentSettings>
      <o:AllowPNG/>
      <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
  </xml>
  <![endif]-->
  <style>
    body { margin: 0; padding: 0; background-color: #050B14; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    table { border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    td { padding: 0; }
    img { -ms-interpolation-mode: bicubic; display: block; border: 0; outline: none; }
    @media only screen and (max-width: 620px) {
      .container { width: 100% !important; }
      .mobile-stack { display: block !important; width: 100% !important; }
      .headline { font-size: 26px !important; line-height: 32px !important; }
    }
  </style>
</head>
```

#### 5.2 WCAG AA Verified Color Palette
| Token | Hex Code | Contrast vs `#0A1128` | Usage | Status |
| :--- | :--- | :--- | :--- | :--- |
| `DarkBg` | `#0A1128` | 1.0:1 | Primary Container Background | Compliant |
| `SurfaceCard`| `#111C3A` | 1.34:1 | Card Background Containers | Compliant |
| `TextWhite` | `#FFFFFF` | 19.34:1 | Primary Titles & Headlines | ✅ WCAG AAA |
| `TextSlate` | `#CBD5E1` | 12.59:1 | Primary Body Reflection Copy | ✅ WCAG AAA |
| `TextMuted` | `#94A3B8` | 7.29:1 | Metadata, Timestamps, Labels | ✅ WCAG AA |
| `TextWarning`| `#FACC15` | 14.88:1 | Scripture Badges & Accents | ✅ WCAG AAA |
| `BannedSlate`| `#64748B` | **3.92:1** | **BANNED IN PRODUCTION** | ❌ FAILS WCAG |

#### 5.3 Image Payload Compression Pipeline
* Inline email graphics must be progressive JPEGs:
```python
def optimize_email_asset(input_path: Path, output_path: Path, max_kb: int = 180) -> Path:
    """
    Compresses poster render to a progressive JPEG under max_kb for instant email loading.
    """
    with Image.open(input_path) as img:
        rgb_img = img.convert("RGB")
        quality = 85
        rgb_img.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)
        
        while output_path.stat().st_size > (max_kb * 1024) and quality > 40:
            quality -= 5
            rgb_img.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)
            
    return output_path
```

---

### MODULE 6: CI/CD STATE CONCURRENCY & CLOSED-LOOP TELEMETRY

#### 6.1 GitHub Actions Workflow Hardening (`.github/workflows/daily.yml`)
* Inject rebase locks before commit push:
```yaml
      - name: Rebase and Push State
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git fetch origin main
          git pull --rebase origin main
          git add data/state.json data/performance.csv data/used.json
          git commit -m "chore(ops): update daily issue state and performance telemetry [skip ci]" || echo "No changes to commit"
          git push origin main
```

#### 6.2 Closed-Loop Learning CLI (`src/learn.py`)
* Connect manual feedback ingestion to update `data/performance.csv`:
```bash
python -m src.learn --log --issue 55 --shares 142 --saves 89 --likes 1205 --reach 18400
```
* Update exploration/exploitation bandit weights in `src/design/engine.py` using empirical engagement metrics.

---

## 4. ACCEPTANCE CRITERIA & VERIFICATION PROTOCOL

Every implementation of this master overhaul must satisfy the following automated and visual verification gates:

### Automated Test Suite (`tests/`)
1. **Font Resolution Test:** Assert that `resolve_bundled_font("Montserrat", "Bold")` returns an existing file inside `assets/fonts/` with TrueType headers `00 01 00 00` and weight metadata `700`.
2. **Scripture Validation Test:** Assert that `validate_scripture_reference()` returns `True` for all 66 canonical books and `False` for any non-canonical or malformed text.
3. **SSOT Quote Match Test:** Assert that `flyer.headline_pre + " " + flyer.accent_word` is a normalized substring of `issue.quote.text`.
4. **Contrast Math Test:** Assert that `calculate_contrast_ratio()` on all rendered flyers returns $\ge 12.0:1$ across all sampled text coordinates.
5. **Payload Size Test:** Assert that `flyer_email_optimized.jpg` is $\le 180\text{ KB}$ and total email size $\le 600\text{ KB}$.
6. **Email Markup Test:** Assert that the generated email HTML contains zero `display: flex` or `display: grid` directives in body containers and passes `mso` table validation.

### Production Dry-Run Verification Command
```bash
python -m src.main --dry-run --issue 56
```
Must execute cleanly in $< 45\text{ seconds}$ with zero errors, generate all 3 aspect ratios, validate contrast ratios $> 15:1$, and verify that preacher attribution resolves to a human minister or *The Kingdom Journal*.

---

## 5. EXECUTION DIRECTIVE

Implement this specification across all modules of `gospel-content-automation`. Maintain git history integrity, preserve existing working tests, update outdated assertions, and ensure the production pipeline is hardened against all failure modes identified.
