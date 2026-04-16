# TODO: Test User's check_email_exists function

## Steps:
- [x] Step 1: Create `test_check_email.py` with user's functions + tests for non-existing (`test@nonexistent.com`) and existing (`ellen.caroliny@ufrpe.br`) emails.
- [x] Step 2: Run `test_check_email.py` - failed due to missing SUPABASE_SERVICE_KEY.
- [ ] Step 3: Adjust to use `SUPABASE_KEY` fallback and re-test.
- [ ] Step 4: Compare with existing `auth_service.py` function.
- [ ] Step 5: Test server endpoint if needed: start `uvicorn app.main:app --reload` and curl /check-email.
- [ ] Step 6: Complete task.

**Progress: Step 1 complete, running Step 2**
