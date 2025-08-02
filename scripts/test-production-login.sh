#!/bin/bash

# =====================================================
# 生产环境登录测试脚本
# =====================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKEND_URL="http://localhost:8000"
LOGIN_ENDPOINT="/api/v1/auth/login"
HEALTH_ENDPOINT="/health"

# 测试用户信息
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin123"

echo "=================================="
echo "🧪 生产环境登录测试"
echo "=================================="

# 1. 检查服务是否启动
echo -e "${BLUE}[1/4]${NC} 检查后端服务状态..."
if curl -f -s "${BACKEND_URL}${HEALTH_ENDPOINT}" > /dev/null; then
    echo -e "${GREEN}✓${NC} 后端服务运行正常"
else
    echo -e "${RED}✗${NC} 后端服务未启动或无法访问"
    echo "请先启动生产环境: ./scripts/production-start.sh"
    exit 1
fi

# 2. 等待服务完全启动
echo -e "${BLUE}[2/4]${NC} 等待服务完全启动..."
sleep 5

# 3. 测试admin用户登录
echo -e "${BLUE}[3/4]${NC} 测试admin用户登录..."

LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${BACKEND_URL}${LOGIN_ENDPOINT}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${ADMIN_USERNAME}&password=${ADMIN_PASSWORD}")

# 分离响应体和状态码
HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

echo "HTTP状态码: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} 登录请求成功"
    
    # 检查响应中是否包含token
    if echo "$RESPONSE_BODY" | grep -q "access_token"; then
        echo -e "${GREEN}✓${NC} 获取访问令牌成功"
        
        # 提取token
        ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('access_token', ''))
except:
    print('')
")
        
        if [ ! -z "$ACCESS_TOKEN" ]; then
            echo "令牌长度: ${#ACCESS_TOKEN} 字符"
            
            # 4. 测试使用token访问受保护资源
            echo -e "${BLUE}[4/4]${NC} 测试token访问用户信息..."
            
            PROFILE_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
                "${BACKEND_URL}/api/v1/auth/profile" \
                -H "Authorization: Bearer ${ACCESS_TOKEN}")
            
            PROFILE_HTTP_CODE=$(echo "$PROFILE_RESPONSE" | tail -n1)
            PROFILE_BODY=$(echo "$PROFILE_RESPONSE" | sed '$d')
            
            if [ "$PROFILE_HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓${NC} Token验证成功，获取用户信息成功"
                
                # 显示用户信息
                echo "用户信息:"
                echo "$PROFILE_BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"  用户名: {data.get('username', 'N/A')}\")
    print(f\"  邮箱: {data.get('email', 'N/A')}\")
    print(f\"  姓名: {data.get('full_name', 'N/A')}\")
    print(f\"  状态: {'激活' if data.get('is_active') else '未激活'}\")
except Exception as e:
    print('  无法解析用户信息')
"
                
                echo ""
                echo "=================================="
                echo -e "${GREEN}🎉 生产环境登录测试通过！${NC}"
                echo "=================================="
                exit 0
            else
                echo -e "${RED}✗${NC} Token验证失败 (HTTP: $PROFILE_HTTP_CODE)"
                echo "响应: $PROFILE_BODY"
            fi
        else
            echo -e "${RED}✗${NC} 无法提取访问令牌"
        fi
    else
        echo -e "${RED}✗${NC} 响应中未找到access_token"
        echo "响应内容: $RESPONSE_BODY"
    fi
else
    echo -e "${RED}✗${NC} 登录失败 (HTTP: $HTTP_CODE)"
    echo "响应内容: $RESPONSE_BODY"
fi

echo ""
echo "=================================="
echo -e "${RED}❌ 生产环境登录测试失败${NC}"
echo "=================================="

# 显示调试信息
echo ""
echo "🔍 调试信息:"
echo "  后端地址: $BACKEND_URL"
echo "  登录端点: $LOGIN_ENDPOINT"
echo "  测试用户: $ADMIN_USERNAME"
echo "  服务状态: $(curl -s ${BACKEND_URL}${HEALTH_ENDPOINT} || echo '无法访问')"

exit 1 