from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "reports" / "figures_batch1"

ROWS = [
    ("real_006", "Attention / Greet"),
    ("real_016", "Interest / Elicit"),
    ("real_021", "Desire / Inform"),
    ("real_031", "Desire / Recommend"),
]
COLS = ["t=0s", "t=5s", "t=10s"]


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = img.convert("RGB")
    target_w, target_h = size
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont) -> None:
    x, y = xy
    pad_x, pad_y = 10, 5
    bbox = draw.textbbox((x, y), text, font=font)
    rect = (bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y)
    draw.rounded_rectangle(rect, radius=6, fill=(255, 255, 255, 230), outline=(43, 58, 74), width=1)
    draw.text((x, y), text, fill=(21, 31, 42), font=font)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cell_w, cell_h = 430, 260
    row_gap, col_gap = 18, 12
    left_label_w = 230
    top_header_h = 56
    margin = 22
    width = margin * 2 + left_label_w + len(COLS) * cell_w + (len(COLS) - 1) * col_gap
    height = margin * 2 + top_header_h + len(ROWS) * cell_h + (len(ROWS) - 1) * row_gap

    canvas = Image.new("RGB", (width, height), (248, 249, 250))
    draw = ImageDraw.Draw(canvas, "RGBA")
    title_font = load_font(28, bold=True)
    header_font = load_font(24, bold=True)
    row_font = load_font(22, bold=True)
    small_font = load_font(18)

    draw.text((margin, 14), "Real-store video slices from the sim-to-real pilot", fill=(16, 32, 45), font=title_font)

    for c, col in enumerate(COLS):
        x = margin + left_label_w + c * (cell_w + col_gap) + cell_w // 2
        bbox = draw.textbbox((0, 0), col, font=header_font)
        draw.text((x - (bbox[2] - bbox[0]) / 2, margin + 26), col, fill=(16, 32, 45), font=header_font)

    for r, (session_id, label) in enumerate(ROWS):
        y = margin + top_header_h + r * (cell_h + row_gap)
        draw.rounded_rectangle((margin, y, margin + left_label_w - 18, y + cell_h), radius=8, fill=(233, 239, 244), outline=(194, 205, 214), width=1)
        draw.text((margin + 16, y + 76), session_id, fill=(16, 32, 45), font=row_font)
        draw.text((margin + 16, y + 112), label, fill=(48, 79, 104), font=small_font)
        draw.text((margin + 16, y + 144), "full annotation", fill=(48, 79, 104), font=small_font)

        for c in range(3):
            x = margin + left_label_w + c * (cell_w + col_gap)
            frame = ROOT / "reports" / "real_eval_20260525" / "frames" / session_id / f"{c:03d}.jpg"
            img = fit_cover(Image.open(frame), (cell_w, cell_h))
            canvas.paste(img, (x, y))
            draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=3, outline=(23, 37, 51), width=2)
            draw_label(draw, (x + 12, y + 12), f"{session_id} / {COLS[c]}", small_font)

    png_path = OUT_DIR / "V6_real_store_video_slices.png"
    pdf_path = OUT_DIR / "V6_real_store_video_slices.pdf"
    canvas.save(png_path, quality=92)
    canvas.save(pdf_path, "PDF", resolution=150.0)
    print(png_path)
    print(pdf_path)


if __name__ == "__main__":
    main()
