# infra/supabaseClient.py
import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL ou SUPABASE_SERVICE_KEY não foram carregados.")

    return create_client(url, key)