// 私人金融分析师 - API请求处理文件

// ===== API配置 =====
const API_CONFIG = {
    baseURL: window.location.origin,
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
};

// ===== HTTP状态码常量 =====
const HTTP_STATUS = {
    OK: 200,
    CREATED: 201,
    NO_CONTENT: 204,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500,
    SERVICE_UNAVAILABLE: 503
};

// ===== API请求类 =====
class APIClient {
    constructor(config = {}) {
        this.baseURL = config.baseURL || API_CONFIG.baseURL;
        this.timeout = config.timeout || API_CONFIG.timeout;
        this.retryAttempts = config.retryAttempts || API_CONFIG.retryAttempts;
        this.retryDelay = config.retryDelay || API_CONFIG.retryDelay;
        
        // 请求拦截器
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        
        // 设置默认的请求拦截器
        this.addRequestInterceptor(this.defaultRequestInterceptor.bind(this));
        this.addResponseInterceptor(this.defaultResponseInterceptor.bind(this));
    }
    
    // 添加请求拦截器
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }
    
    // 添加响应拦截器
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }
    
    // 默认请求拦截器
    defaultRequestInterceptor(config) {
        // 添加认证头
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers = {
                ...config.headers,
                'Authorization': `Bearer ${token}`
            };
        }
        
        // 添加默认Content-Type
        if (!config.headers['Content-Type'] && config.body && typeof config.body === 'object') {
            config.headers['Content-Type'] = 'application/json';
        }
        
        return config;
    }
    
    // 默认响应拦截器
    async defaultResponseInterceptor(response, config) {
        // 处理401未授权错误
        if (response.status === HTTP_STATUS.UNAUTHORIZED) {
            await this.handleUnauthorized();
            return response;
        }
        
        // 处理其他HTTP错误
        if (!response.ok) {
            const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
            error.response = response;
            error.status = response.status;
            throw error;
        }
        
        return response;
    }
    
    // 处理未授权错误
    async handleUnauthorized() {
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (refreshToken) {
            try {
                const response = await this.refreshAccessToken(refreshToken);
                if (response.access_token) {
                    localStorage.setItem('accessToken', response.access_token);
                    return true;
                }
            } catch (error) {
                console.error('Token refresh failed:', error);
            }
        }
        
        // 刷新失败，清除token并重定向到登录页
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
        
        return false;
    }
    
    // 刷新访问令牌
    async refreshAccessToken(refreshToken) {
        const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                refresh_token: refreshToken
            })
        });
        
        if (response.ok) {
            return await response.json();
        }
        
        throw new Error('Token refresh failed');
    }
    
    // 执行请求拦截器
    async executeRequestInterceptors(config) {
        for (const interceptor of this.requestInterceptors) {
            config = await interceptor(config);
        }
        return config;
    }
    
    // 执行响应拦截器
    async executeResponseInterceptors(response, config) {
        for (const interceptor of this.responseInterceptors) {
            response = await interceptor(response, config);
        }
        return response;
    }
    
    // 核心请求方法
    async request(url, options = {}) {
        let config = {
            method: 'GET',
            headers: {},
            ...options,
            url: url.startsWith('http') ? url : `${this.baseURL}${url}`
        };
        
        // 执行请求拦截器
        config = await this.executeRequestInterceptors(config);
        
        // 序列化请求体
        if (config.body && typeof config.body === 'object' && config.headers['Content-Type'] === 'application/json') {
            config.body = JSON.stringify(config.body);
        }
        
        let lastError;
        
        // 重试机制
        for (let attempt = 0; attempt <= this.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                
                const response = await fetch(config.url, {
                    ...config,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                // 执行响应拦截器
                const interceptedResponse = await this.executeResponseInterceptors(response, config);
                
                return interceptedResponse;
                
            } catch (error) {
                lastError = error;
                
                // 如果是最后一次尝试或者是不可重试的错误，直接抛出
                if (attempt === this.retryAttempts || this.isNonRetryableError(error)) {
                    throw error;
                }
                
                // 等待后重试
                await this.delay(this.retryDelay * Math.pow(2, attempt));
            }
        }
        
        throw lastError;
    }
    
    // 判断是否为不可重试的错误
    isNonRetryableError(error) {
        if (error.name === 'AbortError') return true;
        if (error.status && error.status >= 400 && error.status < 500) return true;
        return false;
    }
    
    // 延迟工具函数
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // GET请求
    async get(url, params = {}) {
        const urlObj = new URL(url.startsWith('http') ? url : `${this.baseURL}${url}`);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                urlObj.searchParams.append(key, params[key]);
            }
        });
        
        return this.request(urlObj.toString());
    }
    
    // POST请求
    async post(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'POST',
            body: data,
            ...options
        });
    }
    
    // PUT请求
    async put(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data,
            ...options
        });
    }
    
    // DELETE请求
    async delete(url, options = {}) {
        return this.request(url, {
            method: 'DELETE',
            ...options
        });
    }
    
    // PATCH请求
    async patch(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: data,
            ...options
        });
    }
}

// ===== 创建API客户端实例 =====
const apiClient = new APIClient();

// ===== 通用API请求函数 =====
async function apiRequest(url, options = {}) {
    try {
        const response = await apiClient.request(url, options);
        
        // 尝试解析JSON响应
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
        
    } catch (error) {
        console.error('API Request Error:', error);
        
        // 根据错误类型显示不同的提示
        let errorMessage = '请求失败，请稍后重试';
        
        if (error.name === 'AbortError') {
            errorMessage = '请求超时，请检查网络连接';
        } else if (error.status === HTTP_STATUS.UNAUTHORIZED) {
            errorMessage = '用户未授权，请重新登录';
        } else if (error.status === HTTP_STATUS.FORBIDDEN) {
            errorMessage = '权限不足，无法访问该资源';
        } else if (error.status === HTTP_STATUS.NOT_FOUND) {
            errorMessage = '请求的资源不存在';
        } else if (error.status >= HTTP_STATUS.INTERNAL_SERVER_ERROR) {
            errorMessage = '服务器错误，请稍后重试';
        }
        
        // 显示错误通知
        if (typeof showNotification === 'function') {
            showNotification(errorMessage, 'error');
        }
        
        throw error;
    }
}

// ===== 具体API方法 =====

// 认证相关API
const authAPI = {
    // 用户登录
    async login(username, password) {
        return apiClient.post('/api/v1/auth/login', null, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username,
                password
            })
        }).then(response => response.json());
    },
    
    // 用户登出
    async logout() {
        return apiClient.post('/api/v1/auth/logout');
    },
    
    // 获取用户信息
    async getProfile() {
        return apiClient.get('/api/v1/auth/profile').then(response => response.json());
    }
};

// AI助手相关API
const assistantAPI = {
    // 与AI聊天
    async chat(message, context = {}, stockCode = null) {
        return apiClient.post('/api/v1/assistant/chat', {
            message,
            context,
            stock_code: stockCode
        }).then(response => response.json());
    },
    
    // 股票分析
    async analyzeStock(stockCode, analysisType = 'comprehensive', period = '1d', days = 30) {
        return apiClient.post('/api/v1/assistant/analyze-stock', {
            stock_code: stockCode,
            analysis_type: analysisType,
            period,
            days
        }).then(response => response.json());
    },
    
    // 获取市场洞察
    async getMarketInsights(market = null, industry = null, insightType = 'overview') {
        return apiClient.post('/api/v1/assistant/market-insights', {
            market,
            industry,
            insight_type: insightType
        }).then(response => response.json());
    },
    
    // 获取智能建议
    async getSuggestions() {
        return apiClient.get('/api/v1/assistant/suggestions').then(response => response.json());
    },
    
    // 获取对话历史
    async getConversationHistory(limit = 50) {
        return apiClient.get('/api/v1/assistant/conversation-history', { limit }).then(response => response.json());
    },
    
    // 清空对话历史
    async clearConversationHistory() {
        return apiClient.delete('/api/v1/assistant/conversation-history').then(response => response.json());
    }
};

// 股票相关API
const stockAPI = {
    // 获取股票列表
    async getStocksList(params = {}) {
        return apiClient.get('/api/v1/stocks/', params).then(response => response.json());
    },
    
    // 获取股票详情
    async getStockDetail(stockCode) {
        return apiClient.get(`/api/v1/stocks/${stockCode}`).then(response => response.json());
    },
    
    // 搜索股票
    async searchStocks(query) {
        return apiClient.get('/api/v1/stocks/search', { q: query }).then(response => response.json());
    }
};

// 用户相关API
const userAPI = {
    // 获取当前用户信息
    async getCurrentUser() {
        return apiClient.get('/api/v1/users/me').then(response => response.json());
    },
    
    // 更新用户信息
    async updateProfile(data) {
        return apiClient.put('/api/v1/users/me', data).then(response => response.json());
    }
};

// ===== 请求状态管理 =====
class RequestManager {
    constructor() {
        this.pendingRequests = new Map();
        this.requestCount = 0;
    }
    
    // 开始请求
    startRequest(key = null) {
        const requestId = key || `request_${++this.requestCount}`;
        this.pendingRequests.set(requestId, Date.now());
        
        // 显示加载状态
        if (this.pendingRequests.size === 1 && typeof showLoading === 'function') {
            showLoading();
        }
        
        return requestId;
    }
    
    // 结束请求
    endRequest(requestId) {
        this.pendingRequests.delete(requestId);
        
        // 隐藏加载状态
        if (this.pendingRequests.size === 0 && typeof hideLoading === 'function') {
            hideLoading();
        }
    }
    
    // 取消所有请求
    cancelAllRequests() {
        this.pendingRequests.clear();
        if (typeof hideLoading === 'function') {
            hideLoading();
        }
    }
    
    // 是否有待处理的请求
    hasPendingRequests() {
        return this.pendingRequests.size > 0;
    }
}

const requestManager = new RequestManager();

// ===== 导出API =====
window.apiRequest = apiRequest;
window.apiClient = apiClient;
window.authAPI = authAPI;
window.assistantAPI = assistantAPI;
window.stockAPI = stockAPI;
window.userAPI = userAPI;
window.requestManager = requestManager;

console.log('✅ API处理文件加载完成');