"""
Typography Art Direction & Emotional Matching Engine (src/design/typography_system.py)
Implements a multi-hierarchy typographic system with 3-5 complementary fonts per design:
  Role 1: Main Headline / Hero Quote (display)
  Role 2: Emphasized Anchor Words (accent: 1-4 words max)
  Role 3: Supporting Message (support: quieter refined sans/serif)
  Role 4: Scripture Reference Badge/Strip (reference: compact condensed)
  Role 5: Small Details & Credit (detail: neutral modern sans)

Maps emotional message tone + photographic negative space + luminance polarity
to bespoke, magazine-grade Christian editorial art direction.
"""

import re
from typing import Dict, List, Optional, Tuple

# 5 Style Directions aligned with Christian & Editorial Typography Craft
TYPOGRAPHY_STYLES: Dict[str, Dict] = {
    # A. Bold modern sans + expressive brush script + clean medium sans
    "encouragement_brush": {
        "id": "encouragement_brush",
        "name": "Encouragement & Hope (Sans + Brush Script)",
        "tones": ["encouragement", "hope", "faith", "comfort"],
        "fonts": {
            "display": "sans_bold",             # Poppins-Bold
            "accent": "display_brush",          # KaushanScript-Regular
            "support": "sans_medium",           # Poppins-Medium
            "reference": "display_condensed_italic", # BarlowCondensed-BoldItalic
            "detail": "sans_regular",           # Poppins-Regular
        },
        "treatment": "hero_anchor_script",      # Massive brush script anchor + curved brush underline
        "badge_style": "brush",                 # Painted brush ribbon badge
        "support_rules": False,
        "accent_scale": 1.48,
        "line_leading": 1.18,
    },
    # B. Heavy condensed sans + painterly highlight strip + refined italic serif support
    "authority_condensed": {
        "id": "authority_condensed",
        "name": "Authority & Urgency (Condensed + Highlight Strip)",
        "tones": ["authority", "urgency", "warning", "action", "repentance"],
        "fonts": {
            "display": "sans_bold_italic",      # Poppins-BoldItalic
            "accent": "display_condensed",      # BarlowCondensed-Bold
            "support": "serif_italic",          # DMSerifDisplay-Italic
            "reference": "sans_condensed_ref",  # BarlowCondensed-SemiBold
            "detail": "sans_regular",           # Poppins-Regular
        },
        "treatment": "paint_strip_highlight",   # Emphasized phrase inside organic paint strip
        "badge_style": "pill",
        "support_rules": True,                  # — Work hard, pray often... —
        "accent_scale": 1.16,
        "line_leading": 1.28,
    },
    # C. Dramatic editorial serif + inline italic serif accents + clean sans
    "reflection_editorial": {
        "id": "reflection_editorial",
        "name": "Spiritual Reflection (Editorial Serif + Italic Inline)",
        "tones": ["reflection", "wisdom", "scripture", "revelation", "meditation"],
        "fonts": {
            "display": "serif_editorial",       # DMSerifDisplay-Regular
            "accent": "serif_italic",           # DMSerifDisplay-Italic
            "support": "sans_medium",           # Poppins-Medium
            "reference": "display_condensed",   # BarlowCondensed-Bold
            "detail": "sans_regular",           # Poppins-Regular
        },
        "treatment": "inline_italic_accent",    # Inline italic contrast + sweeping arc
        "badge_style": "pill",
        "support_rules": False,
        "accent_scale": 1.06,
        "line_leading": 1.24,
    },
    # D. Refined classic serif + calligraphic script accent + minimalist sans
    "grace_calligraphy": {
        "id": "grace_calligraphy",
        "name": "Grace & Worship (Classic Serif + Calligraphy)",
        "tones": ["grace", "worship", "love", "mercy", "peace", "humility"],
        "fonts": {
            "display": "serif_bold",            # PlayfairDisplay-Bold
            "accent": "display_brush",          # KaushanScript-Regular (legible at all mobile widths)
            "support": "sans_medium",           # Poppins-Medium
            "reference": "sans_condensed_ref",  # BarlowCondensed-SemiBold
            "detail": "sans_regular",           # Poppins-Regular
        },
        "treatment": "hero_anchor_script",
        "badge_style": "brush",
        "support_rules": False,
        "accent_scale": 1.40,
        "line_leading": 1.22,
    },
    # E. Towering display sans + expressive condensed italic accent + crisp sans support
    "victory_statement": {
        "id": "victory_statement",
        "name": "Victory & Breakthrough (Towering Display)",
        "tones": ["victory", "breakthrough", "power", "overcoming"],
        "fonts": {
            "display": "display_bebas",         # BebasNeue-Regular
            "accent": "display_condensed_italic", # BarlowCondensed-BoldItalic
            "support": "sans_medium",           # Poppins-Medium
            "reference": "display_condensed",   # BarlowCondensed-Bold
            "detail": "sans_regular",           # Poppins-Regular
        },
        "treatment": "inline_italic_accent",
        "badge_style": "pill",
        "support_rules": True,
        "accent_scale": 1.08,
        "line_leading": 1.12,
    },
}

# Verified spatial zones per photographic canvas (keeps subjects/faces/crosses/Bibles untouched)
BACKGROUND_PROFILES: Dict[str, Dict] = {
    "cross_sunrise": {
        # Wooden cross sits lower-right (x > 55%, y > 43%); bright sky across upper-left & top
        "polarity": "light_sky",
        "zones": {
            "4:5":  {"x1": 0.08, "y1": 0.07, "x2": 0.57, "y2": 0.57, "align": "left"},
            "1:1":  {"x1": 0.07, "y1": 0.07, "x2": 0.55, "y2": 0.64, "align": "left"},
            "9:16": {"x1": 0.09, "y1": 0.13, "x2": 0.91, "y2": 0.44, "align": "center"},
        },
    },
    "mountain_summit": {
        # Hiker on ridge in bottom half (y > 52%); clear sky in top 48%
        "polarity": "light_sky",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.49, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.49, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.13, "x2": 0.91, "y2": 0.48, "align": "center"},
        },
    },
    "green_sprout": {
        # Dewdrop sprout in lower-right/center (y > 56%); dark bokeh top 53%
        "polarity": "dark",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.52, "align": "center"},
            "1:1":  {"x1": 0.08, "y1": 0.07, "x2": 0.92, "y2": 0.54, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.13, "x2": 0.91, "y2": 0.50, "align": "center"},
        },
    },
    "open_bible": {
        # Open Bible across lower half (y > 51%); dark quiet wall in upper 49%
        "polarity": "dark",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.49, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.48, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.13, "x2": 0.91, "y2": 0.48, "align": "center"},
        },
    },
    "royal_crown": {
        # Golden crown on velvet bottom half (y > 50%); dark purple folds in upper 48%
        "polarity": "dark",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.48, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.07, "x2": 0.91, "y2": 0.47, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.13, "x2": 0.91, "y2": 0.47, "align": "center"},
        },
    },
    "study_desk": {
        # Desk lamp right (x > 74%), notebook bottom (y > 68%); warm plaster wall left
        "polarity": "light_wall",
        "zones": {
            "4:5":  {"x1": 0.08, "y1": 0.09, "x2": 0.72, "y2": 0.62, "align": "left"},
            "1:1":  {"x1": 0.08, "y1": 0.08, "x2": 0.72, "y2": 0.60, "align": "left"},
            "9:16": {"x1": 0.09, "y1": 0.13, "x2": 0.91, "y2": 0.50, "align": "center"},
        },
    },
    "diagonal_royal_gold": {
        # Crisp white/silver diagonal paper framed top-left & bottom-right with navy+gold bands
        "polarity": "light_wall",
        "zones": {
            "4:5":  {"x1": 0.12, "y1": 0.21, "x2": 0.88, "y2": 0.76, "align": "center"},
            "1:1":  {"x1": 0.12, "y1": 0.20, "x2": 0.88, "y2": 0.76, "align": "center"},
            "9:16": {"x1": 0.10, "y1": 0.22, "x2": 0.90, "y2": 0.75, "align": "center"},
        },
    },
    "golden_sunburst_clouds": {
        # Radiant warm sky top-left/center, amber clouds below (y > 67%)
        "polarity": "light_sky",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.11, "x2": 0.89, "y2": 0.63, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.10, "x2": 0.89, "y2": 0.63, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.14, "x2": 0.91, "y2": 0.60, "align": "center"},
        },
    },
    "deep_cobalt_wave": {
        # Rich royal cobalt field between upper azure curve (y < 14%) and gold S-wave (y > 75%)
        "polarity": "dark",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.18, "x2": 0.91, "y2": 0.73, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.18, "x2": 0.91, "y2": 0.73, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.20, "x2": 0.91, "y2": 0.72, "align": "center"},
        },
    },
    "emerald_white_wave": {
        # Clean ivory center framed by top-left & bottom-right forest/lime waves
        "polarity": "light_wall",
        "zones": {
            "4:5":  {"x1": 0.11, "y1": 0.21, "x2": 0.89, "y2": 0.73, "align": "center"},
            "1:1":  {"x1": 0.11, "y1": 0.20, "x2": 0.89, "y2": 0.74, "align": "center"},
            "9:16": {"x1": 0.10, "y1": 0.22, "x2": 0.90, "y2": 0.72, "align": "center"},
        },
    },
    "crimson_cream_wave": {
        # Warm parchment cream center framed by scarlet waves top (y < 14%) & bottom (y > 76%)
        "polarity": "light_wall",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.18, "x2": 0.91, "y2": 0.73, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.18, "x2": 0.91, "y2": 0.73, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.20, "x2": 0.91, "y2": 0.72, "align": "center"},
        },
    },
    "terracotta_amber_wave": {
        # Warm linen ivory field framed top & bottom by deep terracotta + burnt amber waves
        "polarity": "light_wall",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.18, "x2": 0.91, "y2": 0.73, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.18, "x2": 0.91, "y2": 0.73, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.20, "x2": 0.91, "y2": 0.72, "align": "center"},
        },
    },
}

# Approved 2-3 Color Harmonies (never random gradients or rainbow noise)
COLOR_HARMONIES: Dict[str, Dict] = {
    # Bright sky / light wall ink palettes
    "light_navy_crimson": {
        "primary": (14, 29, 58, 255),      # Deep editorial navy
        "accent": (118, 12, 18, 255),      # Rich high-contrast crimson ink (4.5:1+ on blue sky)
        "support": (28, 42, 68, 248),      # Muted dark navy slate
        "detail": (42, 56, 78, 240),       # Subtle slate
        "strip_bg": (14, 29, 58, 255),     # Navy highlight strip
        "strip_fg": (255, 255, 255, 255),  # Crisp white text inside strip
        "badge_bg": (14, 29, 58, 255),     # Navy ribbon/pill badge
        "badge_fg": (255, 255, 255, 255),
        "underline": (165, 20, 26, 255),   # Crimson curved underline
        "is_dark_text": True,
    },
    "light_charcoal_red": {
        "primary": (18, 20, 24, 255),      # Crisp ink charcoal
        "accent": (122, 14, 20, 255),      # Rich high-contrast red ink
        "support": (42, 46, 54, 248),
        "detail": (62, 68, 78, 240),
        "strip_bg": (250, 204, 21, 255),   # Sunshine yellow highlight strip
        "strip_fg": (17, 24, 39, 255),     # Dark ink inside yellow strip
        "badge_bg": (165, 22, 26, 255),    # Crimson badge
        "badge_fg": (255, 255, 255, 255),
        "underline": (165, 22, 26, 255),
        "is_dark_text": True,
    },
    # Moody dark photography palettes
    "dark_white_gold": {
        "primary": (255, 255, 255, 255),   # Crisp white
        "accent": (250, 204, 21, 255),     # Warm luminous gold/yellow
        "support": (236, 240, 245, 242),   # Soft off-white
        "detail": (210, 218, 228, 225),    # Quiet detail gray-white
        "strip_bg": (250, 204, 21, 255),   # Yellow paint strip
        "strip_fg": (15, 23, 42, 255),     # Deep navy ink inside yellow strip
        "badge_bg": (250, 204, 21, 255),   # Yellow badge
        "badge_fg": (15, 23, 42, 255),
        "underline": (250, 204, 21, 255),
        "is_dark_text": False,
    },
    "dark_white_crimson": {
        "primary": (255, 255, 255, 255),
        "accent": (248, 113, 113, 255),    # Readable coral-crimson on dark
        "support": (236, 240, 245, 242),
        "detail": (210, 218, 228, 225),
        "strip_bg": (185, 28, 28, 255),    # Deep red strip
        "strip_fg": (255, 255, 255, 255),
        "badge_bg": (185, 28, 28, 255),
        "badge_fg": (255, 255, 255, 255),
        "underline": (239, 68, 68, 255),
        "is_dark_text": False,
    },
    "dark_cream_gold": {
        "primary": (250, 246, 238, 255),   # Warm ivory cream
        "accent": (228, 184, 72, 255),     # Antique gold
        "support": (230, 224, 214, 240),
        "detail": (205, 198, 186, 225),
        "strip_bg": (228, 184, 72, 255),
        "strip_fg": (18, 18, 24, 255),
        "badge_bg": (228, 184, 72, 255),
        "badge_fg": (18, 18, 24, 255),
        "underline": (228, 184, 72, 255),
        "is_dark_text": False,
    },
    # Viral Custom Canvas Harmonies (High-contrast scroll-stopping 2-3 color systems)
    "viral_royal_navy_gold": {
        "primary": (9, 26, 78, 255),       # Royal midnight navy (echoes diagonal corner)
        "accent": (176, 16, 28, 255),      # Punchy royal crimson OR amber-gold contrast
        "support": (34, 48, 86, 248),
        "detail": (62, 74, 108, 240),
        "strip_bg": (9, 26, 78, 255),      # Royal navy highlight strip
        "strip_fg": (253, 224, 71, 255),   # Luminous gold bold text inside navy strip
        "badge_bg": (9, 26, 78, 255),
        "badge_fg": (253, 224, 71, 255),   # Gold reference inside navy ribbon
        "underline": (196, 140, 12, 255),  # Brushed gold swoosh matching ribbon
        "is_dark_text": True,
    },
    "viral_cobalt_white_gold": {
        "primary": (255, 255, 255, 255),   # Crisp high-contrast pure white
        "accent": (250, 204, 21, 255),     # Electric solar gold matching wave
        "support": (226, 236, 252, 245),
        "detail": (198, 216, 246, 230),
        "strip_bg": (250, 204, 21, 255),   # High-voltage solar yellow strip
        "strip_fg": (6, 24, 78, 255),      # Deep royal cobalt ink inside yellow strip
        "badge_bg": (250, 204, 21, 255),
        "badge_fg": (6, 24, 78, 255),
        "underline": (250, 204, 21, 255),
        "is_dark_text": False,
    },
    "viral_emerald_forest_gold": {
        "primary": (6, 56, 24, 255),       # Deep forest evergreen ink
        "accent": (168, 24, 28, 255),      # Bold botanical red/terracotta contrast
        "support": (28, 72, 42, 248),
        "detail": (58, 92, 68, 240),
        "strip_bg": (6, 56, 24, 255),      # Deep emerald paint strip
        "strip_fg": (253, 224, 71, 255),   # Radiant gold text inside emerald strip
        "badge_bg": (6, 56, 24, 255),
        "badge_fg": (255, 255, 255, 255),
        "underline": (106, 168, 22, 255),  # Vibrant lime-leaf swoosh matching wave
        "is_dark_text": True,
    },
    "viral_crimson_parchment_bold": {
        "primary": (20, 20, 24, 255),      # Stark obsidian black ink
        "accent": (184, 12, 20, 255),      # High-voltage scarlet red matching wave
        "support": (52, 48, 46, 248),
        "detail": (78, 70, 66, 240),
        "strip_bg": (184, 12, 20, 255),    # Vivid crimson highlight strip
        "strip_fg": (255, 255, 255, 255),  # Crisp white bold text inside strip
        "badge_bg": (184, 12, 20, 255),
        "badge_fg": (255, 255, 255, 255),
        "underline": (184, 12, 20, 255),
        "is_dark_text": True,
    },
    "viral_sunburst_espresso_amber": {
        "primary": (34, 20, 12, 255),      # Rich warm espresso ink
        "accent": (164, 26, 18, 255),      # Deep sunlit crimson-copper
        "support": (62, 42, 28, 248),
        "detail": (86, 62, 44, 240),
        "strip_bg": (34, 20, 12, 255),     # Espresso brush strip
        "strip_fg": (253, 224, 71, 255),   # Bright sunlit gold inside strip
        "badge_bg": (34, 20, 12, 255),
        "badge_fg": (253, 224, 71, 255),
        "underline": (186, 68, 12, 255),   # Warm solar copper arc
        "is_dark_text": True,
    },
    "viral_terracotta_amber": {
        "primary": (28, 25, 23, 255),      # Deep espresso carbon ink
        "accent": (154, 52, 18, 255),      # Rich burnt terracotta (#9A3412)
        "support": (68, 60, 56, 248),      # Warm umber slate
        "detail": (87, 83, 78, 240),       # Warm stone gray
        "strip_bg": (154, 52, 18, 255),    # Terracotta highlight brush strip
        "strip_fg": (255, 251, 235, 255),  # Crisp warm ivory inside strip
        "badge_bg": (154, 52, 18, 255),    # Terracotta reference badge
        "badge_fg": (255, 251, 235, 255),
        "underline": (217, 119, 6, 255),   # Burnt amber brush arc (#D97706)
        "is_dark_text": True,
    },
    "light_terracotta_amber": {
        "primary": (36, 20, 14, 255),      # Warm dark walnut ink
        "accent": (140, 42, 14, 255),      # High-contrast terracotta accent
        "support": (62, 44, 34, 248),
        "detail": (82, 62, 50, 240),
        "strip_bg": (154, 52, 18, 255),    # Terracotta strip
        "strip_fg": (255, 251, 235, 255),
        "badge_bg": (154, 52, 18, 255),
        "badge_fg": (255, 251, 235, 255),
        "underline": (217, 119, 6, 255),   # Burnt amber underline
        "is_dark_text": True,
    },
    "dark_terracotta_amber": {
        "primary": (255, 251, 235, 255),   # Warm ivory cream
        "accent": (245, 158, 11, 255),     # Luminous burnt amber
        "support": (253, 230, 198, 244),   # Soft warm parchment tint
        "detail": (231, 212, 190, 228),
        "strip_bg": (154, 52, 18, 255),    # Terracotta strip
        "strip_fg": (255, 251, 235, 255),  # Ivory inside strip
        "badge_bg": (217, 119, 6, 255),    # Burnt amber badge
        "badge_fg": (28, 25, 23, 255),     # Espresso ink on amber pill
        "underline": (245, 158, 11, 255),
        "is_dark_text": False,
    },
}


def detect_emotional_tone(headline: str, subline: str = "") -> str:
    """Infers emotional tone from quote keywords when not explicitly specified."""
    text = f"{headline} {subline}".lower()
    if any(w in text for w in ["faith", "hope", "trust", "mountain", "climb", "keep going", "strength", "never alone"]):
        return "encouragement"
    if any(w in text for w in ["cross", "grace", "love", "mercy", "worship", "still", "peace", "rest", "shepherd"]):
        return "grace"
    if any(w in text for w in ["word", "lamp", "light", "truth", "wisdom", "secret", "pray", "spirit"]):
        return "reflection"
    if any(w in text for w in ["victory", "conqueror", "overcome", "breakthrough", "glory", "rise", "crown", "king"]):
        return "victory"
    if any(w in text for w in ["plant", "seed", "harvest", "settle", "stop", "command", "repent", "obey", "beware"]):
        return "authority"
    return "reflection"


def extract_emphasized_words(headline: str, max_words: int = 3) -> List[str]:
    """
    Intelligently selects 1-3 high-impact emotional anchor words from headline
    if the editorial engine did not supply an explicit emphasis list.
    """
    words = headline.strip().split()
    if not words:
        return []
    if len(words) <= 3:
        return [words[-1]]

    # Priority spiritual anchor words
    power_nouns = {
        "faith", "grace", "god", "jesus", "christ", "cross", "glory", "lord", "peace",
        "light", "lamp", "word", "spirit", "prayer", "pray", "worship", "hope", "love",
        "victory", "conqueror", "strength", "fire", "life", "eternal", "breakthrough",
        "surrender", "seeds", "harvest", "still", "alive", "power", "mercy", "secret"
    }
    clean_matches = []
    for w in words:
        core = re.sub(r'^[^\w]+|[^\w]+$', '', w.lower())
        if core in power_nouns and w not in clean_matches:
            clean_matches.append(w)

    if clean_matches:
        return clean_matches[:max_words]

    # Fallback: final 2 impact words
    return [" ".join(words[-2:])]


def select_art_direction(
    tone: Optional[str],
    background_archetype: str,
    headline: str,
    accent_color_hint: str = "yellow",
    explicit_style: Optional[str] = None,
    bg_luminance: Optional[float] = None
) -> Dict:
    """
    Selects the optimal Style System (A-E), Color Harmony, and Subject Safe Zone.
    Automatically adapts light/dark ink polarity to match photographic luminance so typography
    integrates organically rather than slapping dark mud scrims over bright daylight skies.
    """
    resolved_tone = (tone or detect_emotional_tone(headline)).lower().strip()

    # Select Typography Style System
    chosen_style = None
    if explicit_style and explicit_style in TYPOGRAPHY_STYLES:
        chosen_style = TYPOGRAPHY_STYLES[explicit_style]
    else:
        for style_def in TYPOGRAPHY_STYLES.values():
            if resolved_tone in style_def["tones"]:
                chosen_style = style_def
                break
        if chosen_style is None:
            chosen_style = TYPOGRAPHY_STYLES["reflection_editorial"]

    # Determine Background Profile & Polarity
    bg_profile = BACKGROUND_PROFILES.get(background_archetype, {
        "polarity": "dark",
        "zones": {
            "4:5":  {"x1": 0.09, "y1": 0.08, "x2": 0.91, "y2": 0.52, "align": "center"},
            "1:1":  {"x1": 0.09, "y1": 0.08, "x2": 0.91, "y2": 0.54, "align": "center"},
            "9:16": {"x1": 0.09, "y1": 0.14, "x2": 0.91, "y2": 0.50, "align": "center"},
        },
    })

    if bg_luminance is not None:
        use_light_polarity = bg_luminance >= 0.30
    else:
        use_light_polarity = bg_profile["polarity"] in ("light_sky", "light_wall")

    # Match Approved High-Contrast Viral Color Harmony (Canvas-Aware First!)
    ARCHETYPE_HARMONY_MAP = {
        "diagonal_royal_gold": "viral_royal_navy_gold",
        "deep_cobalt_wave": "viral_cobalt_white_gold",
        "emerald_white_wave": "viral_emerald_forest_gold",
        "crimson_cream_wave": "viral_crimson_parchment_bold",
        "golden_sunburst_clouds": "viral_sunburst_espresso_amber",
        "terracotta_amber_wave": "viral_terracotta_amber",
    }
    hint = (accent_color_hint or "terracotta").lower()
    if background_archetype in ARCHETYPE_HARMONY_MAP:
        harmony = COLOR_HARMONIES[ARCHETYPE_HARMONY_MAP[background_archetype]]
        use_light_polarity = harmony["is_dark_text"]
    elif use_light_polarity:
        if hint in ("terracotta", "amber"):
            harmony = COLOR_HARMONIES["light_terracotta_amber"]
        elif chosen_style["id"] == "authority_condensed":
            harmony = COLOR_HARMONIES["light_charcoal_red"]
        else:
            harmony = COLOR_HARMONIES["light_navy_crimson"]
    else:
        if hint in ("terracotta", "amber"):
            harmony = COLOR_HARMONIES["dark_terracotta_amber"]
        elif hint == "red":
            harmony = COLOR_HARMONIES["dark_white_crimson"]
        elif chosen_style["id"] in ("grace_calligraphy", "reflection_editorial") and hint == "gold":
            harmony = COLOR_HARMONIES["dark_cream_gold"]
        else:
            harmony = COLOR_HARMONIES["dark_white_gold"]

    return {
        "tone": resolved_tone,
        "style": chosen_style,
        "harmony": harmony,
        "zones": bg_profile["zones"],
        "is_light_bg": use_light_polarity,
    }
