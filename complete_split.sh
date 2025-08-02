#!/bin/bash

echo "🚀 完成项目彻底分离..."

# 创建备份
echo "📦 创建备份..."
cp -r ../private_financial_analyst_backend ../private_financial_analyst_backend_backup
cp -r ../private_financial_analyst_frontend ../private_financial_analyst_frontend_backup

# 移动所有剩余目录到后端（除了frontend、backend和两个新项目目录）
echo "📁 移动剩余目录到后端..."
for dir in agents auth config data database logs scripts temp_scripts tests tools; do
    if [ -d "$dir" ]; then
        echo "移动 $dir 到后端项目..."
        cp -r "$dir" ../private_financial_analyst_backend/ 2>/dev/null || echo "$dir 已存在"
    fi
done

# 移动所有剩余文件到后端
echo "📄 移动剩余文件到后端..."
for file in *.py *.md *.txt *.yml *.yaml *.conf *.sh *.dockerfile Dockerfile .gitignore; do
    if [ -f "$file" ]; then
        echo "移动 $file 到后端项目..."
        cp "$file" ../private_financial_analyst_backend/ 2>/dev/null || echo "$file 已存在"
    fi
done

# 移动隐藏目录
echo "🔍 移动隐藏目录..."
for dir in .pytest_cache; do
    if [ -d "$dir" ]; then
        echo "移动 $dir 到后端项目..."
        cp -r "$dir" ../private_financial_analyst_backend/ 2>/dev/null || echo "$dir 已存在"
    fi
done

echo "✅ 文件移动完成!"

# 检查结果
echo "📊 检查结果:"
echo "原项目剩余文件数量: $(ls -la | grep -E '^-' | wc -l)"
echo "原项目剩余目录数量: $(ls -la | grep -E '^d' | grep -v -E "^(\.|backend|frontend|private_financial_analyst_backend|private_financial_analyst_frontend)$" | wc -l)"
echo "后端项目文件数量: $(ls -la ../private_financial_analyst_backend/ | wc -l)"
echo "前端项目文件数量: $(ls -la ../private_financial_analyst_frontend/ | wc -l)"

