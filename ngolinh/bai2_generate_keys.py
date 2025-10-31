from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

# === Cấu hình đường dẫn lưu file ===
BASE_DIR = r"D:\ngolinh"
KEY_FILE = os.path.join(BASE_DIR, "signer_key.pem")
CERT_FILE = os.path.join(BASE_DIR, "signer_cert.pem")

# === 1. Sinh khóa riêng (private key RSA 2048 bit) ===
print("🔐 Tạo private key RSA 2048-bit...")
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# === 2. Tạo certificate (tự ký) ===
print("📜 Tạo chứng chỉ tự ký (self-signed)...")
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Thai Nguyen"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Thai Nguyen"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "K58KTP"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Ngo Thi Thuy Linh"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .sign(private_key, hashes.SHA256())
)

# === 3. Lưu private key ===
with open(KEY_FILE, "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,  # 🔑 định dạng chính xác cho pyHanko
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
print(f"✅ Private key lưu tại: {KEY_FILE}")

# === 4. Lưu certificate ===
with open(CERT_FILE, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
print(f"✅ Certificate lưu tại: {CERT_FILE}")

print("\n🎉 Đã tạo cặp khóa & chứng chỉ hợp lệ!")
