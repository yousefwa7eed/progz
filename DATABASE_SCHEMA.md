# تصميم قاعدة البيانات - نظام الماجد
## Almajid Database Schema

---

## المبادئ العامة
- **الترقيم**: UUID لكل جدول (للتوزع المستقبلي)
- **التدقيق**: كل جدول يحتوي على `created_at`, `updated_at`, `created_by`, `updated_by`
- **الحذف المنطقي**: `is_active`, `is_deleted`, `deleted_at` بدلاً من الحذف الفعلي
- **التدقيق الشرعي**: كل معاملة مالية تحمل `transaction_type` (زكاة/صدقة/كفالة/عام)
- **الترقيم التلقائي**: رقم تسلسلي لكل كيان رئيسي
- **الحقول المُضافة**: `notes`, `attachments` قابلة للتوسع

---

## 1. جدول: User (مستخدم النظام)
**ملف: accounts/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| username | VARCHAR(150) | اسم المستخدم |
| email | EmailField | البريد الإلكتروني |
| password | Hash | كلمة المرور (مشفرة) |
| full_name | VARCHAR(255) | الاسم الكامل |
| phone | VARCHAR(20) | رقم الجوال |
| national_id | VARCHAR(20) | رقم الهوية (مشفّر) |
| branch | FK → Branch | الفرع التابع له |
| role | FK → Role | الدور الوظيفي |
| is_active | Boolean | نشط |
| is_deleted | Boolean | محذوف منطقياً |
| last_login | DateTime | آخر دخول |
| created_at | DateTime | تاريخ الإنشاء |
| updated_at | DateTime | آخر تحديث |
| created_by | FK → User | منشأ بواسطة |
| otp_secret | VARCHAR(32) | سر 2FA (مشفّر) |
| otp_enabled | Boolean | تفعيل 2FA |

### علاقات إضافية:
- User M2M → Permission (صلاحيات إضافية)
- User M2M → Branch (إذا كان مسؤول عن أكثر من فرع)

---

## 2. جدول: Role (الدور الوظيفي)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| name | VARCHAR(100) | اسم الدور |
| code | VARCHAR(50) | كود الدور (unique) |
| description | Text | وصف الدور |
| priority | Integer | أولوية الدور (للترتيب) |
| is_system | Boolean | دور نظامي (لا يمكن حذفه) |

---

## 3. جدول: Permission (الصلاحية)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| name | VARCHAR(255) | اسم الصلاحية |
| codename | VARCHAR(100) | كود الصلاحية (unique) |
| module | VARCHAR(50) | الوحدة (accounts, finance, etc) |
| description | Text | وصف |

### علاقات:
- Permission M2M → Role (صلاحيات الدور)
- Permission M2M → User (صلاحيات إضافية للمستخدم)

---

## 4. جدول: Branch (الفرع)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| code | VARCHAR(20) | كود الفرع (unique) |
| name | VARCHAR(255) | اسم الفرع |
| address | Text | العنوان |
| city | VARCHAR(100) | المدينة |
| phone | VARCHAR(20) | الهاتف |
| email | EmailField | البريد |
| is_active | Boolean | نشط |
| created_at | DateTime | تاريخ الإنشاء |

---

## 5. جدول: Beneficiary (المستفيد)
**ملف: beneficiaries/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| code | VARCHAR(20) | رقم المستفيد (تسلسلي) |
| full_name | VARCHAR(255) | الاسم الكامل |
| gender | CharField(1) | الجنس (M/F) |
| national_id | VARCHAR(20) | رقم الهوية (مشفّر) |
| birth_date | Date | تاريخ الميلاد |
| phone | VARCHAR(20) | رقم الجوال |
| phone2 | VARCHAR(20) | جوال آخر |
| address | Text | العنوان |
| city | VARCHAR(100) | المدينة |
| district | VARCHAR(100) | الحي |
| marital_status | CharField | الحالة الاجتماعية |
| family_members | Integer | عدد أفراد الأسرة |
| has_orphans | Boolean | يوجد أيتام بالأسرة |
| orphans_count | Integer | عدد الأيتام |
| health_status | Text | الحالة الصحية |
| has_chronic_disease | Boolean | أمراض مزمنة |
| chronic_diseases | Text | تفاصيل الأمراض |
| has_disabilities | Boolean | إعاقات |
| disabilities_details | Text | تفاصيل الإعاقات |
| employment_status | CharField | الوضع الوظيفي |
| monthly_income | Decimal | الدخل الشهري |
| housing_type | CharField | نوع السكن |
| is_urgent | Boolean | حالة عاجلة |
| priority_score | Integer | درجة الأولوية (حسبة) |
| notes | Text | ملاحظات |
| attachments | JSON | قائمة المرفقات |
| status | CharField | الحالة (نشط/موقوف/مغلق) |
| is_active | Boolean | نشط |
| created_at | DateTime | تاريخ التسجيل |
| updated_at | DateTime | آخر تحديث |

### علاقات:
- Beneficiary M2M → Case (الحالات المرتبطة)
- Beneficiary M2M → Sponsorship (الكفالات)
- Beneficiary M2M → Document (المستندات)

---

## 6. جدول: Donor (المتبرع)
**ملف: donors/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| code | VARCHAR(20) | رقم المتبرع (تسلسلي) |
| full_name | VARCHAR(255) | الاسم الكامل |
| donor_type | CharField | فرد / شركة / مؤسسة |
| phone | VARCHAR(20) | جوال |
| email | EmailField | بريد |
| address | Text | عنوان |
| city | VARCHAR(100) | مدينة |
| national_id | VARCHAR(20) | هوية (للأفراد) |
| commercial_reg | VARCHAR(50) | سجل تجاري (للشركات) |
| contact_person | VARCHAR(255) | شخص للتواصل (للشركات) |
| preferred_contact | CharField | طريقة التواصل المفضلة |
| preferred_donation | CharField | نوع التبرع المفضل |
| is_anonymous | Boolean | متبرع مجهول |
| is_committed | Boolean | متبرع منتظم |
| total_donations | Decimal | إجمالي التبرعات (حسبة) |
| last_donation_date | Date | تاريخ آخر تبرع |
| donor_category | FK → DonorCategory | تصنيف المتبرع |
| notes | Text | ملاحظات |
| is_active | Boolean | نشط |
| created_at | DateTime | تاريخ التسجيل |

### علاقات:
- Donor M2M → Donation (التبرعات)
- Donor M2M → Sponsorship (الكفالات)

---

## 7. جدول: DonorCategory (تصنيف المتبرعين)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| name | VARCHAR(100) | اسم التصنيف |
| description | Text | وصف |
| priority | Integer | أولوية التواصل |

---

## 8. جدول: Donation (التبرع)
**ملف: donations/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف فريد |
| code | VARCHAR(20) | رقم التبرع (تسلسلي) |
| donor | FK → Donor | المتبرع |
| donation_type | CharField | نقدي / عيني / إلكتروني |
| payment_method | CharField | نقداً / تحويل / بطاقة / محفظة |
| amount | Decimal | المبلغ (للنقدي) |
| currency | VARCHAR(3) | العملة (SAR) |
| items | JSON | الأصناف (للعيني) |
| transaction_type | CharField | زكاة / صدقة / كفالة / مشروع / عام |
| campaign | CharField | حملة (إن وجدت) |
| project | FK → Project | مشروع (إن وجد) |
| branch | FK → Branch | الفرع المستلم |
| received_by | FK → User | المستلم |
| receipt_number | VARCHAR(50) | رقم الإيصال |
| receipt_date | Date | تاريخ الإيصال |
| is_anonymous | Boolean | تبرع مجهول |
| is_zakat | Boolean | زكاة |
| zakat_year | Integer | سنة الزكاة |
| notes | Text | ملاحظات |
| attachments | JSON | المرفقات |
| status | CharField | مسجل / مؤكد / ملغي |
| created_at | DateTime | تاريخ التسجيل |

### علاقات:
- Donation M2M → InventoryItem (للتبرعات العينية)

---

## 9. جدول: Sponsorship (الكفالة)
**ملف: sponsorships/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | رقم الكفالة |
| sponsor | FK → Donor | الكفيل |
| beneficiary | FK → Beneficiary | المستفيد (لليتيم/الطالب/المريض) |
| family_beneficiary | FK → Beneficiary | المستفيد الرئيسي (للأسرة) |
| sponsorship_type | CharField | يتيم / أسرة / مريض / طالب |
| monthly_amount | Decimal | المبلغ الشهري |
| start_date | Date | تاريخ البدء |
| end_date | Date | تاريخ الانتهاء |
| duration_months | Integer | المدة بالأشهر |
| payment_method | CharField | طريقة الدفع |
| payment_day | Integer | يوم الدفع الشهري |
| is_active | Boolean | سارية |
| status | CharField | نشطة / متوقفة / منتهية |
| last_payment_date | Date | آخر صرف |
| next_payment_date | Date | تاريخ الصرف القادم |
| total_paid | Decimal | إجمالي المدفوع |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ الإنشاء |

### علاقات:
- Sponsorship M2M → SponsorshipPayment (دفعات الكفالة)

---

## 10. جدول: SponsorshipPayment (دفعة كفالة)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| sponsorship | FK → Sponsorship | الكفالة |
| amount | Decimal | المبلغ |
| payment_date | Date | تاريخ الدفع |
| month | Integer | الشهر |
| year | Integer | السنة |
| is_donor_paid | Boolean | دفع الكفيل |
| is_beneficiary_received | Boolean | استلم المستفيد |
| receipt_number | VARCHAR(50) | رقم إيصال الصرف |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ الإنشاء |

---

## 11. جدول: Case (الحالة)
**ملف: cases/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | رقم الحالة |
| beneficiary | FK → Beneficiary | المستفيد |
| case_type | CharField | نوع المساعدة (نقدي/عيني/علاج/....) |
| priority | CharField | عاجلة / عالية / متوسطة / منخفضة |
| description | Text | وصف الحالة |
| requested_amount | Decimal | المبلغ المطلوب |
| approved_amount | Decimal | المبلغ المعتمد |
| status | CharField | جديد / دراسة / معتمد / صرف / مغلق |
| assigned_to | FK → User | الباحث الاجتماعي |
| reviewed_by | FK → User | المراجع |
| approved_by | FK → User | المعتمد |
| reviewed_at | DateTime | تاريخ المراجعة |
| approved_at | DateTime | تاريخ الاعتماد |
| closed_at | DateTime | تاريخ الإغلاق |
| close_reason | Text | سبب الإغلاق |
| needs_reassessment | Boolean | يحتاج إعادة تقييم |
| reassessment_date | Date | تاريخ إعادة التقييم |
| attachments | JSON | المرفقات |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ الإنشاء |
| updated_at | DateTime | آخر تحديث |

---

## 12. جدول: CaseActivity (نشاط الحالة)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| case | FK → Case | الحالة |
| activity_type | CharField | نوع النشاط |
| description | Text | وصف النشاط |
| performed_by | FK → User | منفذ النشاط |
| old_status | CharField | الحالة القديمة |
| new_status | CharField | الحالة الجديدة |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ النشاط |

---

## 13. جدول: Project (المشروع الخيري)
**ملف: projects/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | رقم المشروع |
| name | VARCHAR(255) | اسم المشروع |
| project_type | CharField | غذاء / كسوة / مياه / علاج / ترميم / تعليم / موسمي |
| description | Text | وصف المشروع |
| goal_amount | Decimal | الهدف المالي |
| total_budget | Decimal | إجمالي الميزانية |
| start_date | Date | تاريخ البداية |
| end_date | Date | تاريخ النهاية |
| status | CharField | تخطيط / اعتماد / تنفيذ / منتهي / ملغي |
| manager | FK → User | مدير المشروع |
| approved_by | FK → User | المعتمد |
| beneficiaries_count | Integer | عدد المستفيدين |
| locations | Text | مواقع التنفيذ |
| notes | Text | ملاحظات |
| attachments | JSON | مرفقات |
| is_active | Boolean | نشط |
| created_at | DateTime | تاريخ الإنشاء |

### علاقات:
- Project M2M → Donation (التبرعات المخصصة)
- Project M2M → Expense (مصروفات المشروع)

---

## 14. جدول: ProjectPhase (مرحلة المشروع)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| project | FK → Project | المشروع |
| name | VARCHAR(255) | اسم المرحلة |
| description | Text | وصف |
| start_date | Date | تاريخ البداية |
| end_date | Date | تاريخ النهاية |
| budget | Decimal | ميزانية المرحلة |
| spent | Decimal | المنصرف |
| status | CharField | pending / in_progress / completed |
| notes | Text | ملاحظات |

---

## 15. جدول: FinancialEntry (قيد مالي)
**ملف: finance/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | رقم القيد |
| entry_type | CharField | إيراد / مصروف / تحويل |
| entry_date | Date | تاريخ القيد |
| amount | Decimal | المبلغ |
| currency | VARCHAR(3) | العملة |
| description | Text | بيان القيد |
| account | FK → Account | الحساب |
| donor | FK → Donor | متبرع (للإيرادات) |
| donation | FK → Donation | تبرع (للإيرادات) |
| expense_category | FK → ExpenseCategory | تصنيف المصروف |
| project | FK → Project | مشروع (إن وجد) |
| case | FK → Case | حالة (إن وجد) |
| payment_method | CharField | طريقة الدفع |
| bank_account | FK → BankAccount | حساب بنكي |
| reference_number | VARCHAR(100) | رقم مرجعي |
| receipt_number | VARCHAR(50) | رقم إيصال |
| approved_by | FK → User | المعتمد |
| recorded_by | FK → User | المسجل |
| transaction_type | CharField | زكاة / صدقة / عام |
| is_reconciled | Boolean | تمت التسوية |
| notes | Text | ملاحظات |
| attachments | JSON | مرفقات |
| created_at | DateTime | تاريخ التسجيل |

---

## 16. جدول: Account (الحساب المالي)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | كود الحساب (دليل حسابات موحد) |
| name | VARCHAR(255) | اسم الحساب |
| account_type | CharField | رئيسي / فرعي |
| parent | FK → Account | الحساب الأب (للهيكل الشجري) |
| account_group | CharField | أصول / خصوم / إيرادات / مصروفات |
| opening_balance | Decimal | الرصيد الافتتاحي |
| current_balance | Decimal | الرصيد الحالي (حسبة) |
| is_active | Boolean | نشط |
| notes | Text | ملاحظات |

### هيكل دليل الحسابات المبسط:
```
1000 - الأصول
  1100 - الصندوق
  1200 - البنوك
  1300 - المخزون
2000 - الخصوم
  2100 - دائنون
3000 - الإيرادات
  3100 - تبرعات عامة
  3200 - زكاة
  3300 - صدقات
  3400 - كفالات
  3500 - أوقاف
4000 - المصروفات
  4100 - مساعدات مباشرة
  4200 - مشاريع
  4300 - رواتب
  4400 - مصروفات تشغيل
  4500 - مصروفات إدارية
```

---

## 17. جدول: BankAccount (حساب بنكي)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| bank_name | VARCHAR(255) | اسم البنك |
| account_name | VARCHAR(255) | اسم الحساب |
| account_number | VARCHAR(50) | رقم الحساب |
| iban | VARCHAR(34) | IBAN |
| account_type | CharField | جاري / استثماري |
| current_balance | Decimal | الرصيد الحالي |
| is_active | Boolean | نشط |

---

## 18. جدول: ExpenseCategory (تصنيف المصروفات)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| name | VARCHAR(255) | اسم التصنيف |
| code | VARCHAR(20) | كود التصنيف |
| parent | FK → ExpenseCategory | تصنيف أب |
| is_active | Boolean | نشط |

---

## 19. جدول: InventoryItem (صنف مخزني)
**ملف: inventory/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | كود الصنف |
| name | VARCHAR(255) | اسم الصنف |
| category | FK → InventoryCategory | التصنيف |
| unit | CharField | وحدة القياس (كيلو / حبة / عبوة) |
| quantity | Decimal | الكمية الحالية |
| min_quantity | Decimal | الحد الأدنى |
| max_quantity | Decimal | الحد الأقصى |
| unit_price | Decimal | سعر الوحدة |
| expiry_date | Date | تاريخ انتهاء الصلاحية |
| location | VARCHAR(255) | موقع التخزين |
| notes | Text | ملاحظات |
| is_active | Boolean | نشط |

---

## 20. جدول: InventoryCategory (تصنيف المخزون)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| name | VARCHAR(255) | اسم التصنيف |
| parent | FK → InventoryCategory | تصنيف أب |
| description | Text | وصف |

### التصنيفات المقترحة:
```
مواد غذائية
  - أرز
  - سكر
  - زيت
  - تمر
  - معلبات
ملابس
  - رجال
  - نساء
  - أطفال
أجهزة
  - إلكترونية
  - منزلية
أدوية
  - أدوية
مستلزمات دراسية
  - قرطاسية
  - كتب
  - أجهزة لوحية
مواد تنظيف
  - صابون
  - منظفات
بطانيات وفرش
```

---

## 21. جدول: InventoryTransaction (حركة مخزنية)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| item | FK → InventoryItem | الصنف |
| transaction_type | CharField | استلام / صرف / جرد / مرتجع |
| quantity | Decimal | الكمية |
| unit_price | Decimal | سعر الوحدة |
| total | Decimal | الإجمالي |
| source | CharField | مصدر الاستلام (تبرع / شراء) |
| donation | FK → Donation | تبرع عيني (إن وجد) |
| beneficiary | FK → Beneficiary | مستفيد (للصرف) |
| case | FK → Case | حالة (للصرف) |
| project | FK → Project | مشروع |
| performed_by | FK → User | منفذ الحركة |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ الحركة |

---

## 22. جدول: Employee (الموظف)
**ملف: employees/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| user | FK → User | حساب النظام |
| employee_code | VARCHAR(20) | كود الموظف |
| full_name | VARCHAR(255) | الاسم الكامل |
| employee_type | CharField | موظف / متطوع |
| position | VARCHAR(255) | المسمى الوظيفي |
| department | VARCHAR(255) | القسم |
| branch | FK → Branch | الفرع |
| hire_date | Date | تاريخ التعيين |
| contract_type | CharField | دوام كامل / جزئي / متطوع |
| salary | Decimal | الراتب |
| phone | VARCHAR(20) | جوال |
| email | EmailField | بريد وظيفي |
| emergency_contact | VARCHAR(255) | طوارئ |
| qualifications | Text | المؤهلات |
| skills | Text | المهارات |
| notes | Text | ملاحظات |
| attachments | JSON | مرفقات |
| is_active | Boolean | نشط |

---

## 23. جدول: Attendance (الحضور)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| employee | FK → Employee | الموظف |
| date | Date | التاريخ |
| check_in | Time | وقت الحضور |
| check_out | Time | وقت الانصراف |
| status | CharField | حاضر / غائب / إجازة / مأمورية |
| notes | Text | ملاحظات |

---

## 24. جدول: Task (المهمة)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| title | VARCHAR(255) | عنوان المهمة |
| description | Text | وصف |
| assigned_to | FK → User | المسند إليه |
| assigned_by | FK → User | المسند من |
| priority | CharField | عالية / متوسطة / منخفضة |
| due_date | Date | تاريخ التسليم |
| status | CharField | جديدة / قيد_التنفيذ / منجزة / ملغاة |
| related_to | CharField | نوع العلاقة (case/project/...) |
| related_id | UUID | معرف العنصر المرتبط |
| notes | Text | ملاحظات |
| completed_at | DateTime | تاريخ الإنجاز |

---

## 25. جدول: Communication (المراسلة)
**ملف: communications/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| communication_type | CharField | بريد / SMS / واتساب / مكالمة |
| direction | CharField | وارد / صادر |
| subject | VARCHAR(255) | الموضوع |
| content | Text | المحتوى |
| sender | FK → User | المرسل |
| recipient | CharField | المستلم (email/phone) |
| donor | FK → Donor | متبرع (إن وجد) |
| beneficiary | FK → Beneficiary | مستفيد (إن وجد) |
| related_model | CharField | العنصر المرتبط |
| related_id | UUID | معرف العنصر |
| status | CharField | مرسلة / مقروءة / فشلت |
| sent_at | DateTime | تاريخ الإرسال |
| attachments | JSON | مرفقات |

---

## 26. جدول: Document (الوثيقة)
**ملف: documents/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| code | VARCHAR(20) | رقم الوثيقة |
| title | VARCHAR(255) | عنوان الوثيقة |
| document_type | CharField | هوية / تقرير / عقد / إيصال / صورة / ... |
| file | FileField | الملف |
| file_size | Integer | حجم الملف (بايت) |
| file_type | VARCHAR(50) | نوع الملف (pdf, jpg, etc) |
| related_model | CharField | النموذج المرتبط (beneficiary/donor/...) |
| related_id | UUID | معرف العنصر |
| uploaded_by | FK → User | الرافع |
| is_confidential | Boolean | سري |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ الرفع |

---

## 27. جدول: AuditLog (سجل التدقيق)
**ملف: audit/models.py**

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| action | CharField | إنشاء / تعديل / حذف / قراءة / تسجيل_دخول |
| actor | FK → User | المستخدم |
| model_name | VARCHAR(100) | اسم النموذج |
| model_id | UUID | معرف العنصر |
| changes | JSON | التغييرات (old → new) |
| ip_address | GenericIPAddressField | IP المستخدم |
| user_agent | Text | معلومات المتصفح |
| branch | FK → Branch | الفرع |
| timestamp | DateTime | وقت الحدث |

---

## 28. جدول: Notification (الإشعار)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| user | FK → User | المستخدم |
| title | VARCHAR(255) | العنوان |
| message | Text | الرسالة |
| notification_type | CharField | info / warning / success / error |
| is_read | Boolean | مقروء |
| related_model | CharField | النموذج المرتبط |
| related_id | UUID | معرف العنصر |
| created_at | DateTime | تاريخ الإنشاء |

---

## 29. جدول: BackupLog (سجل النسخ الاحتياطي)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| file_name | VARCHAR(255) | اسم ملف النسخة |
| file_size | BigInteger | حجم الملف |
| status | CharField | نجاح / فشل |
| type | CharField | تلقائي / يدوي |
| location | VARCHAR(255) | مسار الحفظ |
| notes | Text | ملاحظات |
| created_at | DateTime | تاريخ الإنشاء |

---

## 30. جدول: SystemSetting (إعدادات النظام)

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | UUID (PK) | معرف |
| key | VARCHAR(100) | المفتاح (unique) |
| value | JSON | القيمة |
| description | Text | وصف |
| is_encrypted | Boolean | مشفرة |
| updated_by | FK → User | آخر من عدّل |

### أمثلة:
- `organization_name`: مؤسسة الماجد
- `currency`: SAR
- `zakat_percentage`: 2.5
- `receipt_prefix`: REC-
- `case_prefix`: CAS-
- `auto_backup_enabled`: true
- `auto_backup_interval`: daily
- `smtp_host`, `smtp_port`, ...

---

## العلاقات الأساسية بين الجداول (ER Diagram - نصي)

```
User ──→ Role (N:1)
User ──→ Branch (N:1)
User ──M2M── Permission
Permission ──M2M── Role

Beneficiary ──→ Case (1:N)
Beneficiary ──→ Sponsorship (1:N)
Beneficiary ──→ InventoryTransaction (1:N)

Donor ──→ Donation (1:N)
Donor ──→ Sponsorship (1:N)
Donor ──→ FinancialEntry (1:N)
Donor ──→ DonorCategory (N:1)

Donation ──→ Project (N:1)
Donation ──→ Branch (N:1)
Donation ──M2M── InventoryItem (M:N)

Sponsorship ──→ SponsorshipPayment (1:N)
Sponsorship ──→ Donor (N:1)
Sponsorship ──→ Beneficiary (N:1)

Case ──→ CaseActivity (1:N)
Case ──→ FinancialEntry (1:N)
Case ──→ InventoryTransaction (1:N)

Project ──→ ProjectPhase (1:N)
Project ──→ FinancialEntry (1:N)

FinancialEntry ──→ Account (N:1)
FinancialEntry ──→ BankAccount (N:1)
FinancialEntry ──→ ExpenseCategory (N:1)

InventoryItem ──→ InventoryCategory (N:1)
InventoryItem ──→ InventoryTransaction (1:N)

Employee ──→ User (1:1)
Employee ──→ Attendance (1:N)
Employee ──→ Task (1:N)

Document ──→ (Polymorphic to any model)
Communication ──→ Donor/Beneficiary (N:1)
AuditLog ──→ User (N:1)
Notification ──→ User (N:1)
```
