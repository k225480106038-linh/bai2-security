from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

# === ĐƯỜNG DẪN LƯU FILE ===
BASE_DIR = r"D:\ngolinh"
key_path = os.path.join(BASE_DIR, "signer_key.pem")
cert_path = os.path.join(BASE_DIR, "signer_cert.pem")

print("🔐 Đang tạo cặp khóa RSA 2048-bit...")
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# === Ghi private key ===
with open(key_path, "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

print(f"✅ Đã lưu private key tại: {key_path}")

# === Thông tin người ký ===
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "Ngo Thi Thuy Linh"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "K58KTP"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
    x509.NameAttribute(NameOID.SERIAL_NUMBER, "K225480106038"),
])

# === Tạo chứng chỉ X.509 tự ký ===
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=730))  # 2 năm
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .sign(private_key, hashes.SHA256())
)

# === Ghi certificate ra file ===
with open(cert_path, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print(f"✅ Đã lưu certificate tại: {cert_path}")
print("🎉 Hoàn tất tạo khóa & chứng chỉ tự ký!")
