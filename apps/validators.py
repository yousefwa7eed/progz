from django.core.validators import RegexValidator

egypt_phone = RegexValidator(
    regex=r'^(\+20|0)1[0-9]{9}$',
    message='رقم الموبايل المصري: 01234567890 أو +201234567890'
)

egypt_national_id = RegexValidator(
    regex=r'^[0-9]{14}$',
    message='الرقم القومي يجب أن يتكون من 14 رقمًا'
)

EGYPT_GOVERNORATES = [
    ('', '-- اختر المحافظة --'),
    ('cairo', 'القاهرة'),
    ('alexandria', 'الإسكندرية'),
    ('giza', 'الجيزة'),
    ('sharqia', 'الشرقية'),
    ('dakahlia', 'الدقهلية'),
    ('beheira', 'البحيرة'),
    ('gharbia', 'الغربية'),
    ('monufia', 'المنوفية'),
    ('qalyubia', 'القليوبية'),
    ('damietta', 'دمياط'),
    ('port_said', 'بورسعيد'),
    ('suez', 'السويس'),
    ('ismailia', 'الإسماعيلية'),
    ('kafr_sheikh', 'كفر الشيخ'),
    ('fayoum', 'الفيوم'),
    ('b_sweif', 'بني سويف'),
    ('menya', 'المنيا'),
    ('asyut', 'أسيوط'),
    ('sohag', 'سوهاج'),
    ('qena', 'قنا'),
    ('luxor', 'الأقصر'),
    ('aswan', 'أسوان'),
    ('red_sea', 'البحر الأحمر'),
    ('wadi_gedid', 'الوادي الجديد'),
    ('matrouh', 'مطروح'),
    ('north_sinai', 'شمال سيناء'),
    ('south_sinai', 'جنوب سيناء'),
    ('outside', 'خارج مصر'),
]
