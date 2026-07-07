import pyotp
import qrcode
import io
import base64
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.http import JsonResponse
from apps.beneficiaries.models import Beneficiary
from apps.donors.models import Donor
from apps.donations.models import Donation
from apps.sponsorships.models import Sponsorship
from apps.projects.models import Project
from apps.finance.models import FinancialEntry
from apps.cases.models import Case
from apps.inventory.models import InventoryItem
from apps.occasions.models import Occasion


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = []
        if not username:
            errors.append('اسم المستخدم مطلوب')
        elif get_user_model().objects.filter(username=username).exists():
            errors.append('اسم المستخدم موجود بالفعل')

        if not password:
            errors.append('كلمة المرور مطلوبة')
        elif len(password) < 8:
            errors.append('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        elif not any(c.isupper() for c in password):
            errors.append('كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل')
        elif not any(c.islower() for c in password):
            errors.append('كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل')
        elif not any(c.isdigit() for c in password):
            errors.append('كلمة المرور يجب أن تحتوي على رقم واحد على الأقل')
        elif not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append('كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل')
        elif password != password_confirm:
            errors.append('تأكيد كلمة المرور غير متطابق')

        if not errors:
            user = get_user_model().objects.create_user(
                username=username,
                password=password,
            )
            login(request, user)
            messages.success(request, f'مرحباً {user.full_name}، تم إنشاء الحساب بنجاح')
            return redirect('dashboard')

        return render(request, 'registration/register.html', {'errors': errors})
    return render(request, 'registration/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        otp_token = request.POST.get('otp_token', '')
        remember = request.POST.get('remember')

        # Check if this is an OTP step (previously authenticated, now providing OTP)
        pre_auth_user_id = request.session.get('pre_auth_user_id')
        if pre_auth_user_id:
            try:
                user = get_user_model().objects.get(id=pre_auth_user_id, is_active=True)
            except get_user_model().DoesNotExist:
                del request.session['pre_auth_user_id']
                return render(request, 'registration/login.html', {'error': 'انتهت صلاحية الجلسة، يرجى تسجيل الدخول مرة أخرى'})
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(otp_token, valid_window=1):
                return render(request, 'registration/login.html', {
                    'two_factor_required': True,
                    'username': user.username,
                    'error': 'رمز التحقق غير صحيح',
                })
            login(request, user)
            del request.session['pre_auth_user_id']
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'مرحباً {user.full_name}')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')

        # First step: password authentication
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.otp_enabled:
                request.session['pre_auth_user_id'] = str(user.id)
                return render(request, 'registration/login.html', {
                    'two_factor_required': True,
                    'username': username,
                    'error': 'يرجى إدخال رمز التحقق',
                })
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'مرحباً {user.full_name}')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            return render(request, 'registration/login.html', {'error': 'بيانات الدخول غير صحيحة'})
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        if request.POST.get('profile_2fa_enabled') == 'on' and not user.otp_enabled:
            user.otp_enabled = True
            user.otp_secret = pyotp.random_base32()
        elif not request.POST.get('profile_2fa_enabled') and user.otp_enabled:
            user.otp_enabled = False
            user.otp_secret = ''
        user.save()
        messages.success(request, 'تم تحديث الملف الشخصي')
        return redirect('profile')
    qr_uri = ''
    if user.otp_enabled and user.otp_secret:
        totp = pyotp.TOTP(user.otp_secret)
        qr_uri = totp.provisioning_uri(user.email or user.username, issuer_name="الماجد")
    return render(request, 'registration/profile.html', {'qr_uri': qr_uri})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def dashboard_view(request):
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_beneficiaries = Beneficiary.objects.filter(is_active=True).count()
    registered = Donor.objects.filter(is_active=True).count()
    donation_donors = Donation.objects.filter(
        Q(donor__isnull=False) | (~Q(donor_name__isnull=True) & ~Q(donor_name__exact=''))
    ).count()
    total_donors = registered + donation_donors
    if total_donors == 0:
        total_donors = Donation.objects.count()
    elif total_donors < Donation.objects.count():
        total_donors = Donation.objects.count()
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    month_donations = Donation.objects.filter(created_at__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
    active_sponsorships = Sponsorship.objects.filter(is_active=True).count()
    active_projects = Project.objects.filter(is_active=True, status='in_progress').count()
    pending_cases = Case.objects.exclude(status__in=['closed', 'rejected']).count()
    urgent_cases = Case.objects.filter(case_type='emergency').exclude(status__in=['closed', 'rejected']).count()
    total_expense = FinancialEntry.objects.filter(entry_type='expense', is_approved=True).aggregate(total=Sum('amount'))['total'] or 0
    low_stock_items = InventoryItem.objects.filter(is_active=True).count()
    active_occasions = Occasion.objects.filter(status='active').count()

    latest_donations = Donation.objects.select_related('donor').order_by('-created_at')[:10]
    latest_cases = Case.objects.select_related('beneficiary').order_by('-created_at')[:10]

    current_year = today.year
    months_data = []
    for i in range(6):
        m = today.month - i
        y = current_year
        if m <= 0:
            m += 12
            y -= 1
        month_total = Donation.objects.filter(created_at__year=y, created_at__month=m).aggregate(total=Sum('amount'))['total'] or 0
        months_data.insert(0, {'month': f'{m:02d}/{y}', 'total': float(month_total)})

    cases_by_type = []
    for key, label in Case.CASE_TYPES:
        count = Case.objects.filter(case_type=key).exclude(status__in=['cancelled', 'closed']).count()
        if count > 0:
            cases_by_type.append({'type': label, 'count': count})

    donations_by_type = []
    for key, label in Donation.TRANSACTION_TYPES:
        total = Donation.objects.filter(transaction_type=key).aggregate(total=Sum('amount'))['total'] or 0
        if total:
            donations_by_type.append({'type': label, 'total': float(total)})

    context = {
        'total_beneficiaries': total_beneficiaries,
        'total_donors': total_donors,
        'total_donations': total_donations,
        'month_donations': month_donations,
        'active_sponsorships': active_sponsorships,
        'active_projects': active_projects,
        'urgent_cases': urgent_cases,
        'pending_cases': pending_cases,
        'total_expense': total_expense,
        'low_stock_items': low_stock_items,
        'active_occasions': active_occasions,
        'latest_donations': latest_donations,
        'latest_cases': latest_cases,
        'months_data': months_data,
        'cases_by_type': cases_by_type,
        'donations_by_type': donations_by_type,
    }
    return render(request, 'dashboard.html', context)


@login_required
def api_dashboard_stats(request):
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_beneficiaries = Beneficiary.objects.filter(is_active=True).count()
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    month_donations = Donation.objects.filter(created_at__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = FinancialEntry.objects.filter(entry_type='expense', is_approved=True).aggregate(total=Sum('amount'))['total'] or 0
    active_sponsorships = Sponsorship.objects.filter(is_active=True).count()
    active_projects = Project.objects.filter(is_active=True, status='in_progress').count()
    return JsonResponse({
        'total_beneficiaries': total_beneficiaries,
        'total_donations': float(total_donations),
        'month_donations': float(month_donations),
        'total_expense': float(total_expense),
        'active_sponsorships': active_sponsorships,
        'active_projects': active_projects,
    })
