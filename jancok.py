import random
import string
import requests
import os
from pystyle import Colors, Colorate
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import signal

class NGLBot:
    def __init__(self, token: str):
        self.token = token
        self.active_attacks = {}
        self.application = None

    def deviceId(self):  
        characters = string.ascii_lowercase + string.digits  
        part1 = ''.join(random.choices(characters, k=8))  
        part2 = ''.join(random.choices(characters, k=4))  
        part3 = ''.join(random.choices(characters, k=4))  
        part4 = ''.join(random.choices(characters, k=4))  
        part5 = ''.join(random.choices(characters, k=12))  
        device_id = f"{part1}-{part2}-{part3}-{part4}-{part5}"  
        return device_id  
    
    def UserAgent(self):  
        try:  
            with open('user-agents.txt', 'r') as file:  
                user_agents = file.readlines()  
                random_user_agent = random.choice(user_agents).strip()  
                return random_user_agent  
        except:  
            user_agents = [  
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",  
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",  
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"  
            ]  
            return random.choice(user_agents)  
            
    def Proxy(self):  
        try:  
            with open('proxies.txt', 'r') as file:  
                proxies_list = file.readlines()  
                if not proxies_list:  
                    return None  
                random_proxy = random.choice(proxies_list).strip()  
            proxies = {  
                'http': random_proxy,  
                'https': random_proxy  
            }  
            return proxies  
        except:  
            return None  

    def send_ngl_message(self, nglusername: str, message: str, use_proxy: bool = False):  
        headers = {  
            'Host': 'ngl.link',  
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',  
            'accept': '*/*',  
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',  
            'x-requested-with': 'XMLHttpRequest',  
            'sec-ch-ua-mobile': '?0',  
            'user-agent': f'{self.UserAgent()}',  
            'sec-ch-ua-platform': '"Windows"',  
            'origin': 'https://ngl.link',  
            'sec-fetch-site': 'same-origin',  
            'sec-fetch-mode': 'cors',  
            'sec-fetch-dest': 'empty',  
            'referer': f'https://ngl.link/{nglusername}',  
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',  
        }  

        data = {  
            'username': f'{nglusername}',  
            'question': f'{message}',  
            'deviceId': f'{self.deviceId()}',  
            'gameSlug': '',  
            'referrer': '',  
        }  

        proxies = self.Proxy() if use_proxy else None  

        try:  
            response = requests.post('https://ngl.link/api/submit', headers=headers, data=data, proxies=proxies, timeout=10)  
            return response.status_code == 200  
        except:  
            return False  

    async def spamngl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):  
        user_id = update.effective_user.id  
        
        if user_id in self.active_attacks:  
            await update.message.reply_text("🔄 Kamu masih memiliki spam yang berjalan. Tunggu sampai selesai.")  
            return  

        if len(context.args) < 3:  
            await update.message.reply_text(
                "📝 *Cara Pakai:*\n"
                "⚡ `/spamngl username pesan jumlah`\n\n"
                "📌 *Contoh:*\n"
                "🎯 `/spamngl johndoe hello world 100`\n"
                "🎯 `/spamngl janedoe test 50`\n\n"
                "⏱️ Delay otomatis 1 detik",
                parse_mode='Markdown'
            )  
            return  

        nglusername = context.args[0]  
        message = context.args[1]  
        
        try:  
            count = int(context.args[2])  
        except ValueError:  
            await update.message.reply_text("❌ Jumlah harus angka!")  
            return  

        if count > 500:  
            await update.message.reply_text("❌ Maksimal 500 pesan per spam!")  
            return  

        delay = 1.0  
        use_proxy = False  

        self.active_attacks[user_id] = True  
        asyncio.create_task(self.run_spam(update, context, user_id, nglusername, message, count, delay, use_proxy))  
        
        await update.message.reply_text(  
            f"🚀 *Memulai Spam NGL*\n\n"
            f"👤 Username: `{nglusername}`\n"
            f"💬 Pesan: `{message}`\n"
            f"🔢 Jumlah: `{count}`\n"
            f"⏱️ Delay: `{delay}s`\n\n"
            f"⏳ Mohon tunggu...",
            parse_mode='Markdown'
        )  

    async def run_spam(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int,   
                      nglusername: str, message: str, count: int, delay: float, use_proxy: bool):  
        sent = 0  
        failed = 0  
        consecutive_fails = 0  
        
        status_msg = await update.message.reply_text(  
            f"📊 *Status Spam*\n"
            f"✅ Terkirim: `0/{count}`\n"
            f"❌ Gagal: `0`\n"
            f"⏳ Progress: `0%`",
            parse_mode='Markdown'
        )  

        for i in range(count):  
            if not self.active_attacks.get(user_id, False):  
                break  

            success = self.send_ngl_message(nglusername, message, use_proxy)  
            
            if success:  
                sent += 1  
                consecutive_fails = 0  
                print(Colorate.Horizontal(Colors.green_to_blue, f"✅ Pesan {sent} berhasil dikirim ke {nglusername}"))  
            else:  
                failed += 1  
                consecutive_fails += 1  
                print(Colorate.Horizontal(Colors.red_to_yellow, f"❌ Gagal mengirim pesan {sent + failed} ke {nglusername}"))  

            if (i + 1) % 5 == 0 or consecutive_fails >= 3 or i == count - 1:  
                progress = int((sent / count) * 100)  
                success_rate = int((sent / (sent + failed)) * 100) if (sent + failed) > 0 else 0  
                
                try:  
                    await status_msg.edit_text(  
                        f"📊 *Status Spam*\n"
                        f"✅ Terkirim: `{sent}/{count}`\n"
                        f"❌ Gagal: `{failed}`\n"
                        f"⏳ Progress: `{progress}%`\n"
                        f"🎯 Success Rate: `{success_rate}%`",
                        parse_mode='Markdown'
                    )  
                except:  
                    pass  

            if consecutive_fails >= 5:  
                await update.message.reply_text("⚠️ Banyak kegagalan berturut-turut. Menghentikan spam...")  
                break  

            await asyncio.sleep(delay)  

        if user_id in self.active_attacks:  
            del self.active_attacks[user_id]  

        final_success_rate = int((sent / (sent + failed)) * 100) if (sent + failed) > 0 else 0  
        
        await status_msg.edit_text(  
            f"🏁 *Spam Selesai*\n\n"
            f"✅ Berhasil: `{sent}` pesan\n"
            f"❌ Gagal: `{failed}` pesan\n"
            f"📊 Success Rate: `{final_success_rate}%`\n"
            f"👤 Target: `{nglusername}`\n"
            f"💬 Pesan: `{message}`",
            parse_mode='Markdown'
        )  

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):  
        await update.message.reply_text(  
            "🤖 *NGL Spammer Bot*\n\n"
            "📋 *Perintah:*\n"
            "• /start - Menampilkan pesan ini\n"
            "• /spamngl - Memulai spam NGL\n"
            "• /stop - Menghentikan spam\n\n"
            "📌 *Contoh:*\n"
            "🎯 `/spamngl username pesan jumlah`\n"
            "🎯 `/spamngl johndoe hello world 50`\n\n"
            "⏱️ Delay otomatis 1 detik\n"
            "🔢 Maksimal 500 pesan per spam",
            parse_mode='Markdown'
        )  

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):  
        user_id = update.effective_user.id  
        
        if user_id in self.active_attacks:  
            del self.active_attacks[user_id]  
            await update.message.reply_text("🛑 Spam berhasil dihentikan!")  
        else:  
            await update.message.reply_text("ℹ️ Tidak ada spam yang berjalan.")  

    def setup_handlers(self):
        """Setup command handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("spamngl", self.spamngl))
        self.application.add_handler(CommandHandler("stop", self.stop))

    def print_banner(self):
        """Print banner dengan warna"""
        print(Colorate.Horizontal(Colors.blue_to_purple, """
        
    ███╗   ██╗ ██████╗ ██╗         ███████╗██████╗  █████╗ ███╗   ███╗███╗   ███╗███████╗██████╗ 
    ████╗  ██║██╔════╝ ██║         ██╔════╝██╔══██╗██╔══██╗████╗ ████║████╗ ████║██╔════╝██╔══██╗
    ██╔██╗ ██║██║  ███╗██║         ███████╗██████╔╝███████║██╔████╔██║██╔████╔██║█████╗  ██████╔╝
    ██║╚██╗██║██║   ██║██║         ╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██╔══██╗
    ██║ ╚████║╚██████╔╝███████╗    ███████║██║     ██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║  ██║
    ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝    ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                                  
        """))
        print(Colorate.Horizontal(Colors.green_to_blue, "🤖 NGL Bot sedang berjalan..."))
        print(Colorate.Horizontal(Colors.yellow_to_red, "📝 Gunakan /start di Telegram untuk mulai"))
        print(Colorate.Horizontal(Colors.rainbow, "=" * 50))

    def run(self):
        """Jalankan bot dengan cara yang sederhana"""
        try:
            # Buat aplikasi
            self.application = Application.builder().token(self.token).build()
            
            # Setup handlers
            self.setup_handlers()
            
            # Print banner
            self.print_banner()
            
            # Jalankan bot
            print(Colorate.Horizontal(Colors.green_to_blue, "🚀 Bot mulai polling..."))
            self.application.run_polling()
            
        except KeyboardInterrupt:
            print(Colorate.Horizontal(Colors.red_to_yellow, "\n🛑 Bot dihentikan oleh pengguna"))
        except Exception as e:
            print(Colorate.Horizontal(Colors.red_to_yellow, f"❌ Error: {e}"))

if __name__ == "__main__":
    BOT_TOKEN = "8505449691:AAFgjpJWJl75rC2cIWSwZPRsZBG0XxUhTeo"

    bot = NGLBot(BOT_TOKEN)  
    bot.run()
