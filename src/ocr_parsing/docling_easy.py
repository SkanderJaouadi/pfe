from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption,ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

source_pdf = Path("../../data/doc/img.jpg").resolve()
output_dir = Path("../../data/parsed").resolve()
output_dir.mkdir(parents=True, exist_ok=True)

# 1. Setup EasyOCR for Arabic and French
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions()

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
        }
)

print("Running EasyOCR...")
result = converter.convert(source_pdf)
output_path = output_dir / f"easyocr_{source_pdf.stem}2.md"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())
print(f"Saved: {output_path}")