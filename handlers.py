from db import Session, Expense, Gas, Benzin
from reports import export_excel, export_pdf

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler


# ---------------- STATES ----------------
CHOOSING_TYPE, GAS_INPUT, BENZIN_INPUT, EXPENSE_INPUT = range(4)


# ---------------- MAIN MENU ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⛽ Մեքենայի լիցքավորում (գազ)", callback_data="gas")],
        [InlineKeyboardButton("⛽ Մեքենայի լիցքավորում (բենզին)", callback_data="benzin")],
        [InlineKeyboardButton("💸 Սովորական ծախս", callback_data="expense")],
        [InlineKeyboardButton("📊 Հաշվետվություն Excel ֆորմատով", callback_data="report")],
        [InlineKeyboardButton("📄 Հաշվետվություն PDF ֆորմատով", callback_data="report_pdf")],
    ])


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Բարի գալուստ ծախսերի բոտ\n\nԸնտրեք տարբերակը 👇",
        reply_markup=main_menu()
    )
    return CHOOSING_TYPE


# ---------------- CALLBACK HANDLER ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    username = query.from_user.username or "unknown"

    # ---------------- GAS ----------------
    if data == "gas":
        await query.message.reply_text(
            "⛽ Մուտքագրեք՝\n«ընդհանուր արժեք», «մեկ լիտրի գինը», «մեքենայի տվյալ պահի վազքը» (optional)"
        )
        return GAS_INPUT

    # ---------------- BENZIN ----------------
    if data == "benzin":
        await query.message.reply_text(
            "⛽ Մուտքագրեք՝\n«ընդհանուր արժեք», «մեկ լիտրի գինը»"
        )
        return BENZIN_INPUT

    # ---------------- EXPENSE ----------------
    elif data == "expense":
        await query.message.reply_text(
            "💸 Մուտքագրեք՝\n«ընդհանուր ծախս», «պատճառ»"
        )
        return EXPENSE_INPUT

    # ---------------- EXCEL REPORT ----------------
    elif data == "report":
        await query.message.reply_text("📊 Հաշվետվությունը պատրաստվում է...")

        file_path = export_excel(username)

        with open(file_path, "rb") as f:
            await query.message.reply_document(
                document=f,
                caption="📊 Excel Report"
            )

        return CHOOSING_TYPE

    # ---------------- PDF REPORT ----------------
    elif data == "report_pdf":
        await query.message.reply_text("📄 PDF հաշվետվությունը պատրաստվում է...")

        file_path = export_pdf(username)

        with open(file_path, "rb") as f:
            await query.message.reply_document(
                document=f,
                caption="📄 PDF Report"
            )

        return CHOOSING_TYPE

    return CHOOSING_TYPE


# ---------------- GAS INPUT ----------------
async def gas_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        parts = [x.strip() for x in text.split(",")]

        amount = float(parts[0])
        price = float(parts[1])
        km = int(parts[2]) if len(parts) > 2 and parts[2] else None

    except:
        await update.message.reply_text("❌ Սխալ ֆորմատ։ Օրինակ՝ 20000,210,128500")
        return GAS_INPUT

    try:
        liters = round(amount / price, 2)
    except ZeroDivisionError:
        await update.message.reply_text("❌ Մեկ լիտրի գինը չի կարող լինել զրո։")
        return GAS_INPUT

    session = Session()
    gas = Gas(
        user=update.message.from_user.username or "unknown",
        amount=amount,
        price=price,
        liters=liters,
        km=km
    )

    session.add(gas)
    session.commit()

    await update.message.reply_text(
        f"""
✅ Պահպանված է\n⛽ Համպատասխան Ձեր ներկայացրած տվյալների
Ընդհանուր լիցքավորվել է
    {liters} լիտր
    Գին մեկ լիտրի համար՝ {price} դրամ
    Ընդհանուր արժեք՝ {amount} դրամ
    {f"Վազք՝ {km} կմ" if km else ""}
        """,
        reply_markup=main_menu()
    )

    return CHOOSING_TYPE


async def benzin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        parts = [x.strip() for x in text.split(",")]

        amount = float(parts[0])
        price = float(parts[1])

    except:
        await update.message.reply_text("❌ Սխալ ֆորմատ։ Օրինակ՝ 20000,210,128500")
        return BENZIN_INPUT

    liters = round(amount / price, 2)

    session = Session()
    benzin = Benzin(
        user=update.message.from_user.username or "unknown",
        amount=amount,
        price=price,
        liters=liters,
    )

    session.add(benzin)
    session.commit()

    await update.message.reply_text(
        f"""
✅ Պահպանված է\n⛽ Համպատասխան տվյալների
Ընդհանուր լիցքավորվել է
    {liters} լիտր
    Գին մեկ լիտրի համար՝ {price} դրամ
    Ընդհանուր արժեք՝ {amount} դրամ
        """,
        reply_markup=main_menu()
    )

    return CHOOSING_TYPE

# ---------------- EXPENSE INPUT ----------------
async def expense_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        amount_str, reason = text.split(",", 1)

        amount = float(amount_str.strip())
        reason = reason.strip()

    except:
        await update.message.reply_text("❌ Սխալ ֆորմատ։ Օրինակ՝ 5000, Parking")
        return EXPENSE_INPUT

    session = Session()

    expense = Expense(
        user=update.message.from_user.username or "unknown",
        amount=amount,
        reason=reason
    )

    session.add(expense)
    session.commit()

    await update.message.reply_text(
        "✅ Պահպանված է",
        reply_markup=main_menu()
    )

    return CHOOSING_TYPE


# ---------------- REPORT HANDLER (optional) ----------------
async def report_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username or "unknown"

    file_path = export_excel(username)

    await update.message.reply_document(
        document=open(file_path, "rb"),
        caption="📊 Excel Report"
    )

    return CHOOSING_TYPE


# ---------------- PDF REPORT ----------------
async def report_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username or "unknown"

    file_path = export_pdf(username)

    await update.message.reply_document(
        document=open(file_path, "rb"),
        caption="📄 PDF Report"
    )


# ---------------- CANCEL ----------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Չեղարկված է")
    return ConversationHandler.END
