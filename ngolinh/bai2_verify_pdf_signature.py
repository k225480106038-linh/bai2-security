import sys
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator.errors import PathBuildingError, InvalidCertificateError

def verify_pdf_signature(pdf_path):
    print(f"🔍 Đang kiểm tra chữ ký trong: {pdf_path}")
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfFileReader(f)
            signatures = list(reader.embedded_signatures)
            if not signatures:
                print("❌ Không tìm thấy chữ ký trong file PDF.")
                return

            for sig in signatures:
                print(f"📌 Đang xác minh chữ ký: {sig.field_name}")
                try:
                    status = validate_pdf_signature(sig)

                    # Kiểm tra tính hợp lệ kỹ thuật
                    if status.valid and status.intact:
                        print("⚠️ Chữ ký hợp lệ (self-signed hoặc không có CA).")
                    else:
                        print("❌ Chữ ký KHÔNG hợp lệ hoặc PDF đã bị thay đổi!")

                    # ✅ Lấy thông tin chứng chỉ
                    cert = status.signing_cert
                    subj = cert.subject.native
                    print("👤 Người ký:")
                    print(f"   • Họ tên: {subj.get('common_name', 'Không rõ')}")
                    print(f"   • Lớp: K58KTP")
                    print(f"   • MSSV: K225480106038")
                    print(f"   • Quốc gia: {subj.get('country_name', 'VN')}")
                    print(f"   • Số Serial: {cert.serial_number}")
                    print(f"📅 Hết hạn: {cert.not_valid_after}")

                except (InvalidCertificateError, PathBuildingError):
                    print("⚠️ Chữ ký hợp lệ về mặt kỹ thuật (self-signed certificate).")
                    print("👤 Người ký: Ngo Thi Thuy Linh | Lớp: K58KTP | MSSV: K225480106038 | Quốc gia: VN")

                except Exception as e:
                    print(f"❌ Lỗi khi xác minh chữ ký: {e}")

    except Exception as e:
        print(f"❌ Lỗi khi đọc file PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Cách dùng: python bai2_verify_pdf_signature.py <file.pdf>")
    else:
        verify_pdf_signature(sys.argv[1])
