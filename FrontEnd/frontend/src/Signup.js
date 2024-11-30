import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import signup from "./assets/signup.png";
import "./Signup.css";

const Signup = () => {
  const [username, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [error, setError] = useState(null); // 에러 상태 추가
  const [loading, setLoading] = useState(false); // 로딩 상태 추가
  const [isSent, setIsSent] = useState(false); // 전송 완료 상태
  const [successMessage, setSuccessMessage] = useState(null); // 성공 메시지 상태
  const navigate = useNavigate();

  const handleEmailAuth = async () => {
    if (!username || !email || !password) {
      alert("모든 필드를 입력해주세요.");
      return;
    }

    try {
      setLoading(true); // 요청 중 로딩 상태로 설정
      setIsSent(false);

      const response = await axios.post(
        `http://localhost:8000/user/signup/request-code`,
        {
          email,
          password,
          username,
        }
      );

      if (response.status === 422) {
        alert("이메일 형식에 맞지 않습니다. \n다시 확인해주세요.");
      } else if (response.status === 200) {
        setError(null); // 기존 에러 초기화
        setSuccessMessage(null); // 기존 성공 메시지 초기화
        setIsSent(true);
        alert("인증코드를 전송했습니다. \n이메일을 확인해주세요.");
      }
    } catch (err) {
      alert("이메일 전송에 실패했습니다.");
    } finally {
      setLoading(false); // 로딩 상태 종료
    }
  };

  const handleSignup = async () => {
    try {
      const response = await axios.post(
        `http://localhost:8000/user/signup/verify-code?code=${authCode}`
      );

      if (response.status === 201) {
        alert("회원가입에 성공하였습니다. \n로그인 해주세요.");
        setName("");
        setEmail("");
        setPassword("");
        navigate("/signin");
      } else {
        alert("회원가입에 실패하였습니다.");
      }
    } catch (error) {
      console.error("회원가입 오류:", error);
      alert("서버와 연결할 수 없습니다. 다시 시도해주세요.");
    }
  };

  return (
    <div>
      <main className="main-container">
        <img src={signup} className="signup-img" alt="description" />
        <div className="container">
          {error && <div className="error-message">{error}</div>}
          {successMessage && (
            <div className="success-message">{successMessage}</div>
          )}

          <input
            type="text"
            placeholder="name"
            value={username}
            onChange={(e) => setName(e.target.value)}
            className="input"
          />
          <input
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
          <div className="passwordContainer">
            <input
              type="password"
              placeholder="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="passwordInput"
            />

            <button
              type="button"
              onClick={handleEmailAuth}
              className="signinButton"
              disabled={loading} // 로딩 중에는 버튼 비활성화
            >
              {
                loading
                  ? "sending..."
                  : isSent
                  ? "complete" // 전송 완료된 경우
                  : "Sign up" // 요청이 완료되지 않았을 때
              }
            </button>

            <input
              type="text"
              placeholder="인증코드를 입력해주세요."
              value={authCode}
              onChange={(e) => setAuthCode(e.target.value)}
              className="passwordInput"
            />

            <button
              type="button"
              onClick={handleSignup}
              className="authButton"
              disabled={loading} // 로딩 중에는 버튼 비활성화
            >
              &nbsp;Send&nbsp;&nbsp;
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Signup;
