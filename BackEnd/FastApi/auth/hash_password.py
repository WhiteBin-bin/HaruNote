from passlib.context import CryptContext
import logging

class HashPassword:
    def __init__(self, schemes=["bcrypt"]):
        """
        초기화: 비밀번호 해싱 및 검증 알고리즘 설정
        """
        self.pwd_context = CryptContext(schemes=schemes, deprecated="auto")
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def hash_password(self, password: str):
        """
        비밀번호를 해싱하는 함수
        :param password: 평문 비밀번호
        :return: 해싱된 비밀번호
        """
        if not password:
            logging.error("Empty password provided for hashing")
            raise ValueError("Password must not be empty")
        try:
            hashed_password = self.pwd_context.hash(password)
            logging.info("Password successfully hashed")
            return hashed_password
        except Exception as e:
            logging.error(f"Error while hashing password: {e}")
            raise

    def verify_password(self, plain_password: str, hashed_password: str):
        """
        비밀번호를 검증하는 함수
        :param plain_password: 입력된 평문 비밀번호
        :param hashed_password: 저장된 해싱된 비밀번호
        :return: 비밀번호가 일치하면 True, 그렇지 않으면 False
        """
        try:
            is_valid = self.pwd_context.verify(plain_password, hashed_password)
            if is_valid:
                logging.info("Password verification succeeded")
            else:
                logging.warning("Password verification failed")
            return is_valid
        except Exception as e:
            logging.error(f"Error during password verification: {e}")
            raise

