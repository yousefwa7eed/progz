from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.accounts.models import Role, User
from apps.finance.models import Account


class Command(BaseCommand):
    help = 'Initialize system with roles, accounts, and superuser'

    def handle(self, *args, **options):
        roles_data = [
            ('مدير النظام', 'system_admin', 'التحكم الكامل في النظام', 1),
            ('المدير التنفيذي', 'executive_director', 'الإشراف العام', 2),
            ('مدير مالي', 'finance_manager', 'إدارة المالية والميزانية', 3),
            ('مسؤول برامج', 'program_officer', 'إدارة المشاريع والحالات', 4),
            ('مسؤول مستفيدين', 'beneficiary_officer', 'إدارة المستفيدين', 5),
            ('مسؤول مخزون', 'inventory_officer', 'إدارة المخزون', 6),
            ('محاسب', 'accountant', 'تسجيل القيود والحسابات', 7),
            ('موظف استقبال', 'receptionist', 'تسجيل المتبرعين والمستفيدين', 8),
            ('متطوع', 'volunteer', 'صلاحيات محدودة', 9),
        ]
        created_roles = {}
        for name, code, desc, priority in roles_data:
            role, created = Role.objects.get_or_create(code=code, defaults={
                'name': name, 'description': desc, 'priority': priority, 'is_system': True,
            })
            created_roles[code] = role
            self.stdout.write(f'  {"+ " if created else "  "}Role: {name}')

        accounts_data = [
            ('3100', 'صندوق عام', 'main', 'income', 0),
            ('3200', 'صندوق الزكاة', 'main', 'income', 0),
            ('3300', 'صندوق الصدقات', 'main', 'income', 0),
            ('3400', 'صندوق الأوقاف', 'main', 'income', 0),
            ('3500', 'حسابات بنكية', 'main', 'asset', 0),
            ('4100', 'مصروفات المساعدات', 'main', 'expense', 0),
            ('4200', 'مصروفات إدارية', 'main', 'expense', 0),
            ('4300', 'مصروفات المشاريع', 'main', 'expense', 0),
            ('5100', 'أصول ثابتة', 'main', 'asset', 0),
            ('6100', 'ذمم مدينة', 'main', 'asset', 0),
        ]
        for code, name, atype, group, balance in accounts_data:
            acc, created = Account.objects.get_or_create(code=code, defaults={
                'name': name, 'account_type': atype, 'account_group': group,
                'opening_balance': balance, 'current_balance': balance, 'is_active': True,
            })
            self.stdout.write(f'  {"+ " if created else "  "}Account: {code} - {name}')

        sub_accounts = [
            ('3110', 'تبرعات نقدية', '3100', 'sub'),
            ('3120', 'تبرعات عينية', '3100', 'sub'),
            ('4110', 'مساعدات مباشرة', '4100', 'sub'),
            ('4120', 'كفالات أيتام', '4100', 'sub'),
            ('4210', 'رواتب', '4200', 'sub'),
            ('4220', 'إيجارات', '4200', 'sub'),
            ('4230', 'فواتير', '4200', 'sub'),
            ('4310', 'مشاريع موسمية', '4300', 'sub'),
            ('4320', 'مشاريع تنموية', '4300', 'sub'),
            ('5110', 'أثاث ومعدات', '5100', 'sub'),
        ]
        for code, name, parent_code, atype in sub_accounts:
            try:
                parent = Account.objects.get(code=parent_code)
                acc, created = Account.objects.get_or_create(code=code, defaults={
                    'name': name, 'account_type': atype, 'account_group': parent.account_group,
                    'parent': parent, 'opening_balance': 0, 'current_balance': 0, 'is_active': True,
                })
                self.stdout.write(f'  {"+ " if created else "  "}Sub-Account: {code} - {name}')
            except Account.DoesNotExist:
                self.stdout.write(f'  ! Parent account {parent_code} not found for {code}')

        admin_role = created_roles.get('system_admin')
        if not User.objects.filter(username='admin').exists():
            User.objects.create(
                username='admin',
                email='admin@almajid.sa',
                full_name='مدير النظام',
                phone='0500000000',
                role=admin_role,
                is_superuser=True,
                is_staff=True,
                is_active=True,
                password=make_password('admin123'),
            )
            self.stdout.write('  + Superuser: admin / admin123')
        else:
            self.stdout.write('    Superuser already exists')

        self.stdout.write(self.style.SUCCESS('System initialization complete'))
