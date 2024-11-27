def get_email_verification_template(verification_url: str) -> dict:
    """
    이메일 검증 템플릿
    """
    subject = "Email Verification"
    body = f"""
    Hello,

    Please verify your email by clicking the link below:

    {verification_url}

    If you did not request this email, please ignore it.

    Thank you.
    """
    return {"subject": subject, "body": body}


def get_password_reset_template(reset_url: str) -> dict:
    """
    비밀번호 재설정 템플릿
    """
    subject = "Password Reset Request"
    body = f"""
    Hello,

    You requested to reset your password. Please click the link below to proceed:

    {reset_url}

    If you did not request this, please ignore this email.

    Thank you.
    """
    return {"subject": subject, "body": body}
