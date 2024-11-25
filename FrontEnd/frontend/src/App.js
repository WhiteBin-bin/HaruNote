import React from "react";
import Navbar from "./Navbar";
import Main from "./Main";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Signup from "./Signup";
import Signin from "./Signin";
import Calendar from "./Calendar";
import WritePage from "./WritePage";

const App = () => {
  return (
    <>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/signin" element={<Signin />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/calendar/:date" element={<WritePage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
};

export default App;
