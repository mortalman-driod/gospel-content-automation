"""
The Kingdom Journal: Master Pipeline Orchestrator (src/main.py)
Executes the institutional 7-milestone gospel automation pipeline:
M1: Video Discovery & Scoring (src/discover.py)
M2: Transcript Extraction & Code-Level Fuzzy Verification (src/transcripts.py, src/punchlines.py, src/verify.py)
M3: Flyer Design Engine in 3 Sizes & 6 Templates (src/design/engine.py)
M4: Pydantic Schema-Validated Writing Engine (src/write.py)
M5: Institutional Delivery with Inline Artwork & Working Share Intents (src/deliver.py)
M6: State Locks & 36-Hour Watchdog (src/state.py)
M7: Learning Loop & Performance Logging (src/learn.py)
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Setup paths and logging
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("kingdom_journal.main")

from src.discover import DiscoverEngine
from src.transcripts import TranscriptManager
from src.punchlines import PunchlineExtractor
from src.design.engine import FlyerEngine
from src.write import WritingEngine
from src.deliver import EmailDeliverer
from src.state import StateManager
from src.learn import LearningLoop
from src.verify import verify_de_ai_compliance

def run_pipeline(dry_run: bool = False, force: bool = False, override_issue: int = None):
    logger.info("=" * 70)
    logger.info("THE KINGDOM JOURNAL: DAILY EDITORIAL PIPELINE STARTING")
    logger.info(f"Mode: {'DRY-RUN (Simulated)' if dry_run else 'LIVE PRODUCTION'} | Force: {force}")
    logger.info("=" * 70)

    state_mgr = StateManager()

    # Step 0: Idempotency & Watchdog Checks
    can_run, reason = state_mgr.can_run_today(force=force or dry_run)
    if not can_run:
        logger.warning(f"[IDEMPOTENCY LOCK] {reason}")
        print(f"\n[!] Pipeline stopped by idempotency guard: {reason}")
        return

    watchdog_alert = state_mgr.check_watchdog_warning()
    if watchdog_alert:
        logger.warning(f"[WATCHDOG] {watchdog_alert}")

    issue_num = override_issue or state_mgr.get_next_issue_number()
    logger.info(f"Assembling Issue #{issue_num}...")

    review_flags = []
    if watchdog_alert:
        review_flags.append(watchdog_alert)

    try:
        # -------------------------------------------------------------
        # MILESTONE 1: Video Discovery & Velocity Scoring
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 1] DISCOVERING PROVEN-VIRAL MINISTRATIONS ---")
        discover_engine = DiscoverEngine()
        discovery_res = discover_engine.run_discovery(issue_number=issue_num)
        top_videos = discovery_res.get("top_5", [])
        quota_used = discovery_res.get("quota_units_used", 0)

        if not top_videos:
            raise RuntimeError("Discovery stage returned 0 candidate videos.")

        logger.info(f"Top 5 videos ranked with velocity & outlier scores. Quota used: {quota_used} units.")

        # -------------------------------------------------------------
        # MILESTONE 2: Transcript Extraction & Fuzzy Verification
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 2] EXTRACTING TRANSCRIPTS & VERIFYING SPOKEN QUOTES ---")
        transcript_mgr = TranscriptManager(max_fetches_per_run=3)
        punchline_extractor = PunchlineExtractor()

        verified_quote = None
        source_video = None

        for idx, video in enumerate(top_videos[:3]):
            v_id = video.get("video_id") or video.get("id")
            v_title = video.get("title", "")
            logger.info(f"Attempting transcript extraction for candidate #{idx+1}: {v_title[:55]} ({v_id})...")

            snippets, source_type = transcript_mgr.get_transcript(v_id)
            if snippets:
                logger.info(f"Retrieved {len(snippets)} snippets via {source_type}. Extracting punchlines...")
                res = punchline_extractor.extract_punchlines(video, snippets)
                if res.get("primary_quote"):
                    verified_quote = res["primary_quote"]
                    source_video = video
                    logger.info(f"VERIFIED QUOTE: \"{verified_quote['text_verbatim']}\" ({verified_quote['speaker']})")
                    break
                else:
                    logger.info(f"Candidate quotes could not achieve fuzzy match ratio >= 0.92.")

        if not verified_quote:
            logger.info("No candidate quote met strict verification. Degraded fail-soft active (Editorial Reflection Only).")
            source_video = top_videos[0]

        # -------------------------------------------------------------
        # MILESTONE 4: Synthesis & Writing Engine
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 3] SYNTHESIZING EDITORIAL ESSAY & MULTI-PLATFORM KITS ---")
        writer = WritingEngine()
        palette_id = "navy_gold" # Can be rotated
        theme_title = source_video.get("title", "The Secret Place") if source_video else "The Secret Place"

        issue_package = writer.write_issue(
            theme_hint=theme_title,
            verified_quote=verified_quote,
            radar_videos=top_videos,
            palette_id=palette_id,
            issue_number=issue_num
        )
        logger.info(f"Generated Issue Package: Hook = \"{issue_package.hook}\"")

        # De-AI Humanization Verification Gate
        is_compliant, violations, ai_score = verify_de_ai_compliance(
            issue_package.reflection,
            issue_package.facebook_post,
            issue_package.instagram_caption,
            issue_package.whatsapp_status,
        )
        if not is_compliant:
            logger.warning(f"[DE-AI GATE ALERT] AI Score: {ai_score}. Violations detected: {violations}")
            logger.info("Re-rolling issue with alternate storytelling framework to eliminate AI markers...")
            try:
                issue_package = writer.write_issue(
                    theme_hint=theme_title,
                    verified_quote=verified_quote,
                    radar_videos=top_videos,
                    palette_id=palette_id,
                    issue_number=issue_num
                )
                is_compliant, violations, ai_score = verify_de_ai_compliance(
                    issue_package.reflection,
                    issue_package.facebook_post,
                    issue_package.instagram_caption,
                    issue_package.whatsapp_status,
                )
                logger.info(f"[DE-AI GATE RE-ROLL] Post-reroll AI Score: {ai_score}. Compliant: {is_compliant}")
            except Exception as e:
                logger.warning(f"Re-roll error, keeping sanitized package: {e}")
        else:
            logger.info(f"[DE-AI GATE PASS] 100% Natural Human Voice confirmed (AI Score: {ai_score})")

        # -------------------------------------------------------------
        # MILESTONE 3: High-Resolution Flyer Design Engine
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 4] RENDERING EDITORIAL FLYERS (4:5, 1:1, 9:16) ---")
        flyer_engine = FlyerEngine()

        clean_credit = f"— {verified_quote['speaker']}" if verified_quote else "The Kingdom Journal"

        primary_content = {
            "headline_pre": issue_package.viral_headline_pre,
            "accent_word": issue_package.viral_accent_word,
            "accent_color": issue_package.viral_accent_color or "yellow",
            "headline": verified_quote["text_verbatim"] if verified_quote else issue_package.flyers[0].headline,
            "subline": issue_package.viral_subline or "When human striving ends, divine illumination takes over.",
            "credit": clean_credit,
            "scripture_badge": f"{issue_package.scripture.ref}",
            "background_archetype": issue_package.viral_background_archetype or "cross_sunrise",
            "emotional_tone": getattr(issue_package, "emotional_tone", None),
            "emphasized_words": getattr(issue_package, "emphasized_words", None),
            "typography_style": getattr(issue_package, "typography_style", None),
        }

        # Dynamic human archetype selection
        chosen_template = getattr(issue_package, "flyer_template", "asymmetric_split") or "asymmetric_split"
        valid_templates = {"asymmetric_split", "heritage_serif", "heavy_impact", "quiet_light", "viral_quote_poster"}
        if chosen_template not in valid_templates:
            chosen_template = "asymmetric_split"
        logger.info(f"Selected Human Design Archetype for primary flyers: '{chosen_template}'")

        # Render 3 formats for Primary Flyer using chosen archetype
        img_4_5, meta_4_5 = flyer_engine.render_flyer(chosen_template, "4:5", primary_content, palette_id=palette_id)
        img_1_1, meta_1_1 = flyer_engine.render_flyer(chosen_template, "1:1", primary_content, palette_id=palette_id)
        img_9_16, meta_9_16 = flyer_engine.render_flyer(chosen_template, "9:16", primary_content, palette_id=palette_id)

        # Render Alternate Flyer in 4:5 using a complementary art direction
        alt_template = "heritage_serif" if chosen_template != "heritage_serif" else "heavy_impact"
        alt_pool = ["deep_cobalt_wave", "diagonal_royal_gold", "emerald_white_wave", "crimson_cream_wave", "golden_sunburst_clouds", "open_bible"]
        alt_candidates = [b for b in alt_pool if b != primary_content["background_archetype"]]
        alt_bg = alt_candidates[issue_num % len(alt_candidates)]
        alt_content = {
            "headline_pre": issue_package.viral_headline_pre,
            "accent_word": issue_package.viral_accent_word,
            "accent_color": issue_package.viral_accent_color or "gold",
            "headline": verified_quote["text_verbatim"] if verified_quote else (issue_package.flyers[0].headline if issue_package.flyers else "When human capacity runs dry, worship establishes peace."),
            "subline": issue_package.viral_subline or "Rest in His peace today.",
            "credit": clean_credit,
            "scripture_badge": f"{issue_package.scripture.ref}",
            "background_archetype": alt_bg,
            "emotional_tone": getattr(issue_package, "emotional_tone", None),
            "emphasized_words": getattr(issue_package, "emphasized_words", None),
        }
        img_alt_4_5, _ = flyer_engine.render_flyer(alt_template, "4:5", alt_content, palette_id=palette_id)

        flyer_images = {
            "flyer_primary_4_5": img_4_5,
            "flyer_primary_1_1": img_1_1,
            "flyer_primary_9_16": img_9_16,
            "flyer_alternate_4_5": img_alt_4_5
        }
        logger.info(f"Successfully rendered 4 flyer formats. Contrast ratio: {meta_4_5['contrast_ratio']}:1 (WCAG AA: {meta_4_5['wcag_aa_compliant']})")

        # -------------------------------------------------------------
        # MILESTONE 5: Delivery Engine (Email Briefing + PNG Attachments)
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 5] DELIVERING ISSUE BRIEFING ---")
        deliverer = EmailDeliverer()
        package_dict = issue_package.model_dump()

        deliverer.send_issue_email(
            issue_number=issue_num,
            package=package_dict,
            verified_meta=verified_quote,
            radar_videos=top_videos,
            quota_used=quota_used,
            flyer_images=flyer_images,
            review_flags=review_flags,
            dry_run=dry_run
        )

        # -------------------------------------------------------------
        # MILESTONE 6: Commit State & Idempotency Lock
        # -------------------------------------------------------------
        if not dry_run:
            logger.info("\n--- [STAGE 6] COMMITTING STATE & EXPIRING USED TOKENS ---")
            state_mgr.record_success(
                issue_number=issue_num,
                video_id=verified_quote.get("video_id") if verified_quote else None,
                quote_text=verified_quote.get("text_verbatim") if verified_quote else None,
                theme=issue_package.theme
            )

        # -------------------------------------------------------------
        # MILESTONE 7: Register Learning Loop Rows
        # -------------------------------------------------------------
        if not dry_run:
            logger.info("\n--- [STAGE 7] REGISTERING PERFORMANCE TRACKING IDS ---")
            learner = LearningLoop()
            post_ids = learner.register_issue_posts(
                issue_number=issue_num,
                template=chosen_template,
                palette=palette_id,
                theme=issue_package.theme
            )
            logger.info(f"Registered performance post tracking IDs: {', '.join(post_ids[:3])}...")

        logger.info("\n" + "=" * 70)
        logger.info(f"THE KINGDOM JOURNAL ISSUE #{issue_num} COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        state_mgr.record_failure(str(e))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Kingdom Journal Daily Automation")
    parser.add_argument("--dry-run", action="store_true", help="Simulate run, write outputs to out/issue-<N>/ without sending email")
    parser.add_argument("--force", action="store_true", help="Bypass idempotency lock")
    parser.add_argument("--issue", type=int, default=None, help="Explicit issue number override")
    args = parser.parse_args()

    run_pipeline(dry_run=args.dry_run, force=args.force, override_issue=args.issue)
