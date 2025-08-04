// 私人金融分析师 - 主JavaScript文件

// ===== 全局变量 =====
let sidebarOpen = true;
let currentUser = null;

// ===== 页面加载完成后初始化 =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    checkAuthentication();
    setupEventListeners();
});

// ===== 应用初始化 =====
function initializeApp() {
    console.log('🚀 私人金融分析师系统启动');
    
    // 检查本地存储的主题设置
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
    
    // 检查侧边栏状态
    const sidebarState = localStorage.getItem('sidebarOpen');
    if (sidebarState !== null) {
        sidebarOpen = JSON.parse(sidebarState);
        updateSidebarState();
    }
}

// ===== 认证检查 =====
function checkAuthentication() {
    const token = localStorage.getItem('accessToken');
    const currentPath = window.location.pathname;
    
    // 如果在登录页面，不需要检查认证
    if (currentPath === '/login') {
        return;
    }
    
    // 如果没有token且不在登录页，重定向到登录页
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    // 验证token有效性
    validateToken(token);
}

// ===== Token验证 =====
async function validateToken(token) {
    try {
        const response = await fetch('/api/v1/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            updateUserInterface();
        } else {
            // Token无效，清除并重定向
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Token validation error:', error);
        // 网络错误时不强制重定向，允许离线使用
    }
}

// ===== 更新用户界面 =====
function updateUserInterface() {
    if (currentUser) {
        // 更新用户名显示
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(element => {
            element.textContent = currentUser.username || 'User';
        });
        
        // 可以根据用户权限显示/隐藏功能
        updateUIBasedOnPermissions();
    }
}

// ===== 基于权限更新UI =====
function updateUIBasedOnPermissions() {
    if (!currentUser || !currentUser.permissions) return;
    
    // 这里可以根据用户权限显示/隐藏菜单项
    const permissions = currentUser.permissions;
    
    // 示例：如果没有AI助手权限，隐藏相关菜单
    if (!permissions.includes('USE_AI_ASSISTANT')) {
        const chatMenuItem = document.querySelector('a[href="/chat"]');
        if (chatMenuItem) {
            chatMenuItem.parentElement.style.display = 'none';
        }
    }
}

// ===== 事件监听器设置 =====
function setupEventListeners() {
    // 侧边栏切换
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // 全局键盘快捷键
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // 窗口大小变化
    window.addEventListener('resize', handleWindowResize);
    
    // 页面可见性变化
    document.addEventListener('visibilitychange', handleVisibilityChange);
}

// ===== 侧边栏控制 =====
function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
    updateSidebarState();
    localStorage.setItem('sidebarOpen', JSON.stringify(sidebarOpen));
}

function updateSidebarState() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (!sidebar || !mainContent) return;
    
    if (sidebarOpen) {
        sidebar.classList.remove('collapsed');
        mainContent.style.marginLeft = '260px';
    } else {
        sidebar.classList.add('collapsed');
        mainContent.style.marginLeft = '0';
    }
}

// ===== 键盘快捷键处理 =====
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + / 切换侧边栏
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        toggleSidebar();
    }
    
    // Escape 关闭模态框
    if (event.key === 'Escape') {
        closeAllModals();
    }
}

// ===== 窗口大小变化处理 =====
function handleWindowResize() {
    const width = window.innerWidth;
    
    // 在移动设备上自动收起侧边栏
    if (width < 768 && sidebarOpen) {
        sidebarOpen = false;
        updateSidebarState();
    }
}

// ===== 页面可见性变化处理 =====
function handleVisibilityChange() {
    if (document.hidden) {
        // 页面隐藏时的处理
        console.log('页面已隐藏');
    } else {
        // 页面显示时的处理
        console.log('页面已显示');
        // 可以在这里刷新数据
        refreshCurrentPageData();
    }
}

// ===== 刷新当前页面数据 =====
function refreshCurrentPageData() {
    const currentPath = window.location.pathname;
    
    switch (currentPath) {
        case '/':
        case '/dashboard':
            if (typeof loadDashboardData === 'function') {
                loadDashboardData();
            }
            break;
        case '/chat':
            if (typeof loadChatHistory === 'function') {
                loadChatHistory();
            }
            break;
        case '/stocks':
            if (typeof loadStocksList === 'function') {
                loadStocksList();
            }
            break;
    }
}

// ===== 通知系统 =====
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    // 清除之前的类
    notification.className = 'notification';
    notification.classList.add(type);
    notification.textContent = message;
    
    // 显示通知
    notification.classList.add('show');
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
    }, duration);
}

// ===== 加载指示器 =====
function showLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// ===== 模态框控制 =====
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
    document.body.style.overflow = 'auto';
}

// ===== 登出功能 =====
async function logout() {
    if (!confirm('确定要退出登录吗？')) {
        return;
    }
    
    showLoading();
    
    try {
        // 调用登出API
        const token = localStorage.getItem('accessToken');
        if (token) {
            await fetch('/api/v1/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
        }
    } catch (error) {
        console.error('Logout API error:', error);
    } finally {
        // 清除本地存储
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('currentUser');
        
        hideLoading();
        
        // 重定向到登录页
        window.location.href = '/login';
    }
}

// ===== 主题切换 =====
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    showNotification(`已切换到${newTheme === 'dark' ? '深色' : '浅色'}模式`, 'success');
}

// ===== 错误处理 =====
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    
    // 在开发环境显示错误
    if (window.location.hostname === 'localhost') {
        showNotification('页面出现错误，请查看控制台', 'error');
    }
});

// ===== 未处理的Promise拒绝 =====
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    
    if (window.location.hostname === 'localhost') {
        showNotification('网络请求失败，请重试', 'error');
    }
});

// ===== 工具函数 =====

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 格式化数字
function formatNumber(num, precision = 2) {
    if (typeof num !== 'number') return num;
    
    if (num >= 1e9) {
        return (num / 1e9).toFixed(precision) + 'B';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(precision) + 'M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(precision) + 'K';
    }
    
    return num.toFixed(precision);
}

// 格式化日期
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
    const d = new Date(date);
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('已复制到剪贴板', 'success');
        return true;
    } catch (error) {
        console.error('Copy failed:', error);
        showNotification('复制失败', 'error');
        return false;
    }
}

// 生成随机ID
function generateRandomId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// ===== 导出全局函数 =====
window.toggleSidebar = toggleSidebar;
window.logout = logout;
window.showNotification = showNotification;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.openModal = openModal;
window.closeModal = closeModal;
window.toggleTheme = toggleTheme;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.copyToClipboard = copyToClipboard;

console.log('✅ 主JavaScript文件加载完成');