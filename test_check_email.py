import os
from dotenv import load_dotenv
from supabase import create_client
from fastapi import HTTPException

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or SUPABASE_KEY  # Fallback to project key

def get_supabase():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY/SUPABASE_SERVICE_KEY in .env")
    print(f"Using key prefix: {'SERVICE' if os.getenv('SUPABASE_SERVICE_KEY') else 'KEY'}")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def check_email_exists(email: str) -> bool:
    try:
        supabase = get_supabase()

        response = (
            supabase.table("users")
            .select("email")
            .eq("email", email.strip().lower())
            .limit(1)
            .execute()
        )

        if response.data is None:
            raise Exception("Resposta inválida do Supabase")

        return len(response.data) > 0

    except Exception as e:
        print("Erro real:", e)
        raise HTTPException(status_code=500, detail="Erro ao verificar email")

if __name__ == "__main__":
    print("Testing user's check_email_exists function...")
    print("Note: Uses SUPABASE_SERVICE_KEY from .env")
    
    # Test 1: Non-existing email
    print("\n1. Testing non-existing email 'test@nonexistent.com':")
    try:
        result1 = check_email_exists("test@nonexistent.com")
        print(f"   Result: {result1}")
        if not result1:
            print("   ✅ PASSED: Returned False as expected")
        else:
            print("   ❌ FAILED: Should return False")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Existing email (provided by user)
    print("\n2. Testing existing email 'ellen.caroliny@ufrpe.br':")
    try:
        result2 = check_email_exists("ellen.caroliny@ufrpe.br")
        print(f"   Result: {result2}")
        if result2:
            print("   ✅ PASSED: Returned True as expected")
        else:
            print("   ⚠️  Returned False (email may not exist in 'users' table)")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\nTest complete.")
