from datetime import datetime
from pyhanko.sign import signers, fields
from pyhanko.stamp.text import TextStampStyle
from pyhanko.pdf_utils import images
from pyhanko.pdf_utils.text import TextBoxStyle
from pyhanko.pdf_utils.layout import SimpleBoxLayoutRule, AxisAlignment, Margins
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec
import os

print("🚀 Bắt đầu quá trình ký PDF...")

# === ĐƯỜNG DẪN (đúng với thư mục của bạn) ===
BASE_DIR = r"D:\ngolinh"
PDF_IN = os.path.join(BASE_DIR, "bai2.pdf")
PDF_OUT = os.path.join(BASE_DIR, "bai2_signed.pdf")
KEY_FILE = os.path.join(BASE_DIR, "signer_key.pem")
CERT_FILE = os.path.join(BASE_DIR, "signer_cert.pem")
SIG_IMG = os.path.join(BASE_DIR, "anh_bong.png")  # Ảnh chữ ký "bóng"

# === KIỂM TRA FILE ===
for path in [PDF_IN, KEY_FILE, CERT_FILE, SIG_IMG]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Không tìm thấy file: {path}")

# === TẠO SIGNER & CONTEXT ===
signer = signers.SimpleSigner.load(KEY_FILE, CERT_FILE, key_passphrase=None)
vc = ValidationContext(trust_roots=[load_cert_from_pemder(CERT_FILE)])

# === MỞ PDF GỐC ===
with open(PDF_IN, "rb") as inf:
    writer = IncrementalPdfFileWriter(inf)

    # Xác định số trang
    try:
        pages = writer.root["/Pages"]
        num_pages = int(pages["/Count"]) if "/Count" in pages else len(pages["/Kids"])
    except Exception:
        print("⚠️ Không đọc được số trang, mặc định 1.")
        num_pages = 1
    target_page = num_pages - 1

    # Tạo trường chữ ký
    fields.append_signature_field(
        writer,
        SigFieldSpec(
            sig_field_name="SigField1",
            box=(200, 60, 550, 180),  # vị trí chữ ký (x1, y1, x2, y2)
            on_page=target_page
        )
    )

    # === ẢNH CHỮ KÝ ===
    background_img = images.PdfImage(SIG_IMG)

    # Căn layout: ảnh bên trên, chữ bên dưới
    bg_layout = SimpleBoxLayoutRule(
        x_align=AxisAlignment.ALIGN_MID,
        y_align=AxisAlignment.ALIGN_MAX,
        margins=Margins(bottom=40)
    )

    text_layout = SimpleBoxLayoutRule(
        x_align=AxisAlignment.ALIGN_MID,
        y_align=AxisAlignment.ALIGN_MIN,
        margins=Margins(top=120)
    )

    # Style chữ
    text_style = TextBoxStyle(font_size=13)

    # Nội dung chữ ký
    ngay_ky = datetime.now().strftime("%d/%m/%Y")
    stamp_text = (
        "Ngô Thi Thùy Linh"
        f"\nNgày ký: 28/10/2025"
    )

    # Tạo stamp style (ảnh + chữ như mẫu “ảnh bóng”)
    stamp_style = TextStampStyle(
        stamp_text=stamp_text,
        background=background_img,
        background_layout=bg_layout,
        inner_content_layout=text_layout,
        text_box_style=text_style,
        border_width=0,
        background_opacity=0.95,  # tạo hiệu ứng "bóng nhẹ"
    )

    # Metadata chữ ký
    meta = signers.PdfSignatureMetadata(
        field_name="SigField1",
        reason="Nộp bài: Chữ ký số PDF - 58KTP",
        location="Thái Nguyên",
        md_algorithm="sha256",
    )

    # Ký
    pdf_signer = signers.PdfSigner(
        signature_meta=meta,
        signer=signer,
        stamp_style=stamp_style,
    )

    # Xuất file
    with open(PDF_OUT, "wb") as outf:
        pdf_signer.sign_pdf(writer, output=outf)

print("✅ Đã ký PDF thành công!")
print(f"📄 File lưu tại: {PDF_OUT}")
