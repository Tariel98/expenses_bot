import pandas as pd
from db import Session, Expense


def get_user_data(username: str):
    session = Session()

    rows = session.query(Expense).filter_by(user=username).all()

    data = []
    for r in rows:
        data.append({
            "type": r.type,
            "amount": r.amount,
            "price": r.price,
            "liters": r.liters,
            "km": r.km,
            "reason": r.reason,
            "date": r.created_at,
        })

    return pd.DataFrame(data)


def monthly_summary(username: str):
    df = get_user_data(username)

    if df.empty:
        return None

    gas = df[df["type"] == "gas"]["amount"].sum()
    exp = df[df["type"] == "expense"]["amount"].sum()

    return gas, exp