"""Generate a styled Excel (.xlsx) version of the Section 10 Precedents Database.

Exports:
- data/section10_cases_structured_database.xlsx
- /Users/ananyasridhar/Desktop/Section10_Cases_Structured_Database.xlsx
"""

import csv
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_excel(csv_path="data/section10_cases_structured_database.csv", output_path="data/section10_cases_structured_database.xlsx"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source CSV not found: {csv_path}")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Section 10 Case Law Database"

    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        print("No rows found in CSV!")
        return

    # Standard Header: Deep navy
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Review / Advocate Feedback Header: Amber Gold
    review_header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    review_header_fill = PatternFill(start_color="B45309", end_color="B45309", fill_type="solid")

    # Data styling
    data_font = Font(name="Calibri", size=10)
    data_alignment_wrap = Alignment(horizontal="left", vertical="top", wrap_text=True)
    data_alignment_standard = Alignment(horizontal="left", vertical="top")
    data_alignment_center = Alignment(horizontal="center", vertical="top")

    thin_border = Border(
        left=Side(style="thin", color="E5E7EB"),
        right=Side(style="thin", color="E5E7EB"),
        top=Side(style="thin", color="E5E7EB"),
        bottom=Side(style="thin", color="E5E7EB")
    )

    review_cell_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

    for row_idx, row in enumerate(rows, 1):
        for col_idx, val in enumerate(row, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = thin_border

            # Header row
            if row_idx == 1:
                if col_idx in (18, 19, 20):  # Review, Review Issues, Reviewed By
                    cell.font = review_header_font
                    cell.fill = review_header_fill
                else:
                    cell.font = header_font
                    cell.fill = header_fill
                cell.alignment = header_alignment
            else:
                cell.font = data_font
                # Highlight review column cells lightly
                if col_idx == 18:
                    cell.alignment = data_alignment_center
                elif col_idx in (19, 20):
                    cell.alignment = data_alignment_wrap
                elif col_idx in (2, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17):
                    cell.alignment = data_alignment_wrap
                else:
                    cell.alignment = data_alignment_standard

    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 30

    column_widths = {
        1: 22,  # Court
        2: 36,  # Case Title
        3: 22,  # Case Number
        4: 15,  # Judgment Date
        5: 25,  # Judges
        6: 30,  # Acts Cited
        7: 25,  # Sections Cited
        8: 25,  # Legal Topics
        9: 25,  # Outcome
        10: 42, # Fact/ Petitioner
        11: 42, # Fact/ Respondent
        12: 38, # Issues
        13: 38, # Petitioner Argument
        14: 38, # Respondent Argument
        15: 42, # Factors to be Considered
        16: 38, # Decision
        17: 35, # Citation link
        18: 18, # Review
        19: 45, # Review Issues
        20: 22, # Reviewed By
        21: 20, # Ground Primary
        22: 24, # All Grounds
        23: 14, # Judgment Year
        24: 15, # Relief Status
        25: 18, # Marriage Dissolved
        26: 22, # Legal Era
        27: 22, # Substantive Adjudication
        28: 35, # Equivalent Citations
        29: 16, # Doc ID
        30: 35, # URL
        31: 16  # Chunks
    }

    for col_idx, width in column_widths.items():
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"Saved Excel file to: {output_path} ({os.path.getsize(output_path)} bytes)")

    desktop_xlsx = "/Users/ananyasridhar/Desktop/Section10_Cases_Structured_Database.xlsx"
    try:
        wb.save(desktop_xlsx)
        print(f"Saved Desktop copy to: {desktop_xlsx}")
    except Exception as e:
        print(f"Desktop copy notice: {e}")

if __name__ == "__main__":
    build_excel()
