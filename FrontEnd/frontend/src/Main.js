import React from "react";
import title from "./assets/title.png";
import Signin from "./Signin";

const Main = () => {
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
          src={title}
          style={{ width: "600px", marginTop: "25%" }}
          alt="description"
        />
        {/* <p>소소한 일상을 나누는 공간, 하루노트</p> */}
        <Signin />
      </main>
    </div>
  );
};

export default Main;
