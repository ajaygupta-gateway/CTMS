import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // CRITICAL: Send cookies with requests
});

api.interceptors.request.use((config) => {
    // DO NOT send expired access token to refresh endpoint
    // otherwise the backend will return 401 before processing the refresh cookie
    if (config.url === '/auth/refresh/') {
        return config;
    }

    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });

    failedQueue = [];
};

api.interceptors.response.use(
    (response) => {
        // Handle auto-refresh from backend middleware
        const newAccessToken = response.headers['x-new-access-token'];
        if (newAccessToken) {
            localStorage.setItem('access_token', newAccessToken);
            api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
        }
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers['Authorization'] = 'Bearer ' + token;
                        return api(originalRequest);
                    })
                    .catch((err) => {
                        return Promise.reject(err);
                    });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // Call refresh endpoint - refresh_token is sent automatically via cookies
                // No need to send it in the request body
                const response = await api.post('/auth/refresh/', {});

                if (response.data.access) {
                    localStorage.setItem('access_token', response.data.access);
                    api.defaults.headers.common['Authorization'] = 'Bearer ' + response.data.access;
                    processQueue(null, response.data.access);
                    originalRequest.headers['Authorization'] = 'Bearer ' + response.data.access;
                    return api(originalRequest);
                }
            } catch (err) {
                processQueue(err, null);
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                window.location.href = '/login';
                return Promise.reject(err);
            } finally {
                isRefreshing = false;
            }
        }

        // --- IP BLOCK / CAPTCHA HANDLING ---
        if (error.response?.status === 403 && error.response.data?.captcha) {
            const question = error.response.data.captcha;

            return new Promise((resolve, reject) => {
                // Listen for the solved answer
                const handleSolved = (event: any) => {
                    const answer = event.detail.answer;

                    if (answer !== null) {
                        // Retry the request with the answer in header
                        originalRequest.headers['X-Captcha-Answer'] = answer;
                        resolve(api(originalRequest));
                    } else {
                        reject(error);
                    }

                    window.removeEventListener('captcha-solved', handleSolved);
                };

                window.addEventListener('captcha-solved', handleSolved);

                // Trigger the modal
                window.dispatchEvent(new CustomEvent('show-captcha', {
                    detail: { question }
                }));
            });
        }

        return Promise.reject(error);
    }
);

export default api;
