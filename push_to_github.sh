#!/bin/bash

echo "🚀 开始推送AI提示工程师2.0更新到GitHub..."
echo "=" * 50

# 检查Git状态
echo "📊 检查Git状态..."
git status

echo ""
echo "📝 最近的提交:"
git log --oneline -3

echo ""
echo "🌐 远程仓库配置:"
git remote -v

echo ""
echo "🔄 开始推送到GitHub..."

# 尝试推送
if git push origin main; then
    echo "✅ 推送成功！"
    echo "🎉 AI提示工程师2.0已成功更新到GitHub"
    echo "📱 您可以访问 https://github.com/JUNSHENG428/ai-prompt-engineer 查看更新"
else
    echo "❌ 推送失败，尝试强制推送..."
    if git push --force-with-lease origin main; then
        echo "✅ 强制推送成功！"
        echo "🎉 AI提示工程师2.0已成功更新到GitHub"
    else
        echo "❌ 推送失败，请检查网络连接和GitHub权限"
        echo "💡 您可以手动运行以下命令："
        echo "   git push origin main"
        echo "   或者"
        echo "   git push --force-with-lease origin main"
    fi
fi

echo ""
echo "📋 推送完成后的状态:"
git status

echo ""
echo "🔗 GitHub仓库地址: https://github.com/JUNSHENG428/ai-prompt-engineer"
echo "�� 查看README了解新功能使用方法" 