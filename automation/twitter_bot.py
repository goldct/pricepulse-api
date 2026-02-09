#!/usr/bin/env python3
"""
Twitter自动发推脚本
使用tweepy库（Twitter官方Python库）
"""

import tweepy
import json
import random
import string
import time
from datetime import datetime

class TwitterBot:
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        """初始化Twitter API客户端"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        # 创建API客户端
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

    def generate_random_email(self):
        """生成随机邮箱"""
        domains = ['tempmail.org', 'guerrillamail.com', 'throwawaymail.com']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domain = random.choice(domains)
        return f"{username}@{domain}"

    def generate_random_password(self):
        """生成随机密码"""
        chars = string.ascii_letters + string.digits + '!@#$%'
        return ''.join(random.choices(chars, k=16))

    def register_account(self):
        """注册Twitter账号（需要手机验证，简化版）"""
        email = self.generate_random_email()
        password = self.generate_random_password()
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

        print(f"📧 注册Twitter账号...")
        print(f"  邮箱: {email}")
        print(f"  密码: {password}")
        print(f"  用户名: {username}")

        print(f"\n⚠️  注意：Twitter需要手机验证")
        print(f"💡 建议：使用虚拟手机号服务")

        return {
            'email': email,
            'password': password,
            'username': username
        }

    def post_tweet(self, tweet_text, media_url=None):
        """发布推文"""
        try:
            print(f"\n📝 发布推文...")
            print(f"  内容: {tweet_text[:80]}...")

            if media_url:
                # 如果有图片
                media = self.api.media_upload(media_url)
                response = self.client.create_tweet(
                    text=tweet_text,
                    media_ids=[media.media_id]
                )
            else:
                # 纯文本推文
                response = self.client.create_tweet(text=tweet_text)

            if response.data:
                print(f"✅ 推文发布成功")
                print(f"  推文ID: {response.data['id']}")
                print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print(f"❌ 推文发布失败")
                return False

        except tweepy.TweepyException as e:
            print(f"❌ Twitter API错误: {e}")
            return False

    def reply_tweet(self, tweet_id, reply_text):
        """回复推文"""
        try:
            response = self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=tweet_id
            )

            if response.data:
                print(f"✅ 回复成功")
                return True
            else:
                print(f"❌ 回复失败")
                return False

        except tweepy.TweepyException as e:
            print(f"❌ 回复错误: {e}")
            return False

    def post_all_tweets(self, tweets, delay_hours=4):
        """批量发布所有推文"""
        print(f"\n🚀 开始批量发布 {len(tweets)} 条推文")
        print(f"📅 每条推文间隔: {delay_hours} 小时")

        success_count = 0
        fail_count = 0

        for i, tweet in enumerate(tweets, 1):
            print(f"\n{'='*60}")
            print(f"推文 {i}/{len(tweets)}")
            print(f"{'='*60}")

            success = self.post_tweet(tweet['text'], tweet.get('media_url'))

            if success:
                success_count += 1
            else:
                fail_count += 1

            # 如果不是最后一条，等待
            if i < len(tweets):
                print(f"\n⏳ 等待 {delay_hours} 小时后发布下一条...")
                time.sleep(delay_hours * 3600)

        print(f"\n{'='*60}")
        print(f"✅ 批量发布完成")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print(f"{'='*60}")

# 推文内容（21条，7天）
TWEETS = [
    {
        "day": 1,
        "time": "09:00",
        "text": """🚀 Just launched PricePulse - Free Crypto Price API!

✅ Real-time prices (BTC, ETH, SOL, and 10+ more)
✅ <100ms latency
✅ 99.9% uptime
✅ Free tier available (300 req/hour)

📍 https://pricepulse.top

#crypto #API #bitcoin #ethereum #developer #SaaS"""
    },
    {
        "day": 1,
        "time": "14:00",
        "text": """📊 Why choose PricePulse?

✅ Multi-exchange data aggregation (Coinbase + Binance)
✅ Lightning-fast response (<100ms)
✅ Simple RESTful API
✅ Flexible pricing (Free → Pro)
✅ 99.9% uptime

Start for free: https://pricepulse.top

#API #cryptocurrency #fintech #startup #developer"""
    },
    {
        "day": 1,
        "time": "20:00",
        "text": """💻 Developers, try our crypto price API in 1 line:

curl https://pricepulse.top/api/prices

Get instant price data with minimal setup! 🚀

📍 Full docs: https://pricepulse.top/docs

#coding #API #webdev #Python #JavaScript #REST"""
    },
    # Day 2-7的推文...
]

# 使用示例
if __name__ == "__main__":
    # 需要从 https://developer.twitter.com/ 获取API密钥
    # 或者在 https://apps.twitter.com/ 创建应用

    print("⚠️  需要Twitter API密钥")
    print("📍 访问: https://developer.twitter.com/")
    print("📍 或访问: https://apps.twitter.com/")

    # 示例配置
    api_key = "YOUR_API_KEY"
    api_secret = "YOUR_API_SECRET"
    access_token = "YOUR_ACCESS_TOKEN"
    access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

    # 初始化bot
    bot = TwitterBot(api_key, api_secret, access_token, access_token_secret)

    # 发布所有推文
    # bot.post_all_tweets(TWEETS, delay_hours=4)

    # 或者单条发布
    # bot.post_tweet(TWEETS[0]['text'])
