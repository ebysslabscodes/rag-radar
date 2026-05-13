from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from collections import Counter


def _font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def generate_visual_summary(leads, subreddit_counts, output_path, run_date):
    width, height = 1400, 900
    bg = "#0E1117"
    card = "#161B22"
    orange = "#FF8A00"
    white = "#F5F5F5"
    gray = "#A7B0BE"
    muted = "#7D8590"

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    title_font = _font(52, bold=True)
    subtitle_font = _font(28)
    section_font = _font(28, bold=True)
    body_font = _font(24)
    small_font = _font(20)
    tiny_font = _font(16)

    # Header
    draw.text((70, 55), "RAG Radar — Weekly Signals", fill=white, font=title_font)
    draw.text(
        (72, 120),
        f"{run_date} · Retrieval reliability intelligence",
        fill=gray,
        font=subtitle_font,
    )

    # Main stat card
    draw.rounded_rectangle((70, 180, 420, 330), radius=22, fill=card)
    draw.text((100, 210), "Captured", fill=gray, font=section_font)
    draw.text((100, 255), f"{len(leads)}", fill=orange, font=_font(54, bold=True))
    draw.text((190, 270), "relevant discussions", fill=white, font=body_font)

    # Community card
    draw.rounded_rectangle((450, 180, 820, 330), radius=22, fill=card)
    draw.text((480, 210), "Communities", fill=gray, font=section_font)

    y = 252
    for name, count in sorted(
        subreddit_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        draw.text((485, y), f"r/{name}: {count}", fill=white, font=small_font)
        y += 28

    # Top themes
    theme_counter = Counter()
    emotion_counter = Counter()

    for lead in leads:
        for theme in lead.get("themes", []):
            theme_counter[theme] += 1
        for emotion in lead.get("emotions", []):
            emotion_counter[emotion] += 1

    draw.rounded_rectangle((70, 370, 675, 610), radius=22, fill=card)
    draw.text((100, 400), "Top recurring themes", fill=orange, font=section_font)

    y = 455
    for i, (theme, count) in enumerate(theme_counter.most_common(5), start=1):
        draw.text((105, y), f"{i}. {theme} ({count})", fill=white, font=body_font)
        y += 38

    # Emotional pattern
    draw.rounded_rectangle((725, 370, 1330, 610), radius=22, fill=card)
    draw.text(
        (755, 400), "Most common emotional pattern", fill=orange, font=section_font
    )

    top_emotion = (
        emotion_counter.most_common(1)[0] if emotion_counter else ("None detected", 0)
    )
    quote = f"“{top_emotion[0]}”"
    lines = _wrap_text(draw, quote, body_font, 520)

    y = 455
    for line in lines[:4]:
        draw.text((760, y), line, fill=white, font=body_font)
        y += 34

    draw.text(
        (760, 560), f"Detected {top_emotion[1]} times", fill=gray, font=small_font
    )

    # Top production signal
    top_lead = leads[0] if leads else {}
    draw.rounded_rectangle((70, 650, 1330, 810), radius=22, fill=card)
    draw.text((100, 680), "Top production signal", fill=orange, font=section_font)

    title = top_lead.get("title", "No lead detected")
    title_lines = _wrap_text(draw, title, body_font, 1000)

    y = 725
    for line in title_lines[:2]:
        draw.text((100, y), line, fill=white, font=body_font)
        y += 34

    final_score = top_lead.get("final_score", top_lead.get("score", 0))
    intent_score = top_lead.get("intent_score", 0)
    engagement_score = top_lead.get("engagement_score", 0)

    draw.text(
        (100, 780),
        f"Final score: {final_score}  ·  Intent: {intent_score}  ·  Engagement: {engagement_score}",
        fill=gray,
        font=small_font,
    )

    # Footer
    draw.text(
        (70, 850), "rag-radar · Ebysslabs · riswis.com", fill=muted, font=tiny_font
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
