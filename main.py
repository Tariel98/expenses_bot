import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from handlers import (
    start,
    button_handler,
    gas_input,
    expense_input,
    cancel,
    CHOOSING_TYPE,
    GAS_INPUT,
    EXPENSE_INPUT,
    BENZIN_INPUT,
    benzin_input,
)

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ---------------- CONVERSATION ----------------
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            CHOOSING_TYPE: [
                CallbackQueryHandler(button_handler),
            ],
            GAS_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gas_input),
            ],
            BENZIN_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, benzin_input),
            ],
            EXPENSE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, expense_input),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    
    print("🤖 Bot is running...")
    app.run_polling()


# ---------------- RUN ----------------
if __name__ == "__main__":
    main()