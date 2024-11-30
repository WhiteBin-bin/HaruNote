import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import "./Blog.css";

const Blog = () => {
  const token = sessionStorage.getItem("token");
  const [title, setTitle] = useState("");

  const [diaryEntries, setDiaryEntries] = useState([]);

  const filteredEntries = diaryEntries.filter((entry) =>
    entry.title.toLowerCase().includes(title.toLowerCase())
  );

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
  }, []);

  return (
    <>
      <div className="tab-h">
        <div className="tab">HARU BLOG</div>
      </div>
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
                  entry.scheduled_at.split("T")[0]
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
    </>
  );
};

export default Blog;
