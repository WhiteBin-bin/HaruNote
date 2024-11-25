import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Calendar.css";

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [activeTab, setActiveTab] = useState("calendar"); // 탭 상태 추가
  const navigate = useNavigate();

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

  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  let nextDate = "";

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
  const lastDayOfMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth() + 1,
    0
  ).getDate();

  const prevMonthDays = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth(),
    0
  ).getDate();

  const totalCells = Math.ceil((firstDayOfMonth + daysInMonth.length) / 7) * 7;

  return (
    <div className="notion-table-calendar">
      {/* 탭 영역 */}
      <div className="tab-header">
        <button
          className={`tab-button ${activeTab === "calendar" ? "active" : ""}`}
          onClick={() => setActiveTab("calendar")}
        >
          Calendar
        </button>
        <button
          className={`tab-button ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          Analytics
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
                        let prevDate = date;

                        if (date < 0) {
                          date = prevMonthDays + date;
                        }

                        if (date > lastDayOfMonth) {
                          nextDate = date;
                          date = date - lastDayOfMonth;
                        }

                        if (date == 0) {
                          date = prevMonthDays;
                        }

                        const isCurrentMonth =
                          date > 0 && date <= lastDayOfMonth;
                        const isSpecial = date === 31;

                        return (
                          <td
                            key={colIndex}
                            className={`${
                              prevDate > 0 && nextDate < lastDayOfMonth
                                ? "date"
                                : "date faded"
                            } ${
                              colIndex === 0 || colIndex === 6 ? "weekend" : ""
                            }`}
                            data-date={
                              isCurrentMonth ? date : isSpecial ? date : ""
                            }
                          >
                            <button
                              className="cell-button"
                              onClick={() => {
                                navigate(`/new-page/${date}`); // 이동할 경로
                              }}
                            >
                              +
                            </button>
                          </td>
                        );
                      })}
                  </tr>
                ))}
            </tbody>
          </table>
        </>
      )}

      {activeTab === "analytics" && (
        <div class="list-container">
          <h2>나의 일기장 목록</h2>
          <table class="list-table">
            <tbody>
              <tr>
                <td class="icon-column">
                  <i class="file-icon"></i>
                </td>
                <td class="title-column">뚜벅이 경주 여행 기록</td>
                <td class="date-column">2024.11.23</td>
              </tr>
              <tr>
                <td class="icon-column">
                  <i class="file-icon"></i>
                </td>
                <td class="title-column">OO전자 (1차 면접) 취준 일기</td>
                <td class="date-column">2024.09.14</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Calendar;
