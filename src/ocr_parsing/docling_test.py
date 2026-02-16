import os
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption,ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions

# --- SETTINGS ---
source_pdf = Path("../../data/doc/img.pdf").resolve() 
output_dir = Path("../../data/parsed").resolve()
output_filename = Path(source_pdf).stem + ".md"
# ----------------

# 1. Prepare Paths
output_path = Path(output_dir)
output_path.mkdir(parents=True, exist_ok=True)
final_file_path = output_path / output_filename

# 2. Configure for Arabic/French using RapidOCR
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = RapidOcrOptions() 

# 3. Initialize the Converter
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
    }
)

# 4. Run Conversion
print(f"Starting conversion for: {source_pdf}")
result = converter.convert(source_pdf)

# 5. Write the Markdown output
with open(final_file_path, "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())

print(f"Done! Markdown file created at: {final_file_path}")