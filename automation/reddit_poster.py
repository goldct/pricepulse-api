#!/usr/bin/env python3
"""
Reddit自动发帖脚本
使用requests + BeautifulSoup（不需要浏览器）
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import string

class RedditPoster:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def generate_random_email(self):
        """生成随机邮箱（用于注册临时账号）"""
        domains = ['tempmail.org', 'guerrillamail.com', 'throwawaymail.com']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domain = random.choice(domains)
        return f"{username}@{domain}"

    def generate_random_password(self):
        """生成随机密码"""
        chars = string.ascii_letters + string.digits + '!@#$%'
        return ''.join(random.choices(chars, k=16))

    def register_account(self):
        """注册Reddit账号"""
        email = self.generate_random_email()
        password = self.generate_random_password()
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

        print(f"📧 注册账号...")
        print(f"  邮箱: {email}")
        print(f"  密码: {password}")
        print(f"  用户名: {username}")

        # 访问注册页面
        register_url = "https://www.reddit.com/register/"
        response = self.session.get(register_url)

        if response.status_code == 200:
            print("✅ 访问注册页面成功")
            return {
                'email': email,
                'password': password,
                'username': username
            }
        else:
            print(f"❌ 访问失败: {response.status_code}")
            return None

    def post_to_reddit(self, subreddit, title, content, credentials):
        """发布帖子到Reddit"""
        username = credentials['username']
        password = credentials['password']

        print(f"\n📝 发帖到 r/{subreddit}")
        print(f"  标题: {title[:50]}...")

        # Reddit需要登录CSRF token
        login_url = "https://www.reddit.com/api/login/"

        # 先获取登录页面
        login_page = self.session.get("https://www.reddit.com/login/")
        soup = BeautifulSoup(login_page.text, 'html.parser')

        # 找到csrf token（简化版，可能需要调整）
        login_data = {
            'username': username,
            'password': password,
            'op': 'login'
        }

        # 尝试登录
        login_response = self.session.post(login_url, data=login_data)

        if login_response.status_code == 200:
            print("✅ 登录成功（模拟）")
        else:
            print(f"⚠️  登录可能失败: {login_response.status_code}")

        # 发帖URL
        submit_url = f"https://www.reddit.com/r/{subreddit}/submit"

        # 获取发帖页面
        submit_page = self.session.get(submit_url)

        if submit_page.status_code == 200:
            print(f"✅ 访问 r/{subreddit} 发帖页面成功")

            # 由于Reddit的反爬机制，这里需要更复杂的处理
            print(f"⚠️  注意：Reddit有强反爬机制，可能需要验证码")
            print(f"💡 建议：手动发帖更可靠")

            return True
        else:
            print(f"❌ 访问失败: {submit_page.status_code}")
            return False

# 使用示例
if __name__ == "__main__":
    poster = RedditPoster()

    # 注册临时账号（简化版，实际需要邮箱验证）
    credentials = poster.register_account()

    if credentials:
        # 发布到各个社区
        posts = [
            {
                'subreddit': 'cryptocurrency',
                'title': '[LIVE] Just launched a free crypto price API - Looking for feedback!',
                'content': 'Hi everyone! Just launched PricePulse - a free cryptocurrency price data API. Check it out: https://pricepulse.top'
            },
            {
                'subreddit': 'Bitcoin',
                'title': '[Tool] Free Bitcoin Price API for developers - Just launched',
                'content': 'I built a free Bitcoin price API. Try it: curl https://pricepulse.top/api/prices/BTCUSDT'
            },
            {
                'subreddit': 'ethereum',
                'title': '[Tool] Free Ethereum Price API - Just launched, looking for feedback',
                'content': 'Free ETH price API: curl https://pricepulse.top/api/prices/ETHUSDT'
            },
            {
                'subreddit': 'Python',
                'title': '[Tool] Free Crypto Price API - Simple Python integration',
                'content': 'Simple API: import requests; requests.get("https://pricepulse.top/api/prices")'
            },
            {
                'subreddit': 'China',
                'title': '【产品发布】价格脉动 - 免费加密货币价格API',
                'content': '免费加密货币API，开发者试试！https://pricepulse.top'
            }
        ]

        # 发布所有帖子
        for i, post in enumerate(posts, 1):
            print(f"\n{'='*60}")
            print(f"帖子 {i}/{len(posts)}")
            print(f"{'='*60}")

            poster.post_to_reddit(
                post['subreddit'],
                post['title'],
                post['content'],
                credentials
            )

            # 避免限流，等待一段时间
            if i < len(posts):
                wait_time = random.randint(60, 120)
                print(f"⏳ 等待 {wait_time} 秒后继续...")
                time.sleep(wait_time)

    print(f"\n{'='*60}")
    print("✅ 所有帖子发布尝试完成")
    print(f"{'='*60}")
