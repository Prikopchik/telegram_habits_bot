import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from django.conf import settings

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Класс для работы с Telegram ботом"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            'Привет! Я бот для отслеживания привычек. '
            'Я буду напоминать вам о ваших привычках в нужное время.'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
Доступные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/habits - Показать ваши привычки
        """
        await update.message.reply_text(help_text)
    
    async def send_reminder(self, message: str, chat_id: str = None):
        """Отправка напоминания пользователю"""
        try:
            target_chat_id = chat_id or self.chat_id
            if self.application:
                await self.application.bot.send_message(
                    chat_id=target_chat_id,
                    text=message
                )
                logger.info(f"Reminder sent to {target_chat_id}: {message}")
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
    
    async def run(self):
        """Запуск бота"""
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN not set")
            return
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Telegram bot started successfully")
    
    async def stop(self):
        """Остановка бота"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")


# Глобальный экземпляр бота
bot = TelegramBot()
