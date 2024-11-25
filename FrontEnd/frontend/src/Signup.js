import React, { useState } from "react";
import signup from "./assets/signup.png";

const Signup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignin = () => {
    console.log("Email:", email);
    console.log("Password:", password);
  };

  return (
    <div>
      <main
        style={{
          height: "720px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontFamily: "NEXON Lv1 Gothic Low OTF",
          marginTop: "-220px",
          fontSize: "30px",
          flexDirection: "column",
        }}
      >
        <img
          src={signup}
          style={{ width: "500px", marginTop: "25%" }}
          alt="description"
        />
        {/* <p>나만의 일기장 만들기</p> */}
        <div style={styles.container}>
          <input
            type="text"
            placeholder="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={styles.input}
          />
          <input
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
          />

          <div style={styles.passwordContainer}>
            <input
              type="password"
              placeholder="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.passwordInput}
            />

            <button
              type="button"
              onClick={handleSignin}
              style={styles.signinButton}
              onMouseOver={(e) => (e.target.style.backgroundColor = "#444")}
              onMouseOut={(e) => (e.target.style.backgroundColor = "black")}
            >
              Sign up
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
    maxWidth: "400px",
    padding: "20px",
    backgroundColor: "#fff",
    marginTop: "40px",
    position: "relative",
  },
  input: {
    padding: "17px 25px",
    marginBottom: "20px",
    width: "80%",
    borderRadius: "30px",
    border: "1px solid black",
    fontSize: "13px",
  },
  passwordContainer: {
    position: "relative",
    width: "80%",
  },
  passwordInput: {
    padding: "17px 25px",
    marginBottom: "15px",
    width: "100%",
    borderRadius: "30px",
    border: "1px solid black",
    fontSize: "13px",
    position: "relative",
    left: "-20px",
  },
  signinButton: {
    position: "absolute",
    right: "-32px",
    top: "41%",
    transform: "translateY(-50%)",
    padding: "15px 30px",
    backgroundColor: "black",
    color: "white",
    border: "1px solid black",
    borderRadius: "30px",
    fontSize: "16px",
    cursor: "pointer",
    transition: "background-color 0.3s",
  },
};

export default Signup;
