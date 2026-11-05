# 🕊️ Kingdom Creative Media Engine
> Automated daily YouTube gospel trend analysis, viral social media flyer generation, and classic editorial media kit dispatch.

---

## 🌟 Architecture Overview

This autonomous pipeline runs every morning at **7:00 AM (West Africa Time / Africa/Lagos)**:
1. **Trend & Sermon Ingestion**: Analyzes viral worship ministrations from official channels (Apostle Joshua Selman, Dunsin Oyekan, Theophilus Sunday, Moses Bliss, Elevation Worship).
2. **De-AI Humanized Copywriting**: Curates platform-standard captions for **Instagram, WhatsApp Status, Facebook, Twitter/X, and Threads** with authentic fellowship tone.
3. **Multi-Format Graphic Fliers**: Produces high-resolution graphics with textured brush ribbons and scripture citations (1:1 square, 9:16 vertical stories).
4. **Pre-Filled Social Intent Links**: Dispatches an editorial newsletter with 1-click pre-filled compose buttons for X, WhatsApp, Threads, and Facebook.
5. **Deduplication Memory**: Tracks quote and video history in SQLite to guarantee zero repetition within 30 days.

---

## ☁️ Running 24/7 on GitHub Actions (Zero Machine Dependency)

The pipeline is fully configured to run serverless in the cloud via **GitHub Actions** (`.github/workflows/daily_briefing.yml`).

### Required GitHub Secrets
To activate cloud execution:
1. Go to your repository on GitHub: `Settings` > `Secrets and variables` > `Actions` > `New repository secret`.
2. Add the following repository secrets:
   * `SMTP_USER`: `aondoaseerezekiel@gmail.com`
   * `SMTP_PASSWORD`: Your 16-character Google App Password (`ujqpirdjmwppgqol`)
   * `YOUTUBE_API_KEY`: *(Optional)* Your YouTube Data API v3 key from Google Cloud Console.

---

## 🚀 Local Development

```bash
# Clone the repository
git clone https://github.com/mortalman-driod/gospel-content-automation.git
cd gospel-content-automation

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp .env.example .env

# Run local test dispatch
python scripts/send_classic_10_email.py
```
