import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import axios from "axios";
import "./Diary.css";

const Diary = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { date } = useParams();
  const token = sessionStorage.getItem("token");
  const user_id = sessionStorage.getItem("user_id");
  const is_admin = sessionStorage.getItem("is_admin");

  const { entryTitle, id, entryOwner } = location.state || {};

  const [isPublic, setIsPublic] = useState(true);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);

  const toggleVisibility = () => {
    setIsPublic(!isPublic);
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
      setImageFile(file); // 실제 파일 객체 저장
    }
  };

  const handleImageClick = () => {
    document.getElementById("file-input").click(); // 이미지 클릭 시 file input 클릭
  };

  const handleSubmit = async () => {
    if (!title) {
      alert("제목을 입력해주세요.");
      return;
    }

    if (!content) {
      alert("내용을 입력해주세요.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("content", content);
      formData.append("public", isPublic);
      formData.append("scheduled_at", date);
      formData.append("owner_id", Number(user_id));

      if (imageFile) {
        formData.append("files", imageFile);
      }

      if (id) {
        console.log("수정================= ");

        const updateResponse = await axios.put(
          `http://localhost:8000/user/pages/${id}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (updateResponse.status === 200) {
          alert("일기가 수정되었습니다.");
          navigate("/calendar");
        }
      } else {
        console.log("작성================= ");
        const textResponse = await axios.post(
          "http://localhost:8000/user/pages",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (textResponse.status === 200) {
          alert("일기가 저장되었습니다.");
          navigate("/calendar");
        }
      }
    } catch (error) {
      console.error("Upload Failed:", error);
      alert("일기가 저장되지 않았습니다.");
    }
  };

  useEffect(() => {
    if (!entryTitle) {
      return;
    }

    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/user/pages/?title=${entryTitle}`,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.length > 0) {
          const entry = response.data[0]; // 하나의 일기만 있는 경우
          setTitle(entry.title);
          setContent(entry.content);
          setIsPublic(entry.public);

          if (response.data[0].fileurl.length === 0) {
            setImage(null);
          } else {
            const imgUrl = `http://localhost:8000/${entry.fileurl[0]}`;

            setImage(imgUrl);
          }
        }
      } catch (err) {
        alert("일기 데이터를 가져오는 데 실패했습니다.");
      }
    };

    fetchData();
  }, []);

  const handleDelete = async () => {
    try {
      const response = await axios.delete(
        `http://localhost:8000/user/pages/${id}`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 200) {
        alert("일기를 삭제하였습니다.");
        if (is_admin === "true") {
          navigate("/admin");
        } else {
          navigate("/calendar");
        }
      }
    } catch (err) {
      alert("일기를 삭제하는데 실패했습니다.");
    }
  };

  return (
    <div className="diary-container">
      <div className="title-section">
        <input
          type="text"
          className="title-input"
          placeholder="제목을 입력하세요"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <div className="toggle-switch" onClick={toggleVisibility}>
          <div className={`toggle ${isPublic ? "on" : ""}`}>
            <div className="toggle-button">
              <span className="toggle-text">
                {isPublic ? "Public" : "Private"}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div className="content-section">
        <div className="image-upload">
          {image ? (
            <div>
              <img
                src={image}
                alt="Uploaded"
                className="uploaded-image"
                onClick={handleImageClick} // 이미지 클릭 시 수정할 수 있게 함
              />
              <label className="image-edit">
                <input
                  id="file-input"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  style={{ display: "none" }} // 파일 input 숨기기
                />
              </label>
            </div>
          ) : (
            <label className="image-placeholder">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
              />
              +
            </label>
          )}
        </div>
        <textarea
          className="content-input"
          placeholder="오늘은 어땠나요?"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
      </div>
      {is_admin === "true" ? (
        <div className="button-container">
          <button className="cancel-button" onClick={handleDelete}>
            삭제
          </button>
          <button
            style={{ marginLeft: "10px" }}
            className="cancel-button"
            onClick={() => navigate(-1)}
          >
            취소
          </button>
        </div>
      ) : entryOwner === undefined ? (
        <div className="button-container">
          <button className="submit-button" onClick={handleSubmit}>
            저장
          </button>
          <button
            style={{ marginLeft: "10px" }}
            className="cancel-button"
            onClick={() => navigate(-1)}
          >
            취소
          </button>
        </div>
      ) : entryOwner == user_id ? (
        <div className="button-container">
          <button className="submit-button" onClick={handleSubmit}>
            {id ? "수정" : "저장"}
          </button>
          {id ? (
            <button
              style={{ marginLeft: "10px" }}
              className="cancel-button"
              onClick={handleDelete}
            >
              삭제
            </button>
          ) : (
            ""
          )}
          <button
            style={{ marginLeft: "10px" }}
            className="cancel-button"
            onClick={() => navigate(-1)}
          >
            취소
          </button>
        </div>
      ) : (
        ""
      )}
    </div>
  );
};

export default Diary;
