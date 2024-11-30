import React from "react";
import { useNavigate, Link } from "react-router-dom";
import "./NavbarAdm.css";

const NavbarAdm = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/signin");
    window.location.reload();
  };

  return (
    <header className="navbarAdm">
      <Link to="/admin" className="navLinkAdm">
        <div className="logoAdm">HARU NOTE</div>
      </Link>

      <nav>
        <ul className="navListAdm">
          <div className="navLineAdm"></div>

          <li className="navLinkWrapperAdm">
            <Link to="/signup" className="navLinkAdm" onClick={handleLogout}>
              Logout
            </Link>
          </li>
          <li className="navItem2Adm">
            <Link to="/signin" className="navLinkAccount">
              Account
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default NavbarAdm;
