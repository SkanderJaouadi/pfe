import time
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.models.stages.ocr.tesseract_ocr_cli_model import TesseractCliOcrOptions

# --- Paths ---
source_pdf = Path("../../data/doc/img.pdf").resolve() 
output_dir = Path("../../data/parsed").resolve()
output_dir.mkdir(parents=True, exist_ok=True)

# --- Pipeline Options ---
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractCliOcrOptions(lang=["ara", "fra"])  

# --- Initialize the Converter ---
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
    }
)

# --- Conversion ---
print("Running Tesseract OCR...")
start_time = time.time()
result = converter.convert(source_pdf)
end_time = time.time()
print(f"Conversion done in {end_time - start_time:.2f} seconds")

# --- Save Markdown Output ---
output_path = output_dir / f"tesseract_{source_pdf.stem}.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())

print(f"Saved: {output_path}")
