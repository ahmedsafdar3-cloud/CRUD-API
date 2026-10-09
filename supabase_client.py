import os
from dotenv import load_dotenv
from supabase import create_client
from functools import lru_cache

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@lru_cache(maxsize=1)
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)
