from pathlib import Path
import os
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from db import Session, Expense, Gas, Benzin

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/Armenian/arial.ttf")
pdfmetrics.registerFont(TTFont("NotoSans", FONT_PATH))

# ---------------- OUTPUT DIR ----------------
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


# ---------------- LOAD DATA ----------------
def get_user_data(username: str):
    session = Session()

    # ---------------- EXPENSES ----------------
    expenses = session.query(Expense).filter_by(user=username).all()

    expense_data = [
        {
            "table": "expense",
            "user": r.user,
            "amount": r.amount,
            "reason": r.reason,
            "created_at": r.created_at,
        }
        for r in expenses
    ]

    # ---------------- GAS ----------------
    gas_rows = session.query(Gas).filter_by(user=username).all()

    gas_data = [
        {
            "table": "gas",
            "amount": r.amount,
            "user": r.user,
            "price": r.price,
            "liters": r.liters,
            "km": r.km,
            "created_at": r.created_at,
        }
        for r in gas_rows
    ]

    benzin_rows = session.query(Benzin).filter_by(user=username).all()

    benzin_data = [
        {
            "table": "benzin",
            "amount": r.amount,
            "user": r.user,
            "price": r.price,
            "liters": r.liters,
            "created_at": r.created_at,
        }
        for r in benzin_rows
    ]
    return expense_data + gas_data + benzin_data


# ---------------- EXCEL REPORT ----------------
def export_excel(username: str):
    data = get_user_data(username)
    file_path = REPORTS_DIR / f"{username}_report.xlsx"

    if file_path.exists():
        os.remove(file_path)

    if not data:
        df = pd.DataFrame(columns=[
            "table", "id", "user", "amount",
            "price", "liters", "km", "reason", "created_at"
        ])
    else:
        df = pd.DataFrame(data)

    expense_df = df[df["table"] == "expense"] if not df.empty else pd.DataFrame()
    gas_df = df[df["table"] == "gas"] if not df.empty else pd.DataFrame()
    benzin_df = df[df["table"] == "benzin"] if not df.empty else pd.DataFrame()

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="All Data", index=False)

        if not gas_df.empty:
            gas_df.to_excel(writer, sheet_name="Gas", index=False)

        if not expense_df.empty:
            expense_df.to_excel(writer, sheet_name="Expenses", index=False)

        if not benzin_df.empty:
            benzin_df.to_excel(writer, sheet_name="Benzin", index=False)

        summary = pd.DataFrame([{
            "Total Gas Cost": gas_df["amount"].sum() if not gas_df.empty else 0,
            "Total Benzin Cost": benzin_df["amount"].sum() if not benzin_df.empty else 0,
            "Total Expenses": expense_df["amount"].sum() if not expense_df.empty else 0,
            "Total Records": len(df)
        }])

        summary.to_excel(writer, sheet_name="Summary", index=False)

    return str(file_path)


def gen_unique_filename(base_name: str, extension: str):
    counter = 1
    while True:
        file_name = f"{base_name}_#{counter}.{extension}"
        file_path = REPORTS_DIR / file_name
        if not file_path.exists():
            return str(file_path)
        counter += 1

# ---------------- PDF REPORT ----------------
def export_pdf(username: str):
    data = get_user_data(username)

    file_path = REPORTS_DIR / f"{username}_report.pdf"

    if os.path.exists(file_path):
        os.remove(file_path)

    doc = SimpleDocTemplate(str(file_path))

    styles = getSampleStyleSheet()
    armenian_style = ParagraphStyle(
        name="Armenian",
        fontName="NotoSans",
        fontSize=14,
        leading=14,
        spaceafter=10,
        )

    armenian_style_title = ParagraphStyle(
        name="ArmenianTitle",
        fontName="NotoSans",
        fontSize=18,
        leading=18,
        spaceafter=5,
        )
    elements = []

    # ---------------- TITLE ----------------
    elements.append(Paragraph(f"<b>Հաշվետվություն {username}֊ի համար </b>", armenian_style_title))
    elements.append(Spacer(1, 18))

    if not data:
        elements.append(Paragraph("Հասանելի տվյալներ չկան", armenian_style))
        doc.build(elements)
        return str(file_path)

    df = pd.DataFrame(data)

    expense_df = df[df["table"] == "expense"]
    gas_df = df[df["table"] == "gas"]
    benzin_df = df[df["table"] == "benzin"]

    # ---------------- SUMMARY ----------------
    gas_total = gas_df["amount"].sum() if not gas_df.empty else 0
    gas_liter_total = gas_df["liters"].sum() if not gas_df.empty else 0
    expense_total = expense_df["amount"].sum() if not expense_df.empty else 0
    benzin_total = benzin_df["amount"].sum() if not benzin_df.empty else 0

    summary = Paragraph(
        f"""
        <b>Ընդհանուր գազ:</b> {gas_total} դրամ<br/>
        <b>Ընդհանուր գազի լիտրեր:</b> {gas_liter_total:.2f} լ<br/>
        <b>Ընդհանուր բենզին:</b> {benzin_total} դրամ<br/>
        <b>Ընդհանուր ծախսեր:</b> {expense_total} դրամ<br/>
        <b>Ընդհանուր ծախսված գումար:</b> {gas_total + benzin_total + expense_total} դրամ<br/>
        """,
        armenian_style
    )

    elements.append(summary)
    elements.append(Spacer(1, 18))

    # ---------------- GAS TABLE ----------------
    if not gas_df.empty:
        elements.append(Paragraph("Լիցքավորված գազ", armenian_style))
        elements.append(Spacer(1, 18))
        
        if "reason" in gas_df.columns:
            gas_df = gas_df.drop(columns=["reason"])
        if "user" in gas_df.columns:
            gas_df = gas_df.drop(columns=["user"])

        gas_df = gas_df.replace({pd.NaT: ""})
        gas_df = gas_df.replace({np.nan: ""})
        gas_df["created_at"] = pd.to_datetime(gas_df["created_at"]).dt.strftime("%Y-%m-%d-%H-%M")
        gas_table = Table(
            [gas_df.columns.tolist()] + gas_df.astype(str).values.tolist()
        )

        gas_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))

        gas_table.hAlign = "LEFT"
        elements.append(gas_table)
        elements.append(Spacer(1, 12))

    # ---------------- BENZIN TABLE ----------------
    if not benzin_df.empty:
        elements.append(Paragraph("Լիցքավորված բենզին", armenian_style))
        elements.append(Spacer(1, 18))

        if "reason" in benzin_df.columns:
            benzin_df = benzin_df.drop(columns=["reason"])
        if "user" in benzin_df.columns:
            benzin_df = benzin_df.drop(columns=["user"])
        if "km" in benzin_df.columns:
            benzin_df = benzin_df.drop(columns=["km"])
        
        benzin_df = benzin_df.replace({pd.NaT: ""})
        benzin_df = benzin_df.replace({np.nan: ""})
        benzin_df["created_at"] = pd.to_datetime(benzin_df["created_at"]).dt.strftime("%Y-%m-%d-%H-%M")
        benzin_table = Table(
            [benzin_df.columns.tolist()] + benzin_df.astype(str).values.tolist()
        )

        benzin_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))


        benzin_table.hAlign = "LEFT"
        elements.append(benzin_table)
        elements.append(Spacer(1, 12))

    # ---------------- EXPENSE TABLE ----------------
    if not expense_df.empty:
        elements.append(Paragraph("Ընդհանուր ծախսեր", armenian_style))
        elements.append(Spacer(1, 18))
        if "price" in expense_df.columns:
            expense_df = expense_df.drop(columns=["price"])
        if "liters" in expense_df.columns:
            expense_df = expense_df.drop(columns=["liters"])
        if "km" in expense_df.columns:
            expense_df = expense_df.drop(columns=["km"])
        if "user" in expense_df.columns:
            expense_df = expense_df.drop(columns=["user"])

        expense_df["created_at"] = pd.to_datetime(expense_df["created_at"]).dt.strftime("%Y-%m-%d-%H-%M")

        expense_table = Table(
            [expense_df.columns.tolist()] + expense_df.astype(str).values.tolist()
        )

        expense_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        expense_table.hAlign = "LEFT"
        elements.append(expense_table)

    doc.build(elements)
    return str(file_path)