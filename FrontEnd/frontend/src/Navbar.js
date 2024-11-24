import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <header style={styles.navbar}>
      <div style={styles.logo}>HARU NOTE</div>
      <nav>
        <ul style={styles.navList}>
          <div style={styles.navLine}></div>
          <li style={styles.navItem}>
            <a href="/" style={styles.navLink}>
              Calendar
            </a>
          </li>
          <li style={styles.navItem}>
            <a href="#" style={styles.navLink}>
              Blog
            </a>
          </li>
          <li style={styles.navLinkWrapper}>
            <Link to="/signup" style={styles.navLink}>
              Sign up
            </Link>
          </li>
          <li style={styles.navItem2}>
            <Link to="/signin" style={styles.navLinkSignin}>
              Sign in
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
}

const styles = {
  navbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#DCDAD8",
    padding: "10px 20px",
    color: "black",
    height: "50px",
    margin: "0 auto",
  },

  logo: {
    fontSize: "24px",
    fontWeight: "lighter",
    marginLeft: "50px",
  },
  navList: {
    display: "flex",
    listStyleType: "none",
    padding: "11px 0px",
    backgroundColor: "white",
    borderRadius: "50px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    width: "180%",
    justifyContent: "right",
    alignItems: "center",
    transform: "translateX(-46%)",
    height: "20px",
    position: "relative",
  },
  navLine: {
    position: "absolute",
    top: "54%",
    left: "-23%",
    width: "68%",
    height: "1px",
    backgroundColor: "#000000",
    transform: "translateY(-50%)",
  },
  navItem: {
    listStyle: "none",
    margin: "0 50px",
  },
  navItem2: {
    listStyle: "none",
    marginLeft: "50px",
    marginRight: "10px",
  },
  navLinkWrapper: {
    display: "inline-block",
    backgroundColor: "#fff",
    color: "#333",
    padding: "3px 10px",
    borderRadius: "25px",
    textDecoration: "none",
    textAlign: "center",
    border: "1px solid #000",
    width: "80px",
    marginLeft: "10px",
  },
  navLinkText: {
    fontSize: "18px",
  },
  navLink: {
    color: "black",
    textDecoration: "none",
    fontSize: "18px",
  },
  navLinkSignin: {
    display: "inline-block",
    backgroundColor: "black",
    color: "white",
    padding: "6px 30px",
    borderRadius: "25px",
    textDecoration: "none",
    textAlign: "center",
    fontWeight: "normal",
    fontSize: "18px",
  },
};

export default Navbar;
