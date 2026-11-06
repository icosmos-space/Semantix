from semantix.security.password import hash_password, verify_password


def test_hash_roundtrip():
    h = hash_password("secret123")
    assert verify_password("secret123", h)
    assert not verify_password("nope", h)
