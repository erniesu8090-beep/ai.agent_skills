---
name: document-skills
description: Comprehensive document processing suite for Microsoft Office (Word .docx, Excel .xlsx, PowerPoint .pptx) and PDF (.pdf) files. Handles document creation, professional typography and styling, formula calculation (recalc.py), table formatting, slide deck generation, PDF text/table extraction, form filling, watermarking, and OCR. Use when creating, reading, editing, analyzing, or converting Word documents, spreadsheets, presentation slides, or PDF files.
license: Apache-2.0
---

# Document Skills (Office & PDF Processing Suite)

This skill provides a unified, production-grade toolkit for creating, reading, modifying, and formatting Microsoft Office documents (.docx, .xlsx, .pptx) and PDF files (.pdf).

## Quick Navigation (Sub-Guides)

Depending on the document type you are working with, refer to the corresponding sub-guide in 
eferences/:

| Document Type | Formats | Primary Sub-Guide | Key Scripts |
|---|---|---|---|
| **Excel & Spreadsheets** | .xlsx, .csv | 
eferences/xlsx.md | scripts/recalc.py |
| **Word Documents** | .docx | 
eferences/docx.md | scripts/accept_changes.py, scripts/comment.py, scripts/merge_runs.py |
| **PowerPoint Presentations** | .pptx | 
eferences/pptx.md | scripts/add_slide.py, scripts/clean.py, scripts/thumbnail.py |
| **PDF Documents & Forms** | .pdf | 
eferences/pdf.md<br>
eferences/pdf-forms.md<br>
eferences/pdf-reference.md | scripts/fill_fillable_fields.py, scripts/extract_form_field_info.py, scripts/convert_pdf_to_images.py |

---

## 1. Excel & Tabular Data (.xlsx)
- **Key Capabilities**: Professional financial model formatting, visual hierarchy, clean zebra striping, explicit column width calculation, formula recalculation.
- **Formula Recalculation**: openpyxl does not evaluate formula values. When writing formulas (=SUM(...), =AVERAGE(...)), run python scripts/recalc.py <file.xlsx> to pre-compute and cache formula values for viewers that do not run Excel recalculation.
- **Details**: See 
eferences/xlsx.md.

## 2. Word Documents (.docx)
- **Key Capabilities**: Professional corporate report typography, multi-level numbering, table styling with explicit cell widths, headers/footers, tracked changes and comments.
- **Validation & Helpers**: Use scripts/comment.py to annotate Word documents, scripts/accept_changes.py to review tracked revisions, and scripts/merge_runs.py to clean fragmented XML text runs.
- **Details**: See 
eferences/docx.md.

## 3. PowerPoint Presentations (.pptx)
- **Key Capabilities**: Clean slide structure, 16:9 widescreen layout, modern typography, card-based component layouts, contrast and readability rules, speaker notes.
- **Automation Helpers**: Use scripts/add_slide.py for structured layout additions, scripts/clean.py for XML hygiene, and scripts/thumbnail.py for visual slide review.
- **Details**: See 
eferences/pptx.md.

## 4. PDF Extraction & Manipulation (.pdf)
- **Key Capabilities**: Text and tabular data extraction (pypdf, pdfplumber), merging/splitting, form detection and field filling, visual annotation overlay, watermarking, and OCR.
- **Form Filling**: Check fillable fields with scripts/check_fillable_fields.py, inspect coordinates via scripts/extract_form_structure.py, and fill fields using scripts/fill_fillable_fields.py or scripts/fill_pdf_form_with_annotations.py.
- **Details**: See 
eferences/pdf.md, 
eferences/pdf-forms.md, and 
eferences/pdf-reference.md.

---

## Shared Dependencies

Ensure the target project environment has the required Python libraries installed:
`ash
# Office suite
pip install openpyxl python-docx python-pptx

# PDF suite
pip install pypdf pdfplumber reportlab pdf2image pytesseract
`
