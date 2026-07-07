param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\projects\ekhlas"

Write-Host "=== بناء تطبيق مؤسسة الماجد ===" -ForegroundColor Green
Write-Host

# Step 1: Run tests
if (-not $SkipTests) {
    Write-Host "[1/4] تشغيل الاختبارات..." -ForegroundColor Cyan
    $testResult = & python manage.py test apps.accounts.tests apps.beneficiaries.tests apps.occasions.tests --verbosity=1 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "فشلت الاختبارات! إلغاء البناء." -ForegroundColor Red
        Write-Host $testResult
        exit 1
    }
    Write-Host "✓ جميع الاختبارات ناجحة" -ForegroundColor Green
} else {
    Write-Host "[1/4] تجاوز الاختبارات" -ForegroundColor Yellow
}

# Step 2: Run migrations and export DB
Write-Host "[2/4] تحديث قاعدة البيانات..." -ForegroundColor Cyan
& python manage.py migrate --verbosity=0 2>&1
& python manage.py collectstatic --noinput --verbosity=0 2>&1
Write-Host "✓ تم تحديث قاعدة البيانات" -ForegroundColor Green

# Step 3: Build with PyInstaller
Write-Host "[3/4] بناء التطبيق (قد يستغرق 4 دقائق)..." -ForegroundColor Cyan
$pyinstallerArgs = @(
    "--onedir", "--windowed", "--noconfirm"
    '--icon="static\images\icon.ico"'
    '--name="AlmajidApp"'
    '--add-data="templates;templates"'
    '--add-data="static;static"'
    '--add-data="media;media"'
    '--add-data="db.sqlite3;."'
    '--add-data="apps\occasions\templates;apps\occasions\templates"'
    '--add-data="static\fonts;static\fonts"'
    '--runtime-hook="rthook_importlib_metadata.py"'
    '--exclude-module=matplotlib'
    '--exclude-module=scipy'
    '--exclude-module=pandas'
    '--exclude-module=notebook'
    '--exclude-module=IPython'
    '--exclude-module=PyQt5'
    '--hidden-import=pyotp'
    '--hidden-import=qrcode'
    '--hidden-import=openpyxl'
    '--hidden-import=fpdf'
    '--hidden-import=arabic_reshaper'
    '--hidden-import=bidi'
    '--hidden-import=apps.utils'
    '--copy-metadata="django-auditlog"'
    "desktop_app.py"
)

& python -m PyInstaller @pyinstallerArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "فشل بناء التطبيق!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ تم بناء التطبيق بنجاح" -ForegroundColor Green

# Step 4: Verify output
Write-Host "[4/4] التحقق من المخرجات..." -ForegroundColor Cyan
$exePath = "D:\projects\ekhlas\dist\AlmajidApp\AlmajidApp.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "✓ التطبيق جاهز: $exePath ({0:N1} MB)" -f $size -ForegroundColor Green
} else {
    Write-Host "خطأ: لم يتم العثور على الملف التنفيذي!" -ForegroundColor Red
    exit 1
}

Write-Host
Write-Host "=== اكتمل البناء بنجاح ===" -ForegroundColor Green
