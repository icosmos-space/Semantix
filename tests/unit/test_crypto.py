from semantix.security.crypto import decrypt_secret, encrypt_secret


def test_encrypt_roundtrip():
    token = encrypt_secret("s3cret")
    assert token != "s3cret"
    assert decrypt_secret(token) == "s3cret"
