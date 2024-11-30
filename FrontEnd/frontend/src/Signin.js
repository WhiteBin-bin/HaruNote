import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import title from "./assets/title.png";
import "./Signin.css";

const Signin = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSignin();
    }
  };

  const handleSignin = async () => {
    if (!email) {
      alert("이메일을 입력해주세요.");
      return;
    } else if (!password) {
      alert("비밀번호를 입력해주세요.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/user/signin", {
        email,
        password,
      });

      sessionStorage.setItem("token", response.data.access_token);
      sessionStorage.setItem("refresh_token", response.data.refresh_token);
      sessionStorage.setItem("user_id", response.data.user_id);
      sessionStorage.setItem("is_admin", response.data.is_admin);
      sessionStorage.setItem("email", response.data.email);

      if (response.data.is_admin === true) {
        navigate("/admin");
        window.location.reload();
      } else {
        navigate("/calendar");
      }
    } catch (err) {
      console.error(err);
      alert("로그인에 실패했습니다. 다시 시도해주세요.");
    }
  };

  return (
    <div>
      <main className="signin-main">
        <img src={title} className="signin-title" alt="description" />
        <div className="signin-container" onKeyDown={handleKeyDown}>
          <input
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="signin-input"
          />

          <div className="password-container">
            <input
              type="password"
              placeholder="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="password-input"
            />

            <button
              type="button"
              onClick={handleSignin}
              className="signin-button"
            >
              Sign in
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Signin;
