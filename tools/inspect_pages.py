from pathlib import Path
import pdfplumber

pdf_path = Path(r"C:\CB\4-My work\424冷阴极X射线源\5其他\省辐射安全考试\X射线探伤.pdf")
pages = [23, 24, 25, 38, 39, 40, 64, 65, 66, 67, 68]
with pdfplumber.open(pdf_path) as pdf:
    for i in pages:
        print(f"---PAGE {i + 1}---")
        print(((pdf.pages[i].extract_text() or "")[:3000]).replace("\n", " | "))
