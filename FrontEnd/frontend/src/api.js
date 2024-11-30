// api.js
import axios from "axios";

const api = axios.create({
  baseURL: "/api", // 기본 URL 설정
});

// 요청 인터셉터 - 모든 요청에 토큰 추가
api.interceptors.request.use(
  function (config) {
    const accessToken = sessionStorage.getItem("token");
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 처리
api.interceptors.response.use(
  function (response) {
    return response;
  },
  async function (error) {
    const originalRequest = error.config;

    // 401 에러(토큰 만료)이고 재시도하지 않은 요청인 경우
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 세션 스토리지에서 refresh token 가져오기
        const refreshToken = sessionStorage.getItem("refresh_token");

        if (refreshToken) {
          const response = await api.post("/user/refresh-token", {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          sessionStorage.setItem("token", access_token);
          sessionStorage.setItem("refresh_token", refresh_token);

          // 실패한 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // refresh token도 만료된 경우
        sessionStorage.removeItem("token");
        sessionStorage.removeItem("refresh_token");
        window.location.href = "/signin"; // 로그인 페이지로 이동
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
