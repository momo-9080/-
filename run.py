#!/usr/bin/env python3
"""
Truth or Dare Discord Bot Runner
بوت ديسكورد للعبة حقيقة أم تحدي
"""

import os
import sys
import logging
from main import main

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ متغير DISCORD_BOT_TOKEN غير محدد أو غير صحيح")
        logger.error("يرجى تعيين رمز البوت في متغيرات البيئة")
        return False
    
    return True

def print_startup_info():
    """Print startup information"""
    print("=" * 50)
    print("🤖 بوت ديسكورد - حقيقة أم تحدي")
    print("Truth or Dare Discord Bot")
    print("=" * 50)
    print("المطور: مساعد AI")
    print("الإصدار: 1.0.0")
    print("اللغة: العربية")
    print("=" * 50)

if __name__ == "__main__":
    print_startup_info()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    logger.info("🚀 بدء تشغيل البوت...")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {e}")
        sys.exit(1)
