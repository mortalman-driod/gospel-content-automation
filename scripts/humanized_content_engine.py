"""
Humanized Editorial Content & Caption Engine
Synthesizes de-AI'd editorial micro-essays and bespoke captions for 5 platforms:
Instagram, WhatsApp, X (Twitter), Threads, and Facebook.
Strictly eliminates robotic outlines, formulaic bullet points, and AI clichés.
"""

import re
from datetime import datetime

class HumanizedContentEngine:
    def __init__(self, quote: str, speaker: str = None, scripture: str = None, title: str = None):
        self.quote = quote.strip()
        self.speaker = speaker or "Nathaniel Bassey & Apostle Joshua Selman"
        self.scripture = scripture or "Psalm 46:5 • Isaiah 40:31"
        self.title = title or self._derive_title(self.quote)

    def _derive_title(self, quote: str) -> str:
        # Check for natural comma clause
        if "," in quote:
            first_clause = quote.split(",")[0].strip()
            if len(first_clause.split()) <= 7:
                return first_clause.title()
        words = quote.split()
        if len(words) <= 6:
            return quote.title()
        return " ".join(words[:6]).title()

    def generate_editorial_micro_essay(self) -> dict:
        """Constructs a high-class literary essay without any robotic AI hallmarks."""
        title = self.title
        today_date = datetime.now().strftime("%A, %B %d, %Y")

        essay = (
            f"There are seasons in every believer's journey where human vocabulary reaches its natural limit. "
            f"You begin your morning with matters that cannot be easily articulated in a bulleted prayer list, "
            f"and the weight of what you carry defies simplistic explanations.\n\n"
            f"In the eighth chapter of Romans, the Apostle Paul provides a profound consolation for this exact posture: "
            f"the Spirit Himself makes intercession for us with groanings that cannot be uttered. "
            f"The kingdom has never demanded that you produce polished eloquence before God can act on your behalf. "
            f"God does not listen for the perfection of your sentences; He responds to the genuine surrender of your heart.\n\n"
            f"Throughout Scripture, whenever human capacity ran completely dry, heaven introduced a higher sound. "
            f"At the fourth watch of the night, when exhaustion was deepest, divine help arrived. "
            f"When Jehoshaphat had no military solution left, worshippers were sent to the front lines. "
            f"When Paul and Silas were locked in the deepest dungeon with their backs bleeding, they did not debate their circumstances—they began to sing hymns to God at midnight.\n\n"
            f"Drawing from today's live worship ministrations across our fellowship, the spiritual truth is liberating: "
            f"<strong>{self.quote}</strong> When human striving stops, divine intervention takes over. "
            f"You do not have to carry anxiety into today. Lay down the need to orchestrate the outcome, and let your worship establish His peace."
        )

        return {
            "title": title,
            "subtitle": f"On letting faith speak when human words fail, the mystery of the secret place, and divine help in quiet seasons.",
            "essay_paragraphs": essay.split("\n\n"),
            "date_str": today_date
        }

    def generate_multi_platform_captions(self) -> dict:
        """Generates platform-tailored copy for all 5 social destinations."""
        quote = self.quote
        speaker = self.speaker
        scripture = self.scripture

        # 1. Instagram: Hook in first 75 chars, generous line breaks, 14 targeted hashtags
        instagram = (
            f"{quote}.\n\n"
            f"There are days when human vocabulary isn't enough. You don't have the words to explain the pressure, "
            f"and you don't have the energy to formulate a polished argument.\n\n"
            f"Here is what Scripture reminds us in Romans 8:26: The Spirit Himself intercedes for us with groanings that words cannot express.\n\n"
            f"God never asked you to carry every outcome on your own shoulders. When human striving stops, worship takes over.\n\n"
            f"Take 2 minutes this morning to step away from the noise, anchor your heart in His presence, and remember who remains on the throne.\n\n"
            f"“{quote}”\n"
            f"— {scripture} • {speaker}\n\n"
            f"#DivineHelp #WorshipInSpirit #SecretPlace #MorningPrayer #ApostleJoshuaSelman #VictoriaOrenze "
            f"#NathanielBassey #MercyChinwo #FaithOverFear #KingdomMindset #ChristianCreatives #NigerianGospel #PraiseAndWorship #DailyWord"
        )

        # 2. WhatsApp: Warm, personal pastoral broadcast
        whatsapp = (
            f"Good morning my friend. A quiet word for your morning:\n\n"
            f"“{quote}”\n\n"
            f"If you've felt drained, overwhelmed, or unsure of what to pray today, don't force human striving. "
            f"God hears the posture of your heart louder than any spoken sentence.\n\n"
            f"📖 “The Lord is near to all who call upon Him in truth.” — Psalm 145:18\n\n"
            f"Step into today with peace. Forward this to someone who needs strength this morning! ✨"
        )

        # 3. X (Twitter): Sharp, memorable, under 240 chars
        twitter = (
            f"{quote}.\n\n"
            f"When human capacity reaches its limit, you don't need louder arguments—you need deeper surrender.\n\n"
            f"Rest in His covenant today. 🕊️"
        )
        if len(twitter) > 260:
            twitter = f"{quote}.\n\nWhen human striving stops, worship takes over. Rest in His covenant today. 🕊️"

        # 4. Threads: Narrative inquiry with community prompt
        threads = (
            f"A quiet thought for this morning:\n\n"
            f"Most people think prayer is only effective when they have all the right words.\n\n"
            f"Scripture teaches the opposite. In Romans 8:26, the deepest intercession happens when human words run dry and the Spirit steps in.\n\n"
            f"{quote}.\n\n"
            f"Whatever feels heavy right now, you don't have to carry it alone. What are you trusting God for today?"
        )

        # 5. Facebook: Thoughtful community devotional
        facebook = (
            f"“{quote}” ({scripture})\n\n"
            f"There are seasons when human capacity reaches its end, and words simply are not enough. "
            f"In those moments, your worship becomes your deepest prayer. When you choose thanksgiving in the face of pressure, "
            f"you anchor your soul in God's unbroken peace.\n\n"
            f"May His strength meet you at the point of your need today. Have a blessed and favored day!"
        )

        return {
            "instagram": instagram,
            "whatsapp": whatsapp,
            "twitter": twitter,
            "threads": threads,
            "facebook": facebook
        }

if __name__ == "__main__":
    engine = HumanizedContentEngine(
        quote="When words are not enough, let your worship speak",
        speaker="Mercy Chinwo & Apostle Joshua Selman",
        scripture="Romans 8:26 • Psalm 46:10"
    )
    essay = engine.generate_editorial_micro_essay()
    captions = engine.generate_multi_platform_captions()
    print("=== ESSAY TITLE ===")
    print(essay["title"])
    print("\n=== TWITTER CAPTION ===")
    print(captions["twitter"].encode("ascii", "replace").decode())
    print("\n=== INSTAGRAM HOOK ===")
    print(captions["instagram"][:120])
