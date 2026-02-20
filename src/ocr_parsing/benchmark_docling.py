import os
import time
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.models.stages.ocr.tesseract_ocr_cli_model import TesseractCliOcrOptions
# ================= SETTINGS =================

source_dir = Path("../../data/doc").resolve()
output_dir = Path("../../data/benchmark").resolve()
output_dir.mkdir(parents=True, exist_ok=True)

# ================= OCR CONFIG =================

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True

# ================ OCR Engine ==============
#pipeline_options.ocr_options = RapidOcrOptions(lang=["ar", "fr"])
pipeline_options.ocr_options = TesseractCliOcrOptions(lang=["ara", "fra"])

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
    }
)

# ================= HELPER FUNCTIONS =================

def compute_similarity(gt_text, ocr_text):
    return SequenceMatcher(None, gt_text, ocr_text).ratio()

def detect_language_ratio(text):
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    latin_chars = len(re.findall(r'[A-Za-z]', text))
    return arabic_chars, latin_chars

# ================= PROCESS ALL FILES =================

all_metrics = []

for file_path in source_dir.iterdir():
    if file_path.suffix.lower() not in [".pdf", ".png", ".jpg", ".jpeg"]:
        continue

    print(f"\nProcessing: {file_path.name}")

    start_time = time.time()
    result = converter.convert(file_path)
    end_time = time.time()

    total_time = end_time - start_time

    # Export markdown
    markdown_text = result.document.export_to_markdown()

    # Save markdown
    output_md = output_dir / f"tesseract_{file_path.stem}.md"
    #output_md = output_dir / f"rapidOCR{file_path.stem}.md"
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    # ========== METRICS ==========

    # 1. Access the Document object
    doc = result.document
    confidences = []
    num_blocks = 0

    # Recursive function to find elements inside GroupItems
    def get_all_elements(item):
        elements = []
        if hasattr(item, "children"): # It's a GroupItem
            for child in item.children:
                elements.extend(get_all_elements(child))
        else:
            elements.append(item)
        return elements

    # Get every item in the document body
    all_items = get_all_elements(doc.body)

    for element in all_items:
        num_blocks += 1
        # Check for provenance and confidence
        if hasattr(element, "prov") and element.prov:
            for p in element.prov:
                if p.confidence is not None:
                    confidences.append(p.confidence)
                    break 

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # 3. Pages count
    num_pages = len(doc.pages) if doc.pages else 1

    # 4. Word count & Lang Detection
    word_count = len(markdown_text.split())
    arabic_chars, latin_chars = detect_language_ratio(markdown_text)

    # 5. Real accuracy (Ground Truth comparison)
    gt_file = source_dir / f"{file_path.stem}.txt"
    similarity = None
    if gt_file.exists():
        with open(gt_file, "r", encoding="utf-8") as f:
            ground_truth = f.read()
        # Clean both texts slightly to get a fairer similarity score
        similarity = compute_similarity(ground_truth.strip(), markdown_text.strip())

    
    # Collect metrics
    metrics = {
        "file": file_path.name,
        "total_time_sec": round(total_time, 2),
        "pages": num_pages,
        "avg_time_per_page": round(total_time / num_pages, 2),
        "word_count": word_count,
        "arabic_chars": arabic_chars,
        "latin_chars": latin_chars,
        "layout_blocks": num_blocks,
        "avg_confidence": round(avg_confidence, 3) if avg_confidence else None,
        "similarity_accuracy": round(similarity, 3) if similarity else None
    }

    all_metrics.append(metrics)

# Save global benchmark file
metrics_output = output_dir / "benchmark_results(t).json"
with open(metrics_output, "w", encoding="utf-8") as f:
    json.dump(all_metrics, f, indent=4)

print("\nBenchmark completed.")
print(f"Results saved in: {metrics_output}")
