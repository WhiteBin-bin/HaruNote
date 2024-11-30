import React from "react";
import Navbar from "./Navbar";
import { TabProvider } from "./TabContext";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Signup from "./Signup";
import Signin from "./Signin";
import Calendar from "./Calendar";
import Diary from "./Diary";
import Blog from "./Blog";
import NavbarAdm from "./NavbarAdm";
import Admin from "./Admin";

const App = () => {
  const is_admin = Boolean(sessionStorage.getItem("is_admin"));

  return (
    <TabProvider>
      <BrowserRouter>
        {is_admin === true ? <NavbarAdm /> : <Navbar />}
        <Routes>
          {is_admin === true ? (
            <>
              <Route path="/admin" element={<Admin />} />
              <Route path="/diary/:user_id/:date/:title" element={<Diary />} />
            </>
          ) : (
            <>
              <Route path="/" element={<Signin />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/signin" element={<Signin />} />
              <Route path="/calendar" element={<Calendar />} />
              <Route path="/diary/:user_id/:date" element={<Diary />} />
              <Route path="/diary/:user_id/:date/:title" element={<Diary />} />
              <Route path="/blog" element={<Blog />} />
            </>
          )}
        </Routes>
      </BrowserRouter>
    </TabProvider>
  );
};

export default App;
