# 🔧 QUICK FIXES CHECKLIST

## ⚡ CRITICAL FIXES (Do These FIRST!)

### 1. Fix Withdrawal Email Bug
- [ ] **File:** `notifications/email_service.py`
- [ ] **Line 191:** Change `{withdrawal.withdrawal_method}` → `{withdrawal.crypto_type}`
- [ ] **Line 224:** Change `{withdrawal.withdrawal_method}` → `{withdrawal.crypto_type}`
- [ ] **Test:** Create test withdrawal, check admin email

### 2. Fix SECRET_KEY Security
- [ ] **File:** `elite_wealth/settings.py`
- [ ] **Line 16:** Replace with:
```python
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('SECRET_KEY environment variable must be set')
```

### 3. Add Missing CSRF Token
- [ ] **File:** `templates/agent-application.html`
- [ ] Add `{% csrf_token %}` inside the form tag

### 4. Wrap Signup in Transaction
- [ ] **File:** `accounts/views.py`
- [ ] **Lines 173-204:** Wrap entire signup logic in `@transaction.atomic`
- [ ] Add import: `from django.db import transaction`

### 5. Create Missing apply_coupon() View
- [ ] **File:** `investments/views.py`
- [ ] Add new view function:
```python
@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        # Implementation needed
        pass
    return redirect('investments:deposit')
```

---

## 🔴 HIGH PRIORITY (Week 1)

### 6. Create Shared Utilities
- [ ] Create file: `core/__init__.py`
- [ ] Create file: `core/validators.py`
- [ ] Move `validate_uploaded_file()` from 3 files to `core/validators.py`
- [ ] Create file: `core/utils.py`
- [ ] Move `get_client_ip()` from 2 files to `core/utils.py`
- [ ] Update all imports in:
  - `accounts/views.py`
  - `investments/views.py`
  - `kyc/views.py`

### 7. Implement Admin Panel Views
**Create 8 new views:**
- [ ] `investments/views.py` - Add `admin_approve_withdrawal()`
- [ ] `investments/views.py` - Add `admin_reject_withdrawal()`
- [ ] `investments/views.py` - Add `admin_confirm_deposit()`
- [ ] `investments/views.py` - Add `admin_reject_deposit()`
- [ ] `investments/views.py` - Add `admin_approve_loan()`
- [ ] `investments/views.py` - Add `admin_reject_loan()`
- [ ] `kyc/views.py` - Add `admin_approve_kyc()`
- [ ] `kyc/views.py` - Add `admin_reject_kyc()`

**For each view, add:**
- [ ] `@login_required` decorator
- [ ] `@user_passes_test(lambda u: u.is_staff)` check
- [ ] `@transaction.atomic` wrapper
- [ ] Balance updates
- [ ] Email notification
- [ ] Activity log entry

### 8. Add File Error Handling
- [ ] **File:** `dashboard/views.py`
- [ ] **Function:** `serve_robots_txt()` - Add try/except
- [ ] **Function:** `serve_sitemap_xml()` - Add try/except

### 9. Remove Hardcoded Values
- [ ] **File:** `accounts/views.py` Lines 25-26
  - [ ] Remove `NEW_USER_BONUS` and `REFERRER_BONUS`
  - [ ] Use `SiteSettings.get_settings()` instead
- [ ] **File:** `investments/views.py` Lines 561, 565
  - [ ] Move to `settings.py`:
```python
MIN_LOAN_AMOUNT = Decimal('100')
MAX_LOAN_AMOUNT = Decimal('50000')
```
- [ ] **File:** `elite_wealth/settings.py` Lines 420-427
  - [ ] Remove hardcoded `COMPANY_EMAILS` dict
  - [ ] Use `SiteSettings` model fields

---

## ⚠️ MEDIUM PRIORITY (Week 2)

### 10. Add Database Indexes
- [ ] **File:** `accounts/models.py` - CustomUser model
```python
class Meta:
    indexes = [
        models.Index(fields=['email']),
        models.Index(fields=['kyc_status']),
        models.Index(fields=['date_joined']),
    ]
```
- [ ] **File:** `accounts/models.py` - ActivityLog model
```python
class Meta:
    indexes = [
        models.Index(fields=['user', 'created_at']),
        models.Index(fields=['action']),
    ]
```
- [ ] **File:** `accounts/models.py` - Referral model
```python
class Meta:
    indexes = [
        models.Index(fields=['referrer']),
        models.Index(fields=['status']),
    ]
```
- [ ] Run: `python manage.py makemigrations`
- [ ] Run: `python manage.py migrate`

### 11. Add Field Validators
- [ ] **File:** `investments/models.py`
- [ ] Add to Deposit.amount:
```python
from django.core.validators import MinValueValidator
amount = models.DecimalField(
    max_digits=15,
    decimal_places=2,
    validators=[MinValueValidator(Decimal('0.01'))]
)
```
- [ ] Repeat for:
  - [ ] Withdrawal.amount
  - [ ] Loan.amount
  - [ ] Loan.interest_rate
  - [ ] Coupon.discount_value
  - [ ] Investment.amount

### 12. Fix CORS Configuration
- [ ] **File:** `elite_wealth/settings.py` Lines 393-397
- [ ] Replace with:
```python
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000').split(',')
```

### 13. Update .env.example
- [ ] Add missing variables:
```env
CORS_ALLOWED_ORIGINS=https://elitewealthcapita.uk,http://localhost:8000
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

---

## 📝 LOW PRIORITY (Week 3+)

### 14. Write Tests
- [ ] Create `accounts/test_models.py`
- [ ] Create `accounts/test_views.py`
- [ ] Create `investments/test_models.py`
- [ ] Create `investments/test_views.py`
- [ ] Create `kyc/test_views.py`
- [ ] Run: `python manage.py test`

### 15. Add Docstrings
- [ ] **File:** `investments/views.py`
  - [ ] Add docstring to `_bybit_get_deposit_address()`
  - [ ] Add docstring to all view functions
- [ ] **File:** `tasks/tasks.py`
  - [ ] Add docstrings to all Celery tasks
- [ ] **File:** `notifications/email_service.py`
  - [ ] Add docstrings to all email functions

### 16. Performance Optimization
- [ ] Add pagination to activity logs
- [ ] Add caching to user dashboard
- [ ] Optimize N+1 queries with `select_related()`
- [ ] Add query counting in DEBUG mode

---

## ✅ VERIFICATION STEPS

After completing each fix:

1. **Run Linter:**
```bash
flake8 .
pylint accounts investments dashboard kyc
```

2. **Run Tests:**
```bash
python manage.py test
```

3. **Check Migrations:**
```bash
python manage.py makemigrations --dry-run
python manage.py migrate --plan
```

4. **Manual Testing:**
- [ ] Test signup with referral code
- [ ] Test deposit creation
- [ ] Test withdrawal request
- [ ] Test admin panel actions
- [ ] Test coupon application
- [ ] Test KYC upload

5. **Security Check:**
```bash
python manage.py check --deploy
```

---

## 📊 PROGRESS TRACKER

| Category | Total | Done | Remaining |
|----------|-------|------|-----------|
| Critical | 5 | 0 | 5 |
| High Priority | 9 | 0 | 9 |
| Medium Priority | 7 | 0 | 7 |
| Low Priority | 3 | 0 | 3 |
| **TOTAL** | **24** | **0** | **24** |

---

## 🎯 QUICK WINS (Can Do Today)

These are simple find-and-replace fixes:

1. ✅ Fix withdrawal email bug (5 minutes)
2. ✅ Add CSRF token (2 minutes)
3. ✅ Fix SECRET_KEY check (5 minutes)
4. ✅ Add file error handling (10 minutes)
5. ✅ Update .env.example (5 minutes)

**Total Time:** ~30 minutes for 5 critical fixes!

---

## 📞 NEED HELP?

**Common Issues:**

**Q: "How do I test the withdrawal email fix?"**
A: Create a test withdrawal in Django admin, change status to 'approved', check email

**Q: "Where do I create the core/ directory?"**
A: At project root, same level as accounts/, investments/, etc.

**Q: "How do I implement admin approval views?"**
A: Look at existing views in `investments/views.py` for patterns, copy structure

**Q: "Tests are failing after adding validators"**
A: Run migrations first: `python manage.py migrate`

