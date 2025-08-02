# 前端聊天框AI助手接口集成指南

## 🎯 核心接口

### 聊天接口
**POST** `/api/v1/assistant/chat`

## 🔐 认证要求

1. **JWT Token**: 需要在请求头中包含有效的认证令牌
2. **用户权限**: 用户必须拥有 `USE_AI_ASSISTANT` 权限

## 📝 接口详情

### 请求格式

```javascript
const requestData = {
  message: "用户输入的消息内容",
  context: {  // 可选的上下文信息
    stock_data: {...},
    market_data: {...}
  }
}
```

### 响应格式

```javascript
const response = {
  message: "AI助手的回复内容",
  suggestions: ["快速操作建议1", "快速操作建议2"],  // 可选
  charts: {...},                                    // 可选图表数据
  analysis_data: {...},                            // 可选分析数据
  timestamp: "2025-08-02T08:47:49.399826"
}
```

## 💻 前端实现示例

### 1. 基础API调用函数

```javascript
// utils/aiApi.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

// 获取认证令牌
export async function login(username, password) {
  const response = await axios.post(`${API_BASE_URL}/auth/login`, {
    username,
    password
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
  return response.data.access_token
}

// AI聊天接口
export async function sendChatMessage(message, token, context = null) {
  try {
    const response = await axios.post(`${API_BASE_URL}/assistant/chat`, {
      message,
      context
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    return {
      success: true,
      data: response.data
    }
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || '服务暂时不可用'
    }
  }
}
```

### 2. Vue 3 聊天组件示例

```vue
<!-- components/AIChat.vue -->
<template>
  <div class="ai-chat-container">
    <!-- 聊天消息列表 -->
    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="['message', msg.type]"
      >
        <div class="message-content">
          <div class="text">{{ msg.content }}</div>
          <div class="timestamp">{{ formatTime(msg.timestamp) }}</div>
        </div>
        
        <!-- AI回复的建议按钮 -->
        <div v-if="msg.type === 'ai' && msg.suggestions" class="suggestions">
          <button 
            v-for="suggestion in msg.suggestions"
            :key="suggestion"
            @click="sendMessage(suggestion)"
            class="suggestion-btn"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="chat-input">
      <div class="input-group">
        <input
          v-model="inputMessage"
          @keypress.enter="sendMessage()"
          placeholder="请输入您的问题..."
          :disabled="loading"
          class="message-input"
        />
        <button 
          @click="sendMessage()"
          :disabled="loading || !inputMessage.trim()"
          class="send-btn"
        >
          <span v-if="!loading">发送</span>
          <span v-else>发送中...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { sendChatMessage, login } from '@/utils/aiApi'

// 响应式数据
const inputMessage = ref('')
const loading = ref(false)
const messages = reactive([])
const messagesContainer = ref(null)
const authToken = ref(localStorage.getItem('auth_token'))

// 发送消息
async function sendMessage(message = null) {
  const content = message || inputMessage.value.trim()
  if (!content || loading.value) return

  // 添加用户消息
  messages.push({
    type: 'user',
    content,
    timestamp: new Date()
  })

  // 清空输入框
  if (!message) inputMessage.value = ''
  
  loading.value = true
  scrollToBottom()

  try {
    // 调用AI接口
    const result = await sendChatMessage(content, authToken.value)
    
    if (result.success) {
      // 添加AI回复
      messages.push({
        type: 'ai',
        content: result.data.message,
        suggestions: result.data.suggestions,
        timestamp: new Date()
      })
    } else {
      // 错误处理
      messages.push({
        type: 'error',
        content: `错误: ${result.error}`,
        timestamp: new Date()
      })
    }
  } catch (error) {
    messages.push({
      type: 'error',
      content: '网络错误，请稍后重试',
      timestamp: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 格式化时间
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString()
}

// 组件挂载时的初始化
onMounted(async () => {
  // 如果没有认证令牌，先登录
  if (!authToken.value) {
    try {
      const token = await login('admin', 'admin123') // 这里应该使用实际的登录流程
      authToken.value = token
      localStorage.setItem('auth_token', token)
    } catch (error) {
      console.error('登录失败:', error)
    }
  }

  // 发送欢迎消息
  messages.push({
    type: 'ai',
    content: '您好！我是您的专业金融分析师助手。我可以帮您分析股票、解读市场趋势、提供投资建议。请告诉我您想了解什么？',
    suggestions: ['分析具体股票', '查看市场概况', '获取投资建议', '风险评估'],
    timestamp: new Date()
  })
})
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 500px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  background: #fff;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
}

.message.user .message-content {
  background: #007bff;
  color: white;
  border-radius: 18px 18px 4px 18px;
}

.message.ai .message-content {
  background: #f8f9fa;
  color: #333;
  border-radius: 18px 18px 18px 4px;
}

.message.error .message-content {
  background: #f8d7da;
  color: #721c24;
  border-radius: 18px 18px 18px 4px;
}

.message-content {
  padding: 12px 16px;
  word-wrap: break-word;
}

.text {
  font-size: 14px;
  line-height: 1.4;
  white-space: pre-wrap;
}

.timestamp {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 4px;
}

.suggestions {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.suggestion-btn {
  padding: 4px 12px;
  border: 1px solid #007bff;
  background: white;
  color: #007bff;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: #007bff;
  color: white;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e1e5e9;
}

.input-group {
  display: flex;
  gap: 8px;
}

.message-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
}

.message-input:focus {
  border-color: #007bff;
}

.send-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.send-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}
</style>
```

### 3. React 聊天组件示例

```jsx
// components/AIChat.jsx
import React, { useState, useEffect, useRef } from 'react'
import { sendChatMessage, login } from '../utils/aiApi'

const AIChat = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [authToken, setAuthToken] = useState(localStorage.getItem('auth_token'))
  const messagesEndRef = useRef(null)

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [messages])

  // 发送消息
  const handleSendMessage = async (message = null) => {
    const content = message || inputMessage.trim()
    if (!content || loading) return

    // 添加用户消息
    const userMessage = {
      type: 'user',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    if (!message) setInputMessage('')
    setLoading(true)

    try {
      const result = await sendChatMessage(content, authToken)
      
      if (result.success) {
        const aiMessage = {
          type: 'ai',
          content: result.data.message,
          suggestions: result.data.suggestions,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, aiMessage])
      } else {
        const errorMessage = {
          type: 'error',
          content: `错误: ${result.error}`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: '网络错误，请稍后重试',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  // 初始化
  useEffect(() => {
    const initChat = async () => {
      // 登录获取token
      if (!authToken) {
        try {
          const token = await login('admin', 'admin123')
          setAuthToken(token)
          localStorage.setItem('auth_token', token)
        } catch (error) {
          console.error('登录失败:', error)
        }
      }

      // 欢迎消息
      setMessages([{
        type: 'ai',
        content: '您好！我是您的专业金融分析师助手。我可以帮您分析股票、解读市场趋势、提供投资建议。请告诉我您想了解什么？',
        suggestions: ['分析具体股票', '查看市场概况', '获取投资建议', '风险评估'],
        timestamp: new Date()
      }])
    }

    initChat()
  }, [])

  return (
    <div className="ai-chat-container">
      {/* 消息列表 */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-content">
              <div className="text">{msg.content}</div>
              <div className="timestamp">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
            
            {/* 建议按钮 */}
            {msg.type === 'ai' && msg.suggestions && (
              <div className="suggestions">
                {msg.suggestions.map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendMessage(suggestion)}
                    className="suggestion-btn"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="chat-input">
        <div className="input-group">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="请输入您的问题..."
            disabled={loading}
            className="message-input"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={loading || !inputMessage.trim()}
            className="send-btn"
          >
            {loading ? '发送中...' : '发送'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default AIChat
```

## 🔧 实际测试

```bash
# 测试聊天接口
curl -X POST "http://localhost:8000/api/v1/assistant/chat" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "请分析一下当前A股市场的投资机会"
     }'
```

## ⚠️ 注意事项

1. **认证处理**: 确保用户已登录并获取有效的JWT令牌
2. **权限检查**: 用户必须拥有`USE_AI_ASSISTANT`权限
3. **错误处理**: 妥善处理网络错误、认证失败、权限不足等情况
4. **加载状态**: 在等待AI回复时显示加载状态
5. **消息格式**: AI回复支持换行符，需要正确渲染
6. **建议按钮**: 利用AI返回的suggestions提供快速操作

## 🌟 高级功能

1. **上下文传递**: 通过context参数传递股票数据等上下文信息
2. **流式响应**: 可考虑实现WebSocket或Server-Sent Events支持流式回复
3. **历史记录**: 利用`/api/v1/assistant/conversation-history`接口获取历史对话
4. **智能建议**: 利用`/api/v1/assistant/suggestions`接口获取智能操作建议