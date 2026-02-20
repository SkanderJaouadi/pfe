import os
import time
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption,ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions

# --- SETTINGS ---
source_pdf = Path("../../data/doc/lettre.pdf").resolve() 
output_dir = Path("../../data/parsed").resolve()
output_dir.mkdir(parents=True, exist_ok=True)

# 2. Configure for Arabic/French using RapidOCR
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = RapidOcrOptions(lang=["ar", "fr"])


# 3. Initialize the Converter
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
    }
)

# 4. Run Conversion
print("Running RapidOCR...")
start_time = time.time()
result = converter.convert(source_pdf)
end_time = time.time()
print(f"Conversion done in {end_time - start_time:.2f} seconds")

# --- Save Markdown Output ---
output_path = output_dir / f"rapidocr_{source_pdf.stem}.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())

print(f"Saved: {output_path}")