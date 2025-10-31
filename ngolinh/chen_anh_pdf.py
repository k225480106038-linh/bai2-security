import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os

def tao_anh_co_bong_va_chu(duongdan_anh, output_shadow="anh_bong_text.png"):
    """Tạo ảnh có bóng mờ + chèn chữ trong phần cuối ảnh."""
    img = Image.open(duongdan_anh).convert("RGBA")
    w, h = img.size

    # --- Tạo bóng mờ mềm ---
    canvas = Image.new("RGBA", (w + 20, h + 40), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 180))
    shadow_blur = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(shadow_blur, (8, 8), mask=shadow_blur)
    canvas.paste(img, (0, 0), mask=img)

    # --- Thêm chữ trong phần cuối ảnh ---
    draw = ImageDraw.Draw(canvas)
    text = "Ngô Thị Thùy Linh\nNgày ký: 28/10/2025"

    # Font fallback (dùng mặc định nếu không có font đẹp hơn)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    text_w, text_h = draw.multiline_textbbox((0, 0), text, font=font)[2:]
    x_text = (canvas.width - text_w) / 2
    y_text = h - text_h - 5

    # Vẽ bóng cho chữ
    draw.multiline_text((x_text+1, y_text+1), text, font=font, fill=(0, 0, 0, 150), align="center")
    # Vẽ chữ trắng phía trên
    draw.multiline_text((x_text, y_text), text, font=font, fill=(255, 255, 255, 255), align="center")

    canvas.save(output_shadow)
    return output_shadow


def chen_anh_va_chu(pdf_goc, anh, pdf_dich):
    """Chèn ảnh (có bóng + chữ trong ảnh) vào cuối trang PDF."""
    if not os.path.exists(pdf_goc):
        print(f"❌ Không tìm thấy PDF gốc: {pdf_goc}")
        return
    if not os.path.exists(anh):
        print(f"❌ Không tìm thấy ảnh: {anh}")
        return

    anh_hoanthien = tao_anh_co_bong_va_chu(anh)

    doc = fitz.open(pdf_goc)
    trang = doc[-1]
    rect = trang.rect

    # Vị trí: góc phải dưới
    width, height = 220, 150
    margin_right, margin_bottom = 60, 80
    x1 = rect.width - width - margin_right
    y1 = rect.height - height - margin_bottom
    img_rect = fitz.Rect(x1, y1, x1 + width, y1 + height)

    trang.insert_image(img_rect, filename=anh_hoanthien, keep_proportion=True)
    doc.save(pdf_dich)
    doc.close()
    print(f"✅ Đã tạo '{pdf_dich}' với ảnh có bóng mờ + chữ trong ảnh.")


if __name__ == "__main__":
    chen_anh_va_chu("bai2.pdf", "linh.png", "bai2_with_shadow_text.pdf")
