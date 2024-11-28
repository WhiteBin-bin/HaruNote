import secrets

# 256비트 (32바이트) 크기의 강력한 비밀 키 생성
secret_key = secrets.token_hex(32)

# 생성된 SECRET_KEY 출력
print("Generated SECRET_KEY:", secret_key)