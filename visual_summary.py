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


def _fit_text(draw, text, font, max_width):
    if draw.textlength(text, font=font) <= max_width:
        return text

    ellipsis = "..."

    while text and draw.textlength(text + ellipsis, font=font) > max_width:
        text = text[:-1]

    return text.strip() + ellipsis


def generate_visual_summary(
    leads,
    subreddit_counts,
    output_path,
    run_date,
    theme_trends=None,
    riswis_governance_match=None,
    governance_counts=None,
    trust_conflict_count=None,
    production_excerpt=None,
    severity_by_theme=None,
    rri=None,
):
    width, height = 1400, 1220

    bg = "#0E1117"
    card = "#161B22"
    orange = "#FF8A00"
    white = "#F5F5F5"
    gray = "#A7B0BE"
    muted = "#7D8590"
    badge_fill = "#222A33"
    red = "#FF4D4D"
    yellow = "#FFD166"
    green = "#3FB950"

    def severity_color(severity):
        if severity == "CRITICAL":
            return red
        if severity == "HIGH":
            return orange
        if severity == "MODERATE":
            return yellow
        return gray

    def trend_color(trend):
        if str(trend).startswith("↑"):
            return green
        if str(trend).startswith("↓"):
            return red
        return gray

    theme_trends = theme_trends or {}
    governance_counts = governance_counts or {}
    severity_by_theme = severity_by_theme or {}

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    title_font = _font(52, bold=True)
    subtitle_font = _font(28)
    section_font = _font(28, bold=True)
    section_font_small = _font(26, bold=True)
    body_font = _font(24)
    stat_label_font = _font(20)
    small_font = _font(20)
    tiny_font = _font(16)
    methodology_font = _font(13)

    draw.text((70, 55), "RAG Radar — Weekly Signals", fill=white, font=title_font)

    draw.text(
        (72, 120),
        f"{run_date} · Retrieval reliability intelligence",
        fill=gray,
        font=subtitle_font,
    )

    draw.rounded_rectangle((70, 180, 420, 370), radius=22, fill=card)
    draw.text((100, 215), "Signals", fill=gray, font=section_font)

    draw.text((100, 265), f"{len(leads)}", fill=orange, font=_font(54, bold=True))
    draw.text((195, 282), "relevant", fill=white, font=stat_label_font)
    draw.text((195, 307), "retrieval discussions", fill=white, font=stat_label_font)

    rri_label = f"RRI: {rri}/100" if rri is not None else "RRI: N/A"
    draw.text((100, 340), rri_label, fill=gray, font=tiny_font)

    draw.rounded_rectangle((450, 180, 820, 370), radius=22, fill=card)
    draw.text((480, 215), "Trust Conflicts", fill=gray, font=section_font_small)

    trust_label = (
        str(trust_conflict_count) if trust_conflict_count is not None else "N/A"
    )

    draw.text((480, 265), trust_label, fill=orange, font=_font(54, bold=True))
    draw.text((570, 282), "discussions", fill=white, font=stat_label_font)
    draw.text((570, 307), "flagged this week", fill=white, font=stat_label_font)

    draw.rounded_rectangle((850, 180, 1330, 370), radius=22, fill=card)
    draw.text((880, 215), "RISWIS Governance Match", fill=gray, font=section_font_small)

    governance_label = (
        f"{riswis_governance_match}%" if riswis_governance_match is not None else "N/A"
    )

    draw.text((880, 265), governance_label, fill=orange, font=_font(48, bold=True))
    draw.text((1000, 278), "mapped to", fill=white, font=stat_label_font)
    draw.text((1000, 303), "governance controls", fill=white, font=stat_label_font)

    theme_counter = Counter()
    emotion_counter = Counter()

    for lead in leads:
        for theme in lead.get("themes", []):
            theme_counter[theme] += 1

        for emotion in lead.get("emotions", []):
            emotion_counter[emotion] += 1

    draw.rounded_rectangle((70, 405, 675, 690), radius=22, fill=card)

    draw.text(
        (100, 435),
        "Tracked production failure themes",
        fill=orange,
        font=section_font_small,
    )

    y = 495

    for i, (theme, count) in enumerate(theme_counter.most_common(5), start=1):
        severity = severity_by_theme.get(theme, "LOW")
        theme_line = _fit_text(
            draw,
            f"{i}. {theme} ({count}) — {severity}",
            body_font,
            535,
        )
        draw.text(
            (105, y),
            theme_line,
            fill=severity_color(severity),
            font=body_font,
        )
        y += 39

    draw.rounded_rectangle((725, 405, 1330, 690), radius=22, fill=card)

    draw.text(
        (755, 435),
        "Most common production sentiment",
        fill=orange,
        font=section_font_small,
    )

    top_emotion = (
        emotion_counter.most_common(1)[0] if emotion_counter else ("None detected", 0)
    )

    quote = f"“{top_emotion[0]}”"
    lines = _wrap_text(draw, quote, body_font, 520)

    y = 495

    for line in lines[:4]:
        draw.text((760, y), line, fill=white, font=body_font)
        y += 35

    draw.text(
        (760, 615),
        f"Detected {top_emotion[1]} times",
        fill=gray,
        font=small_font,
    )

    draw.rounded_rectangle((70, 715, 675, 890), radius=22, fill=card)

    draw.text(
        (100, 745),
        "Retrieval Trend Direction",
        fill=orange,
        font=section_font_small,
    )

    y = 785

    if theme_trends:
        for theme, trend in list(theme_trends.items())[:4]:
            trend_line = _fit_text(
                draw,
                f"{theme} {trend}",
                small_font,
                535,
            )

            draw.text(
                (105, y),
                trend_line,
                fill=trend_color(trend),
                font=small_font,
            )
            y += 27
    else:
        draw.text(
            (105, y),
            "No previous run available",
            fill=gray,
            font=small_font,
        )

    draw.rounded_rectangle((725, 715, 1330, 890), radius=22, fill=card)

    draw.text(
        (755, 745),
        "Most correlated governance needs",
        fill=orange,
        font=section_font_small,
    )

    y = 785

    if governance_counts:
        sorted_governance = sorted(
            governance_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for governance_need, count in sorted_governance[:4]:
            governance_line = _fit_text(
                draw,
                f"{governance_need} ({count})",
                small_font,
                535,
            )

            draw.text((760, y), governance_line, fill=white, font=small_font)
            y += 27
    else:
        draw.text(
            (760, y),
            "No governance matches detected",
            fill=gray,
            font=small_font,
        )

    top_lead = leads[0] if leads else {}

    draw.rounded_rectangle((70, 915, 1330, 1125), radius=22, fill=card)
    draw.text((100, 940), "Top operational signal", fill=orange, font=section_font)

    title = top_lead.get("title", "No lead detected")
    title_lines = _wrap_text(draw, title, body_font, 1120)

    y = 975

    for line in title_lines[:2]:
        draw.text((100, y), line, fill=white, font=body_font)
        y += 32

    if production_excerpt:
        excerpt = production_excerpt.get("excerpt", "")
        subreddit = production_excerpt.get("subreddit", "unknown")

        excerpt_line = _fit_text(
            draw,
            f'Production excerpt: "{excerpt}"',
            small_font,
            850,
        )

        draw.text((100, 1045), excerpt_line, fill=gray, font=small_font)
        draw.text((100, 1075), f"— r/{subreddit}", fill=muted, font=small_font)

    final_score = top_lead.get("final_score", top_lead.get("score", 0))
    intent_score = top_lead.get("intent_score", 0)
    engagement_score = top_lead.get("engagement_score", 0)

    badge_y = 1000
    badge_h = 34
    badge_gap = 16
    badge_x = 1030

    badges = [
        f"Final: {final_score}",
        f"Intent: {intent_score}",
        f"Engagement: {engagement_score}",
    ]

    for badge in badges:
        text_w = draw.textlength(badge, font=tiny_font)
        badge_w = int(text_w + 28)

        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
            radius=12,
            fill=badge_fill,
        )

        draw.text(
            (badge_x + 14, badge_y + 8),
            badge,
            fill=gray,
            font=tiny_font,
        )

        badge_x += badge_w + badge_gap

    draw.text(
        (70, 1150),
        "rag-radar • retrieval reliability intelligence • riswis.com • @ebysslabs",
        fill=muted,
        font=tiny_font,
    )

    draw.text(
        (70, 1172),
        "Signals include retrieval failures, citation integrity issues, reranker instability, stale retrieval, trust conflicts, and governance correlations.",
        fill=muted,
        font=methodology_font,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
