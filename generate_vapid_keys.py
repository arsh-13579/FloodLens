from py_vapid import Vapid01
from cryptography.hazmat.primitives import serialization
import base64

vapid = Vapid01()
vapid.generate_keys()
vapid.save_key("private_key.pem")
vapid.save_public_key("public_key.pem")

raw = vapid.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint,
)
print("VAPID_PUBLIC_KEY=" + base64.urlsafe_b64encode(raw).rstrip(b'=').decode())