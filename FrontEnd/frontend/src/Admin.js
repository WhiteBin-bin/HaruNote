import React, { useState, useEffect } from "react";
import { useTab } from "./TabContext";
import { Link } from "react-router-dom";
import axios from "axios";
import "./Admin.css";

const Admin = () => {
  const token = sessionStorage.getItem("token");

  const { activeTab, setActiveTab } = useTab();
  const [title, setTitle] = useState("");
  const [diaryEntries, setDiaryEntries] = useState([]);
  const [userList, setUserList] = useState([]);

  const filteredEntries = diaryEntries.filter((entry) =>
    entry.title.toLowerCase().includes(title.toLowerCase())
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/user/users/details`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 200) {
          setUserList(response.data);
        }
      } catch (err) {
        alert("사용자 목록을 가져오는 데 실패했습니다.");
      }
    };

    fetchData();
  }, []); // eslint-disable-next-line react-hooks/exhaustive-deps

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/user/pages`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 200) {
          setDiaryEntries(response.data);
        }
      } catch (err) {
        alert("블로그를 가져오는 데 실패했습니다.");
      }
    };

    fetchData();
  }, []); // eslint-disable-next-line react-hooks/exhaustive-deps

  const handleDeleteUser = (user_email) => {
    const fetchData = async () => {
      try {
        const response = await axios.delete(
          `http://localhost:8000/user/users/email/${user_email}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 200) {
          alert("사용자를 삭제하였습니다.");
          window.location.reload();
        }
      } catch (err) {
        alert("사용자를 삭제하는 중에 오류가 발생했습니다.");
      }
    };

    fetchData();
  };

  return (
    <div className="admin">
      {/* 탭 영역 */}
      <div className="tab-header">
        <button
          className={`tab-button ${activeTab === "account" ? "active" : ""}`}
          onClick={() => setActiveTab("account")}
        >
          Account
        </button>
        <button
          className={`tab-button ${activeTab === "blog" ? "active" : ""}`}
          onClick={() => setActiveTab("blog")}
        >
          Blog
        </button>
      </div>

      {/* 조건부 렌더링 */}
      {activeTab === "account" && (
        <>
          <div className="list-containerAdm">
            <h2>사용자 계정 목록</h2>
            <table className="list-table">
              <tbody>
                {userList.map((el, i) => (
                  <tr className="list-item" key={el.id}>
                    <td className="icon-column">{i + 1}.</td>
                    <td className="title-column">{el.username}</td>
                    <td className="title-column email-cell">
                      {el.email}
                      <button
                        className="delete-button"
                        onClick={() => handleDeleteUser(el.email)}
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {activeTab === "blog" && (
        <div className="blog-container">
          <div className="search-section">
            <input
              type="text"
              className="search-input"
              placeholder="검색어를 입력하세요"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <hr />
          <div className="search-results">
            {filteredEntries.length > 0 ? (
              filteredEntries.map((entry) => (
                <Link
                  key={entry.id}
                  to={`/diary/${entry.owner_id}/${
                    entry.created_at.split("T")[0]
                  }/${entry.id}`}
                  state={{
                    entryTitle: entry.title,
                    id: entry.id,
                    entryOwner: entry.owner_id,
                  }}
                  style={{ textDecoration: "none" }}
                >
                  <div className="blog-entry">
                    <h3 className="entry-title1">{entry.title}</h3>
                    <h3 className="entry-date">
                      {entry.created_at.split("T")[0]}
                    </h3>
                  </div>
                </Link>
              ))
            ) : (
              <p>검색 결과가 없습니다.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
