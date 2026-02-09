#!/bin/bash
# 上传修复后的主页到服务器

echo "=== 上传修复后的主页 ==="
echo ""

scp /Users/gold/clawd/million-dollar-plan/code/index_cn.html root@45.76.156.147:/var/www/pricepulse/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 上传成功！"
    echo ""
    echo "请刷新页面测试："
    echo "https://pricepulse.top"
    echo ""
else
    echo ""
    echo "❌ 上传失败"
    echo "请检查密码是否正确"
    echo ""
fi
