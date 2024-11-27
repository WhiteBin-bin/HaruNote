import React, { useState } from "react";
import "./Calendar.css";

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
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

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDayOfMonth = daysInMonth[0].getDay();

  const lastDayOfMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth() + 1,
    0
  ).getDate(); // 매번 현재 달에 맞게 계산

  const prevMonthDays = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth(),
    0
  ).getDate();

  const totalCells = Math.ceil((firstDayOfMonth + daysInMonth.length) / 7) * 7;

  return (
    <div className="notion-table-calendar">
      <div className="calendar-header">
        <button onClick={handlePrevMonth}>◀</button>
        <h2>
          {currentDate.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
          })}
        </h2>
        <button onClick={handleNextMonth}>▶</button>
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

                    const isCurrentMonth = date > 0 && date <= lastDayOfMonth;
                    const isSpecial = date === 31;

                    return (
                      <td
                        key={colIndex}
                        className={`${
                          prevDate > 0 && nextDate < lastDayOfMonth
                            ? "date"
                            : "date faded"
                        } ${colIndex === 0 || colIndex === 6 ? "weekend" : ""}`}
                        data-date={
                          isCurrentMonth ? date : isSpecial ? date : ""
                        }
                      >
                        <button
                          className="cell-button"
                          onClick={handleOpenModal}
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

      {/* 모달 컴포넌트 */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()} // 모달 내부 클릭 시 닫히지 않도록
          >
            <h2>Modal</h2>
            <p>This is a modal window!</p>
            {/* <button onClick={handleCloseModal}>Close</button> */}
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;
