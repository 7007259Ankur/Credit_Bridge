"""Load mock CSV data for agent testing."""
import os
import pandas as pd
from app.core.config import settings


MOCK_PATH = settings.MOCK_DATA_PATH


def load_mock(filename: str, user_id: int) -> pd.DataFrame:
    """Load mock CSV and filter by user_id."""
    path = os.path.join(MOCK_PATH, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "user_id" in df.columns:
        return df[df["user_id"] == user_id].copy()
    return df


def load_phone_bills(user_id: int) -> pd.DataFrame:
    return load_mock("phone_bills.csv", user_id)


def load_ecommerce(user_id: int) -> pd.DataFrame:
    return load_mock("ecommerce.csv", user_id)


def load_bank_transactions(user_id: int) -> pd.DataFrame:
    return load_mock("bank_transactions.csv", user_id)


def load_merchant(user_id: int) -> pd.DataFrame:
    return load_mock("merchant.csv", user_id)


def load_geolocation(user_id: int) -> pd.DataFrame:
    return load_mock("geolocation.csv", user_id)


def load_psychometric(user_id: int) -> dict:
    """Load psychometric answers from Redis."""
    import redis
    import json
    from app.core.config import settings

    r = redis.from_url(settings.REDIS_URL)
    key = f"psychometric:{user_id}"
    raw = r.get(key)
    if raw:
        return json.loads(raw)
    # fallback to CSV
    df = load_mock("psychometric.csv", user_id)
    if df.empty:
        return {}
    return dict(zip(df["question_id"].astype(str), df["answer"]))
