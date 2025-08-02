# 私人金融分析师 - 前端界面

这是私人金融分析师系统的前端用户界面。

## 项目简介

基于Vue 3和TypeScript开发的现代化金融分析前端应用，提供直观的股票数据查看、AI分析结果展示、用户管理等功能。

## 技术栈

- **框架**: Vue 3
- **语言**: TypeScript
- **构建工具**: Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: SCSS
- **图表**: ECharts
- **HTTP客户端**: Axios

## 项目结构

```
private_financial_analyst_frontend/
├── public/                 # 静态资源
├── src/                   # 源代码
│   ├── api/              # API接口
│   ├── assets/           # 静态资源（图片、样式等）
│   ├── components/       # 公共组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia状态管理
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口
├── index.html            # HTML模板
├── package.json          # 项目配置
├── tsconfig.json         # TypeScript配置
├── vite.config.ts        # Vite配置
└── README.md            # 项目说明
```

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn

### 安装步骤

1. **克隆项目**
```bash
git clone <your-repository-url>
cd private_financial_analyst_frontend
```

2. **安装依赖**
```bash
npm install
# 或
yarn install
```

3. **配置环境变量**
复制 `.env.example` 到 `.env` 并修改配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8000

# 应用配置
VITE_APP_TITLE=私人金融分析师
VITE_APP_VERSION=1.0.0

# 其他配置
VITE_ENABLE_MOCK=false
```

4. **启动开发服务器**
```bash
npm run dev
# 或
yarn dev
```

应用将在 http://localhost:3000 启动

## 脚本命令

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 类型检查
npm run type-check

# 代码格式化
npm run format

# 代码检查
npm run lint

# 依赖更新
npm run deps:update
```

## 主要功能

### 1. 用户认证
- 用户登录/注册
- JWT令牌管理
- 权限控制

### 2. 股票数据展示
- 实时股价显示
- 历史数据图表
- 技术指标可视化
- 自选股管理

### 3. AI分析界面
- 智能对话界面
- 投资建议展示
- 市场趋势分析
- 风险评估报告

### 4. 仪表板
- 数据概览
- 性能指标
- 快捷操作

### 5. 系统管理
- 用户管理（管理员）
- 系统配置
- 日志查看

## 开发指南

### 代码规范
- 遵循Vue 3 Composition API规范
- 使用TypeScript进行类型约束
- 组件命名采用PascalCase
- 文件命名采用kebab-case

### 组件开发
```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 组件逻辑
const data = ref<string>('')

const computedValue = computed(() => {
  return data.value.toUpperCase()
})

onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
.component-name {
  /* 样式 */
}
</style>
```

### 状态管理
使用Pinia进行状态管理：
```typescript
// stores/example.ts
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', {
  state: () => ({
    data: ''
  }),
  
  getters: {
    formattedData: (state) => state.data.toUpperCase()
  },
  
  actions: {
    async fetchData() {
      // 异步操作
    }
  }
})
```

### API调用
```typescript
// api/example.ts
import { apiClient } from '@/utils/api'

export const exampleApi = {
  getData: () => apiClient.get('/api/data'),
  postData: (data: any) => apiClient.post('/api/data', data)
}
```

## 构建和部署

### 构建生产版本
```bash
npm run build
```

构建产物将生成在 `dist/` 目录。

### Docker部署
创建 `Dockerfile`：
```dockerfile
FROM node:16-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建和运行：
```bash
docker build -t financial-frontend .
docker run -p 80:80 financial-frontend
```

### 静态部署
构建后的文件可以部署到任何静态文件服务器：
- Nginx
- Apache
- CDN服务
- Vercel/Netlify

## 环境配置

### 开发环境
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_MOCK=true
```

### 生产环境
```env
VITE_API_BASE_URL=https://api.yourdomian.com
VITE_ENABLE_MOCK=false
```

## 性能优化

### 代码分割
路由级别的代码分割已配置：
```typescript
{
  path: '/dashboard',
  component: () => import('@/views/Dashboard.vue')
}
```

### 组件懒加载
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const AsyncComponent = defineAsyncComponent(() => import('./HeavyComponent.vue'))
</script>
```

### 构建优化
- Tree shaking
- 资源压缩
- 代码分割
- 静态资源优化

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 指定端口启动
   npm run dev -- --port 3001
   ```

2. **构建失败**
   ```bash
   # 清除缓存
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **类型错误**
   ```bash
   # 运行类型检查
   npm run type-check
   ```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: your-email@example.com
- 项目Issues: [GitHub Issues](https://github.com/your-username/private_financial_analyst_frontend/issues)