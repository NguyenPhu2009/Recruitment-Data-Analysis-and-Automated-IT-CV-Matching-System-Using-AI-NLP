import pymupdf as fitz
import pdfplumber
import re

def validate_extraction(text: str) -> dict:
    if not text:
        return {'is_reliable': False, 'score': 0.0}

    # 1. Bảo vệ các từ khóa IT chứa ký tự đặc biệt
    protected_text = text.lower()
    protected_text = protected_text.replace('c++', 'cplusplus')
    protected_text = protected_text.replace('c#', 'csharp')
    protected_text = protected_text.replace('.net', 'dotnet')

    word_count = len(protected_text.split())

    # 2. Tính tỷ lệ ký tự đặc biệt trên văn bản đã được bảo vệ
    special_chars = sum(1 for c in protected_text if not c.isalnum() and not c.isspace())
    special_char_ratio = special_chars / max(len(protected_text), 1)

    # Ngưỡng tin cậy: >= 50 từ và tỷ lệ ký tự đặc biệt < 25%
    is_reliable = word_count >= 50 and special_char_ratio < 0.25

    return {
        'is_reliable': is_reliable,
        'score': min(word_count / 200, 1.0)
    }


def extract_text_from_cv(pdf_path):
    text = ""
    try:
        # Bước 1: Thử với PyMuPDF
        doc = fitz.open(pdf_path)
        text_blocks = []

        for page in doc:
            # Lấy văn bản theo từng khối (block) thay vì từng dòng đơn thuần
            blocks = page.get_text("blocks")
            # blocks: (x0, y0, x1, y1, "text", block_no, block_type)
            # Sắp xếp blocks ưu tiên tọa độ Y (từ trên xuống), sau đó X (từ trái qua)
            blocks.sort(key=lambda b: (round(b[1], 1), b[0]))

            for b in blocks:
                if b[6] == 0:  # block_type == 0 là văn bản
                    text_blocks.append(b[4])

        doc.close()
        text = "\n".join(text_blocks)

        # Bước 2: Validate chất lượng văn bản trích xuất
        quality = validate_extraction(text)
        if not quality['is_reliable']:
            raise ValueError("Văn bản trích xuất quá ngắn hoặc nhiều ký tự rác, chuyển sang fallback.")

    except Exception as e:
        print(f"[Warning] PyMuPDF thất bại hoặc text không chuẩn, fallback sang pdfplumber: {e}")
        text = extract_fallback_pdfplumber(pdf_path)

    return text.strip()


def extract_fallback_pdfplumber(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text(layout=True)
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"[Error] Không thể đọc CV bằng cả 2 thư viện: {e}")

    return text.strip()