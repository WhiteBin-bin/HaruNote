import React from "react";
import { useParams } from "react-router-dom";

const WritePage = () => {
  const { date } = useParams();

  console.log("date ", date);
  return (
    <div>
      <h1>Selected Date: {date}</h1>
    </div>
  );
};

export default WritePage;
