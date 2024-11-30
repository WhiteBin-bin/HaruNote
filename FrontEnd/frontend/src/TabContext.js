import React, { createContext, useContext, useState } from "react";

const TabContext = createContext();

export const TabProvider = ({ children }) => {
  const is_admin = sessionStorage.getItem("is_admin");

  const [activeTab, setActiveTab] = useState(is_admin ? "account" : "calendar");
  return (
    <TabContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabContext.Provider>
  );
};

export const useTab = () => useContext(TabContext);
