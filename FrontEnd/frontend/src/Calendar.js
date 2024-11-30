import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTab } from "./TabContext";
import axios from "axios";
import "./Calendar.css";

const Calendar = () => {
  const navigate = useNavigate();
  const { activeTab, setActiveTab } = useTab();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [diaryEntries, setDiaryEntries] = useState([]);
  const user_id = sessionStorage.getItem("user_id");
  const token = sessionStorage.getItem("token");

  const handlePrevMonth = () => {
    setCurrentDate((prevDate) => {
      const newDate = new Date(
        prevDate.getFullYear(),
        prevDate.getMonth() - 1,
        1
      );
      return newDate;
    });
  };

  const handleNextMonth = () => {
    setCurrentDate((prevDate) => {
      const newDate = new Date(
        prevDate.getFullYear(),
        prevDate.getMonth() + 1,
        1
      );
      return newDate;
    });
  };

  // 날짜 형식화 함수
  const formatDate = (year, month, day) => {
    const formattedMonth = month < 10 ? `0${month}` : month;
    const formattedDay = day < 10 ? `0${day}` : day;
    return `${year}-${formattedMonth}-${formattedDay}`;
  };

  // URL 생성 함수
  const getDiaryURL = (isCurrent, isPrev, isNext, year, month, date) => {
    if (isCurrent) {
      return formatDate(year, month, date);
    } else if (isPrev) {
      const prevMonth = month === 1 ? 12 : month - 1;
      const prevYear = month === 1 ? year - 1 : year;
      return formatDate(prevYear, prevMonth, date);
    } else if (isNext) {
      const nextMonth = month === 12 ? 1 : month + 1;
      const nextYear = month === 12 ? year + 1 : year;
      return formatDate(nextYear, nextMonth, date);
    }
    return "";
  };

  // CSS 클래스 계산 함수
  const getClassName = (isCurrent, isPrev, isNext, colIndex) => {
    const baseClass = isCurrent ? "date" : "date faded";
    const weekendClass = colIndex === 0 || colIndex === 6 ? "weekend" : "";
    return `${baseClass} ${weekendClass}`;
  };

  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    return new Array(31)
      .fill(null)
      .map((_, i) => new Date(year, month, i + 1))
      .filter((date) => date.getMonth() === month);
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDayOfMonth = daysInMonth[0].getDay();

  const totalCells = Math.ceil((firstDayOfMonth + daysInMonth.length) / 7) * 7;

  const formatResponseDate = (dateString) => {
    const date = new Date(dateString);
    const formattedDate = date.toLocaleDateString("en-CA").split("T")[0];
    return formattedDate;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/user/pages/by-owner/${user_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`, // Authorization 헤더 추가
            },
          }
        );

        const formattedData = response.data.map((item) => ({
          ...item,
          date: formatResponseDate(item.scheduled_at), // scheduled_at 포맷팅
        }));
        setDiaryEntries(formattedData);
      } catch (err) {
        console.log("err: ", err);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="table-calendar">
      {/* 탭 영역 */}
      <div className="tab-header">
        <button
          className={`tab-button ${activeTab === "calendar" ? "active" : ""}`}
          onClick={() => setActiveTab("calendar")}
        >
          Calendar
        </button>
        <button
          className={`tab-button ${activeTab === "list" ? "active" : ""}`}
          onClick={() => setActiveTab("list")}
        >
          List
        </button>
      </div>

      {/* 조건부 렌더링 */}
      {activeTab === "calendar" && (
        <>
          <div className="calendar-header">
            <h2>
              {currentDate.toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
              })}
            </h2>
            <div className="button-group">
              <button onClick={handlePrevMonth}>&lt;</button>
              <button onClick={handleNextMonth}>&gt;</button>
            </div>
          </div>
          <table className="calendar-table">
            <thead>
              <tr>
                {daysOfWeek.map((day) => (
                  <th key={day}>{day}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array(Math.ceil(totalCells / 7))
                .fill(null)
                .map((_, rowIndex) => (
                  <tr key={rowIndex}>
                    {Array(7)
                      .fill(null)
                      .map((_, colIndex) => {
                        const cellIndex = rowIndex * 7 + colIndex;
                        let date = cellIndex - firstDayOfMonth + 1;

                        // 날짜 정보 계산
                        const currentMonth = currentDate.getMonth() + 1;
                        const currentYear = currentDate.getFullYear();
                        const lastDayOfCurrentMonth = new Date(
                          currentYear,
                          currentMonth,
                          0
                        ).getDate();

                        // 달 상태 판별
                        const isCurrentMonth =
                          date > 0 && date <= lastDayOfCurrentMonth;
                        const isPrevMonth = date <= 0;
                        const isNextMonth = date > lastDayOfCurrentMonth;

                        // 날짜 보정
                        if (isPrevMonth) {
                          date += new Date(
                            currentYear,
                            currentMonth - 1,
                            0
                          ).getDate();
                        } else if (isNextMonth) {
                          date -= lastDayOfCurrentMonth;
                        }

                        const diaryURL = getDiaryURL(
                          isCurrentMonth,
                          isPrevMonth,
                          isNextMonth,
                          currentYear,
                          currentMonth,
                          date
                        );

                        // diaryEntries에서 항목 찾기
                        const entries = diaryEntries.filter(
                          (item) => item.date === diaryURL
                        );

                        return (
                          <td
                            key={colIndex}
                            className={getClassName(
                              isCurrentMonth,
                              isPrevMonth,
                              isNextMonth,
                              colIndex
                            )}
                            data-date={date}
                          >
                            <button
                              className="cell-button"
                              onClick={() =>
                                navigate(`/diary/${user_id}/${diaryURL}/`)
                              }
                            >
                              +
                            </button>

                            <div className="entry-container">
                              {entries.length > 0 &&
                                entries.map((entry) => (
                                  <Link
                                    key={entry.id}
                                    to={`/diary/${user_id}/${diaryURL}/${entry.id}`}
                                    state={{
                                      entryTitle: entry.title,
                                      id: entry.id,
                                      entryOwner: user_id,
                                    }}
                                    style={{ textDecoration: "none" }}
                                  >
                                    <p className="entry-title">{entry.title}</p>
                                  </Link>
                                ))}
                            </div>
                          </td>
                        );
                      })}
                  </tr>
                ))}
            </tbody>
          </table>
        </>
      )}

      {activeTab === "list" && (
        <div className="list-container">
          <h2>나의 일기장 목록</h2>
          <table className="list-table">
            <tbody>
              {diaryEntries.map((entry, i) => (
                <tr className="list-item" key={i}>
                  <td className="icon-column">{i + 1}.</td>
                  <Link
                    to={`/diary/${user_id}/${entry.date}/${entry.id}`}
                    state={{ entryTitle: entry.title }}
                    style={{ textDecoration: "none" }}
                  >
                    <td className="title-column">{entry.title}</td>
                  </Link>
                  <td className="date-column">
                    {entry.scheduled_at &&
                      new Date(entry.scheduled_at).toISOString().split("T")[0]}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Calendar;
