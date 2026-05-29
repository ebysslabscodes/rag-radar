from PIL import Image, ImageDraw, ImageFont
import textwrap


def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


def wrap_text(text, width=85):
    if not text:
        return ""
    return "\n".join(textwrap.wrap(str(text), width=width))


def truncate(text, max_chars=260):
    if not text:
        return "No excerpt available."
    text = str(text).replace("\n", " ").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def generate_evidence_summary(
    leads,
    output_path,
    run_date,
    max_items=4,
):
    """
    Generates a second PNG that supports the main weekly dashboard.

    This image shows operational evidence behind the weekly signals:
    - top discussions
    - excerpts
    - detected themes
    - governance mappings
    - scoring metadata
    """

    width = 1400
    height = 1500

    bg = "#0D1117"
    card = "#151B23"
    orange = "#FF8A00"
    white = "#F0F3F6"
    muted = "#A8B3C2"
    gray = "#7D8794"
    border = "#212A35"
    green = "#3FB950"

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    title_font = load_font(52, bold=True)
    subtitle_font = load_font(26)
    section_font = load_font(28, bold=True)
    body_font = load_font(22)
    small_font = load_font(18)
    tiny_font = load_font(15)

    # Header
    draw.text(
        (70, 55),
        "RAG Radar — Retrieval Risk Evidence",
        fill=white,
        font=title_font,
    )

    draw.text(
        (72, 118),
        f"{run_date} · Operational evidence behind weekly retrieval risk signals",
        fill=muted,
        font=subtitle_font,
    )

    draw.text(
        (72, 165),
        "Top discussions ranked by production relevance, governance mapping, and operational signal strength.",
        fill=gray,
        font=small_font,
    )

    # Top leads
    evidence_items = leads[:max_items]

    start_y = 220
    card_h = 285
    gap = 26

    for idx, lead in enumerate(evidence_items, start=1):
        y = start_y + (idx - 1) * (card_h + gap)

        draw.rounded_rectangle(
            (65, y, width - 65, y + card_h),
            radius=24,
            fill=card,
            outline=border,
            width=1,
        )

        subreddit = lead.get("subreddit", "Unknown")
        title = lead.get("title", "Untitled discussion")
        excerpt = lead.get("text_preview", "")
        themes = lead.get("themes", [])
        mappings = lead.get("governance_mapping", [])

        final_score = lead.get("final_score", 0)
        intent_score = lead.get("intent_score", 0)
        engagement_score = lead.get("engagement_score", 0)

        # Source / rank
        draw.text(
            (95, y + 28),
            f"{idx}. {subreddit}",
            fill=orange,
            font=section_font,
        )

        # Title
        wrapped_title = wrap_text(title, width=82)
        title_lines = wrapped_title.split("\n")[:2]

        ty = y + 68
        for line in title_lines:
            draw.text((95, ty), line, fill=white, font=body_font)
            ty += 28

        # Excerpt
        clean_excerpt = truncate(excerpt, max_chars=260)
        wrapped_excerpt = wrap_text(clean_excerpt, width=105)

        ey = y + 132
        draw.text((95, ey), "Excerpt:", fill=muted, font=small_font)
        ey += 26

        for line in wrapped_excerpt.split("\n")[:3]:
            draw.text((95, ey), line, fill=gray, font=small_font)
            ey += 23

        # Themes
        theme_text = ", ".join(themes[:3]) if themes else "No themes detected"
        draw.text(
            (95, y + 235),
            f"Themes: {theme_text}",
            fill=muted,
            font=small_font,
        )

        # Governance mappings
        governance_needs = []
        for item in mappings:
            need = item.get("governance_need")
            if need and need not in governance_needs:
                governance_needs.append(need)

        governance_text = (
            ", ".join(governance_needs[:3])
            if governance_needs
            else "No governance mapping detected"
        )

        draw.text(
            (95, y + 262),
            f"Governance needs: {governance_text}",
            fill=green if governance_needs else gray,
            font=small_font,
        )

        # Score pills
        pill_y = y + 35
        pill_x = width - 420

        pills = [
            f"Final: {final_score}",
            f"Intent: {intent_score}",
            f"Engagement: {engagement_score}",
        ]

        for pill in pills:
            pill_w = 118 if "Engagement" not in pill else 165

            draw.rounded_rectangle(
                (pill_x, pill_y, pill_x + pill_w, pill_y + 36),
                radius=14,
                fill="#222B36",
            )

            draw.text(
                (pill_x + 14, pill_y + 8),
                pill,
                fill=muted,
                font=tiny_font,
            )

            pill_x += pill_w + 14

    # Footer
    footer_y = height - 70

    draw.text(
        (70, footer_y),
        "rag-radar • retrieval risk intelligence • riswis.com • @ebysslabs",
        fill=muted,
        font=tiny_font,
    )

    draw.text(
        (70, footer_y + 24),
        "Evidence cards summarize public operational discussions, detected retrieval failure themes, and mapped governance needs.",
        fill=gray,
        font=tiny_font,
    )

    img.save(output_path)
