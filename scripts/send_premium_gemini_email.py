"""
Premium Gospel Content & Gemini AI Flyer Email Dispatcher
Builds a high-end, responsive HTML magazine email newsletter
with embedded Google Gemini flyers and platform-native captions.
"""

import argparse
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

def load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.is_file():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception as e:
            print(f"[DEBUG] Could not load .env: {e}", file=sys.stderr)

def build_newsletter_html(square_cid: str, story_cid: str, twitter_cid: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Gospel Trends & Multi-Platform Distribution</title>
</head>
<body style="margin: 0; padding: 20px 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; -webkit-font-smoothing: antialiased;">
  
  <!-- Outer Wrapper -->
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f1f5f9;">
    <tr>
      <td align="center">
        
        <!-- Main Card Container (Max 680px) -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; margin: 20px auto;">
          
          <!-- HERO HEADER -->
          <tr>
            <td style="background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #312e81 100%); padding: 36px 32px; text-align: center;">
              <span style="display: inline-block; background-color: rgba(245, 158, 11, 0.18); border: 1px solid #f59e0b; color: #fbbf24; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; padding: 5px 14px; border-radius: 50px; text-transform: uppercase; margin-bottom: 14px;">
                ✨ Powered by Google Gemini AI
              </span>
              <h1 style="color: #ffffff; font-size: 26px; font-weight: 800; line-height: 1.3; margin: 0 0 10px 0; letter-spacing: -0.5px;">
                🕊️ Daily Gospel Trends & Multi-Platform Media Kit
              </h1>
              <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5; margin: 0 auto; max-width: 520px;">
                Curated viral YouTube insights, Google Gemini flyer artwork, and ready-to-publish captions for Facebook, Instagram, WhatsApp, Twitter/X, and Threads.
              </p>
            </td>
          </tr>

          <!-- MAIN BODY CONTENT -->
          <tr>
            <td style="padding: 32px 28px;">

              <!-- SECTION: GEMINI AI FLYER SPOTLIGHT -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 36px;">
                <tr>
                  <td>
                    <div style="border-left: 4px solid #f59e0b; padding-left: 12px; margin-bottom: 16px;">
                      <h2 style="color: #0f172a; font-size: 20px; font-weight: 800; margin: 0;">🎨 Google Gemini AI Flyer Spotlight</h2>
                      <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Custom celestial sacred artwork with quote overlay and native typography.</p>
                    </div>

                    <!-- Flyer Hero Card -->
                    <div style="background-color: #0b0f19; border-radius: 14px; overflow: hidden; border: 1px solid #1e293b; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
                      <div style="padding: 12px 16px; background-color: #090d16; color: #fbbf24; font-size: 12px; font-weight: 700; text-align: left; letter-spacing: 0.5px; border-bottom: 1px solid #1e293b;">
                        🌟 Featured Master Flyer (Square 1080x1080)
                      </div>
                      <div style="padding: 16px;">
                        <img src="cid:{square_cid}" alt="Google Gemini Gospel Flyer" style="max-width: 100%; height: auto; border-radius: 10px; display: block; margin: 0 auto; box-shadow: 0 6px 20px rgba(0,0,0,0.4);" />
                      </div>
                      <div style="padding: 12px 20px; background-color: #090d16; border-top: 1px solid #1e293b; text-align: left;">
                        <p style="color: #e2e8f0; font-size: 13px; font-style: italic; margin: 0 0 4px 0;">
                          “What is birthed in the secret place cannot be extinguished by public storms.”
                        </p>
                        <p style="color: #94a3b8; font-size: 11px; margin: 0;">
                          — Apostle Joshua Selman & Dunsin Oyekan • Psalm 91:1
                        </p>
                      </div>
                    </div>

                    <!-- Alternate formats alert -->
                    <div style="margin-top: 12px; background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #475569;">
                      📎 <strong>Attachments Included:</strong> High-res <strong>Story/Status (9:16)</strong> and <strong>Twitter (16:9)</strong> formats are also attached to this email ready for download!
                    </div>
                  </td>
                </tr>
              </table>

              <!-- SECTION: YOUTUBE VIRAL TRENDS (PREVIOUS 24H) -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 36px;">
                <tr>
                  <td>
                    <div style="border-left: 4px solid #3b82f6; padding-left: 12px; margin-bottom: 16px;">
                      <h2 style="color: #0f172a; font-size: 20px; font-weight: 800; margin: 0;">📈 Viral YouTube Gospel Trends (Previous 24 Hours)</h2>
                      <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Top trending releases and spiritual immersions analyzed for today's repurposing:</p>
                    </div>

                    <!-- Grid of 4 Trend Cards -->
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <!-- Trend 1 -->
                        <td width="50%" valign="top" style="padding: 0 8px 12px 0;">
                          <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; height: 100%;">
                            <span style="display: inline-block; background-color: #fee2e2; color: #dc2626; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; margin-bottom: 6px;">Viral Praise</span>
                            <h4 style="margin: 0 0 4px 0; font-size: 14px; color: #0f172a;">Moses Bliss: Mercy Experience</h4>
                            <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">High-energy praise party, joyful thanksgiving, and corporate praise as a spiritual warfare weapon.</p>
                          </div>
                        </td>
                        <!-- Trend 2 -->
                        <td width="50%" valign="top" style="padding: 0 0 12px 8px;">
                          <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; height: 100%;">
                            <span style="display: inline-block; background-color: #e0e7ff; color: #4338ca; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; margin-bottom: 6px;">Soaking Prayer</span>
                            <h4 style="margin: 0 0 4px 0; font-size: 14px; color: #0f172a;">Dunsin Oyekan & Theophilus Sunday</h4>
                            <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">Atmospheric prayer tarrying, personal consecration, and rebuilding the private altar of devotion.</p>
                          </div>
                        </td>
                      </tr>
                      <tr>
                        <!-- Trend 3 -->
                        <td width="50%" valign="top" style="padding: 0 8px 0 0;">
                          <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; height: 100%;">
                            <span style="display: inline-block; background-color: #fef3c7; color: #b45309; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; margin-bottom: 6px;">Spiritual Insight</span>
                            <h4 style="margin: 0 0 4px 0; font-size: 14px; color: #0f172a;">Apostle Joshua Selman (Koinonia)</h4>
                            <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">Kingdom surrender preceding divine authority; cultivating internal spiritual resilience.</p>
                          </div>
                        </td>
                        <!-- Trend 4 -->
                        <td width="50%" valign="top" style="padding: 0 0 0 8px;">
                          <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; height: 100%;">
                            <span style="display: inline-block; background-color: #dcfce7; color: #15803d; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; margin-bottom: 6px;">Global Worship</span>
                            <h4 style="margin: 0 0 4px 0; font-size: 14px; color: #0f172a;">Elevation Worship: 'Been So Good'</h4>
                            <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">Acoustic worship ministration reflecting on God's unwavering track record through every trial.</p>
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- SECTION: PLATFORM 1 - FACEBOOK -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 30px;">
                <tr>
                  <td>
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                      <div style="background-color: #1877f2; padding: 12px 18px; color: #ffffff;">
                        <table width="100%" cellspacing="0" cellpadding="0">
                          <tr>
                            <td style="font-weight: 700; font-size: 15px; color: #ffffff;">📘 FACEBOOK POST</td>
                            <td align="right" style="font-size: 12px; color: #dbeafe;">Community & Storytelling Standard</td>
                          </tr>
                        </table>
                      </div>
                      <div style="padding: 20px;">
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          Have you ever felt like you're fighting battles in public while neglecting your secret place?
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          Listening to the latest ministrations from Apostle Joshua Selman and Dunsin Oyekan this week brought home a timeless truth that every believer needs to hold onto:
                        </p>
                        <div style="background-color: #eff6ff; border-left: 3px solid #1877f2; padding: 12px 16px; margin: 14px 0; font-style: italic; color: #1e3a8a; font-size: 14px; font-weight: 600;">
                          “What is birthed in the secret place cannot be extinguished by public storms.”
                        </div>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          In our fast-paced lives, it's so easy to focus on external performance—showing up strong for family, work, and community—while letting our personal devotion run on empty. But spiritual authority and peace don't come from striving; they flow from surrender.<br><br>
                          When you invest time in prayer, praise, and quiet reflection behind closed doors, God builds a quiet resilience inside you that no sudden crisis can shake.
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          Take 15 minutes today to disconnect from the noise, open your Bible, and rebuild your altar of prayer.
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #1e293b; font-weight: 600; margin: 0 0 14px 0;">
                          👉 How do you guard your quiet time with God when life gets busy? Share your thoughts below in the comments to encourage someone today! 👇
                        </p>
                        <div style="background-color: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 12px; color: #64748b;">
                          <strong>Hashtags:</strong> #FaithJourney #SecretPlace #DailyDevotion #ChristianLiving
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- SECTION: PLATFORM 2 - INSTAGRAM -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 30px;">
                <tr>
                  <td>
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                      <div style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); padding: 12px 18px; color: #ffffff;">
                        <table width="100%" cellspacing="0" cellpadding="0">
                          <tr>
                            <td style="font-weight: 700; font-size: 15px; color: #ffffff;">📸 INSTAGRAM POST</td>
                            <td align="right" style="font-size: 12px; color: #ffe4e6;">Visual Carousel & Save Standard</td>
                          </tr>
                        </table>
                      </div>
                      <div style="padding: 20px;">
                        <p style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 0 0 10px 0;">
                          Most people pray for a public breakthrough.<br>
                          Very few people build the altar to sustain it. 🕊️
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          When life feels overwhelming, our natural instinct is to scramble for quick fixes. But if there’s one recurring truth from the most powerful worship ministrations and sermons this week, it's this:
                        </p>
                        <div style="background-color: #fff1f2; border-left: 3px solid #e11d48; padding: 12px 16px; margin: 14px 0; color: #881337; font-size: 13px; line-height: 1.6;">
                          <strong>1️⃣ Praise is a weapon, not an emotional reaction:</strong> Rejoicing in the trial enforces kingdom victory.<br>
                          <strong>2️⃣ Surrender precedes authority:</strong> God entrusts spiritual power to aligned hearts.<br>
                          <strong>3️⃣ Intimacy over performance:</strong> Anchored devotion cannot be uprooted by public winds.
                        </div>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          📌 <strong>SAVE this post</strong> for when you need a reminder during a hectic week.<br>
                          ✈️ <strong>SHARE this</strong> to your story or send it to someone walking through a challenging season right now.
                        </p>
                        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 10px 14px; border-radius: 6px; font-size: 12px; color: #64748b; line-height: 1.6;">
                          #GospelMusic #WorshipLeader #ChristianQuotes #DailyDevotional #ApostleJoshuaSelman #DunsinOyekan #MosesBliss #FaithOverFear #PrayerAltar #SpiritualGrowth #HolySpirit #SecretPlace #KingdomMindset
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- SECTION: PLATFORM 3 - WHATSAPP -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 30px;">
                <tr>
                  <td>
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                      <div style="background-color: #25d366; padding: 12px 18px; color: #ffffff;">
                        <table width="100%" cellspacing="0" cellpadding="0">
                          <tr>
                            <td style="font-weight: 700; font-size: 15px; color: #ffffff;">💬 WHATSAPP BROADCAST & STATUS</td>
                            <td align="right" style="font-size: 12px; color: #dcfce7;">Status & Group Broadcast Standard</td>
                          </tr>
                        </table>
                      </div>
                      <div style="padding: 20px;">
                        <div style="background-color: #efeae2; border-radius: 10px; padding: 16px; border: 1px solid #e6ded3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                          <div style="background-color: #ffffff; border-radius: 8px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); font-size: 14px; line-height: 1.7; color: #111b21;">
                            🕊️ <strong>MORNING WORD FOR TODAY</strong><br><br>
                            <em>“What is birthed in the secret place cannot be extinguished by public storms.”</em><br><br>
                            Friend, before you rush into today's tasks, take a minute to meditate on this:<br><br>
                            • <strong>Praise is your weapon:</strong> Even when things look uncertain, choose to thank God first (Acts 16:25).<br>
                            • <strong>Guard your quiet time:</strong> Jesus always withdrew to quiet places to pray (Luke 5:16).<br>
                            • <strong>Cast your burdens:</strong> You were never meant to carry life's pressures alone (1 Peter 5:7).<br><br>
                            📖 <strong>Scripture Anchor:</strong><br>
                            <em>“He who dwells in the secret place of the Most High shall abide under the shadow of the Almighty.”</em> — Psalm 91:1<br><br>
                            📲 <em>Status Tip: Post the attached vertical flyer to your WhatsApp Status this morning!</em><br>
                            📤 <em>Forward this to 3 people who need peace and encouragement today.</em> 🙏✨
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- SECTION: PLATFORM 4 - TWITTER / X -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 30px;">
                <tr>
                  <td>
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                      <div style="background-color: #000000; padding: 12px 18px; color: #ffffff;">
                        <table width="100%" cellspacing="0" cellpadding="0">
                          <tr>
                            <td style="font-weight: 700; font-size: 15px; color: #ffffff;">🐦 TWITTER / X THREAD</td>
                            <td align="right" style="font-size: 12px; color: #94a3b8;">High-Velocity Thread Standard</td>
                          </tr>
                        </table>
                      </div>
                      <div style="padding: 20px;">
                        
                        <!-- Tweet 1 -->
                        <div style="border-left: 2px solid #e2e8f0; padding-left: 14px; margin-bottom: 16px;">
                          <span style="font-size: 11px; font-weight: 700; color: #3b82f6; text-transform: uppercase;">Tweet 1 (Hook + Flier)</span>
                          <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                            Most people pray for breakthrough.<br>
                            Few prepare their hearts to carry it.<br><br>
                            Here are 3 spiritual principles drawn from the most viral worship ministrations and teachings from the past 24 hours: 🧵👇<br>
                            <em>[Attach: gemini_flyer_twitter.jpg]</em>
                          </p>
                        </div>

                        <!-- Tweet 2 -->
                        <div style="border-left: 2px solid #e2e8f0; padding-left: 14px; margin-bottom: 16px;">
                          <span style="font-size: 11px; font-weight: 700; color: #3b82f6; text-transform: uppercase;">Tweet 2</span>
                          <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                            1/ Praise is not an emotional reaction—it's a tactical weapon.<br><br>
                            When you see worshippers rejoicing in the midst of uncertainty, it's not denial of reality. It's alignment with divine victory.
                          </p>
                        </div>

                        <!-- Tweet 3 -->
                        <div style="border-left: 2px solid #e2e8f0; padding-left: 14px; margin-bottom: 16px;">
                          <span style="font-size: 11px; font-weight: 700; color: #3b82f6; text-transform: uppercase;">Tweet 3</span>
                          <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                            2/ Tarrying in the secret place cannot be outsourced.<br><br>
                            What you cultivate in hidden prayer produces the fruit that sustains you in public adversity. Build your altar first.
                          </p>
                        </div>

                        <!-- Tweet 4 -->
                        <div style="border-left: 2px solid #3b82f6; padding-left: 14px;">
                          <span style="font-size: 11px; font-weight: 700; color: #3b82f6; text-transform: uppercase;">Tweet 4 (CTA)</span>
                          <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                            3/ Surrender always precedes authority.<br><br>
                            God doesn't need your self-made ambition; He desires your yielded alignment.<br><br>
                            Drop an "Amen" if this speaks to your season today! 🙏
                          </p>
                        </div>

                      </div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- SECTION: PLATFORM 5 - THREADS -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 24px;">
                <tr>
                  <td>
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                      <div style="background-color: #101010; padding: 12px 18px; color: #ffffff;">
                        <table width="100%" cellspacing="0" cellpadding="0">
                          <tr>
                            <td style="font-weight: 700; font-size: 15px; color: #ffffff;">🧵 THREADS POST</td>
                            <td align="right" style="font-size: 12px; color: #a1a1aa;">Conversational & Authentic Standard</td>
                          </tr>
                        </table>
                      </div>
                      <div style="padding: 20px;">
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          A quick thought after listening to recent worship sets from Dunsin Oyekan and Apostle Selman this morning:
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          You really can't pour from a cup that has run dry.
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          Too many of us treat our prayer life like an emergency room rather than a daily dining table. We only show up when something breaks.
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                          What changes your entire week is shifting from panic-praying to daily dwelling. Ten quiet minutes of unhurried thanksgiving before looking at your phone does more for your mental clarity than an hour of scrolling.
                        </p>
                        <p style="font-size: 14px; line-height: 1.7; color: #0f172a; font-weight: 600; margin: 0;">
                          How do you protect your peace when your schedule gets packed?
                        </p>
                      </div>
                    </div>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 24px; text-align: center;">
              <p style="color: #64748b; font-size: 12px; margin: 0 0 6px 0;">
                Gospel Automation Media Engine • Generated with Google Gemini AI
              </p>
              <p style="color: #94a3b8; font-size: 11px; margin: 0;">
                Delivered automatically to <strong>aondoaseerezekiel@gmail.com</strong>
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""

def send_premium_gemini_email(recipient: str, subject: str, fliers_dir: Path):
    load_env_file()
    
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip().replace(" ", "")

    if not smtp_user or not smtp_pass:
        print("[ERROR] SMTP_USER or SMTP_PASSWORD not found in environment or .env", file=sys.stderr)
        return False

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"Gospel Media Engine <{smtp_user}>"
    msg["To"] = recipient

    square_path = fliers_dir / "gemini_flyer_square.jpg"
    story_path = fliers_dir / "gemini_flyer_story.jpg"
    twitter_path = fliers_dir / "gemini_flyer_twitter.jpg"
    raw_ai_path = fliers_dir / "gemini_gospel_flyer.jpg"

    square_cid = "gemini_flyer_square"
    story_cid = "gemini_flyer_story"
    twitter_cid = "gemini_flyer_twitter"

    html_content = build_newsletter_html(square_cid, story_cid, twitter_cid)
    
    # Text fallback
    plain_text = "Daily Gospel Trends & Multi-Platform Distribution Kit. Please enable HTML email view to view the Gemini AI flyers and formatted media kit."
    
    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach images
    for cid, img_file in [
        (square_cid, square_path),
        (story_cid, story_path),
        (twitter_cid, twitter_path),
        ("gemini_raw_art", raw_ai_path)
    ]:
        if img_file.is_file():
            try:
                with open(img_file, "rb") as f:
                    mime_img = MIMEImage(f.read(), _subtype="jpeg")
                    mime_img.add_header("Content-ID", f"<{cid}>")
                    mime_img.add_header("Content-Disposition", "inline", filename=img_file.name)
                    msg.attach(mime_img)
                    print(f"[ATTACHED] {img_file.name}")
            except Exception as e:
                print(f"[WARNING] Failed to attach {img_file}: {e}", file=sys.stderr)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=45) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
        print(f"[SUCCESS] Premium Gemini Email successfully delivered to {recipient}")
        return True
    except Exception as e:
        print(f"[ERROR] Email delivery failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    fliers_dir = Path("C:/Users/ezeki/.gemini/antigravity/scratch/gospel-content-automation/reports/fliers")
    send_premium_gemini_email(
        recipient="aondoaseerezekiel@gmail.com",
        subject="🕊️ Google Gemini AI Gospel Media Kit & Viral Fliers (Live Upgrade)",
        fliers_dir=fliers_dir
    )
