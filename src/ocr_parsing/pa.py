import time
import re
from pathlib import Path
from paddleocr import PaddleOCRVL
import numpy as np
from PIL import Image, ImageDraw, ImageFont

print("go", flush=True)

pipeline = PaddleOCRVL()
print("Model loaded", flush=True)

input_path = "../../sms.jpg"  # supports .pdf, .jpg, .png, etc.
input_name = Path(input_path).stem  # e.g. "contrat"

output_dir = Path("ocr_output") / input_name
output_dir.mkdir(parents=True, exist_ok=True)

start = time.time()
print("Predicting...", flush=True)

result = pipeline.predict(input_path)

end = time.time()
print(f"Prediction took {end - start:.2f} seconds", flush=True)
print(f"Total pages: {len(result)}", flush=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_attr(obj, key, default=""):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

LABEL_COLORS = {
    "text":             (52,  152, 219),
    "table":            (46,  204, 113),
    "paragraph_title":  (155,  89, 182),
    "figure":           (230, 126,  34),
    "header_image":     (231,  76,  60),
    "footer":           (241, 196,  15),
    "default":          (149, 165, 166),
}

def draw_boxes(src_img_array, layout_boxes):
    """Draw bounding boxes with labels and scores on image."""
    vis_img = Image.fromarray(src_img_array).convert("RGB")
    draw = ImageDraw.Draw(vis_img, "RGBA")
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 11)
    except:
        font = ImageFont.load_default()
        small_font = font

    for box in layout_boxes:
        label = box.get("label", "default")
        score = box.get("score", 0)
        x1, y1, x2, y2 = [int(c) for c in box["coordinate"]]
        color = LABEL_COLORS.get(label, LABEL_COLORS["default"])

        draw.rectangle([x1, y1, x2, y2], fill=(*color, 40), outline=(*color, 220), width=2)

        tag = f"{label} {score:.2f}"
        tag_x, tag_y = x1, max(0, y1 - 16)
        draw.rectangle([tag_x, tag_y, tag_x + len(tag) * 7 + 4, tag_y + 15],
                       fill=(*color, 200))
        draw.text((tag_x + 2, tag_y + 1), tag, fill=(255, 255, 255), font=small_font)

    return vis_img

def parse_html_table_to_md(html):
    """Convert HTML table string to markdown table."""
    rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)
    if not rows:
        return html
    md_table = []
    for i, row in enumerate(rows):
        cells = re.findall(r"<td(?:[^>]*)>(.*?)</td>", row, re.DOTALL)
        cells = [c.strip() for c in cells]
        md_table.append("| " + " | ".join(cells) + " |")
        if i == 0:
            md_table.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(md_table)

# ── Process each page ────────────────────────────────────────────────────────
all_md_lines = []
all_md_lines.append('<div dir="rtl" lang="ar">\n')
all_md_lines.append(f"# {input_name}\n")
all_md_lines.append(f"*Source: `{input_path}` — {len(result)} page(s) — {end - start:.2f}s*\n")
all_md_lines.append("---\n")

for page_idx, page in enumerate(result):
    print(f"\nProcessing page {page_idx + 1}/{len(result)}...", flush=True)

    parsing_res_list = page.get("parsing_res_list", [])
    src_img_array = page.get("doc_preprocessor_res", {}).get("output_img")
    layout_boxes = page.get("layout_det_res", {}).get("boxes", [])

    # Page header in markdown
    if len(result) > 1:
        all_md_lines.append(f"\n## Page {page_idx + 1}\n")
        all_md_lines.append("---\n")

    # ── Bounding box image ────────────────────────────────────────────────
    if src_img_array is not None and layout_boxes:
        vis_img = draw_boxes(src_img_array, layout_boxes)
        vis_path = output_dir / f"page_{page_idx + 1:02d}_boxes.png"
        vis_img.save(vis_path)
        print(f"  Saved box visualization: {vis_path}", flush=True)

    # ── Crop header images ────────────────────────────────────────────────
    header_boxes = [b for b in layout_boxes if b.get("label") == "header_image"]
    header_md_inserts = []
    if header_boxes and src_img_array is not None:
        src_img = Image.fromarray(src_img_array)
        for i, box in enumerate(header_boxes):
            x1, y1, x2, y2 = [int(c) for c in box["coordinate"]]
            cropped = src_img.crop((x1, y1, x2, y2))
            img_filename = f"page_{page_idx + 1:02d}_header_{i + 1}.png"
            cropped.save(output_dir / img_filename)
            print(f"  Saved header image: {img_filename}", flush=True)
            header_md_inserts.append(f"![Header](./{img_filename})\n")

    # Insert header images before page content
    all_md_lines.extend(header_md_inserts)

    # ── Parse content blocks ──────────────────────────────────────────────
    fig_counter = 0
    for item in parsing_res_list:
        label = get_attr(item, "label")
        content = str(get_attr(item, "content") or "").strip()

        if not content:
            continue

        if label == "paragraph_title":
            all_md_lines.append(f"### {content}\n")

        elif label == "table":
            all_md_lines.append(parse_html_table_to_md(content) + "\n")

        elif label == "figure":
            img_data = get_attr(item, "img")
            if img_data is not None and isinstance(img_data, np.ndarray):
                fig_counter += 1
                img_filename = f"page_{page_idx + 1:02d}_figure_{fig_counter}.png"
                img_save_path = output_dir / img_filename
                try:
                    Image.fromarray(img_data).save(img_save_path)
                    all_md_lines.append(f"![Figure {fig_counter}](./{img_filename})\n")
                    print(f"  Saved figure: {img_filename}", flush=True)
                except Exception as e:
                    print(f"  Could not save figure: {e}", flush=True)

        else:
            all_md_lines.append(f"{content}\n")

        all_md_lines.append("\n")

all_md_lines.append('\n</div>')

# ── Save markdown ─────────────────────────────────────────────────────────────
md_path = output_dir / f"{input_name}_ocr.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(all_md_lines))

print(f"\nDone!")
print(f"Markdown : {md_path}")
print(f"Images   : {output_dir}/")