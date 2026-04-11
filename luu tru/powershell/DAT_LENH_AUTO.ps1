# Script PowerShell tự động đặt lệnh
# Tự động login, lấy token và đặt lệnh

$BASE_URL = "http://127.0.0.1:8000"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dat lenh truc tiep len Binance" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Login
Write-Host "Buoc 1: Dang nhap..." -ForegroundColor Yellow
$username = Read-Host "Username"
$password = Read-Host "Password" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login?username=$username&password=$plainPassword" -Method Post
    $token = $loginResponse.access_token
    Write-Host "[OK] Dang nhap thanh cong!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Dang nhap that bai: $_" -ForegroundColor Red
    exit 1
}

# List configs
Write-Host "`nBuoc 2: Lay danh sach configs..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $configs = Invoke-RestMethod -Uri "$BASE_URL/api/config/" -Method Get -Headers $headers
    Write-Host "[OK] Tim thay $($configs.Count) config(s)" -ForegroundColor Green
    
    for ($i = 0; $i -lt $configs.Count; $i++) {
        $hasApi = if ($configs[$i].api_key_encrypted) { "[Co API]" } else { "[Chua co API]" }
        Write-Host "  $($i+1). $hasApi ID=$($configs[$i].id) - $($configs[$i].name) - $($configs[$i].symbol)"
    }
    
    $choice = Read-Host "`nChon config (so)"
    $selectedConfig = $configs[[int]$choice - 1]
    Write-Host "[OK] Da chon: $($selectedConfig.name) (ID: $($selectedConfig.id))" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Loi: $_" -ForegroundColor Red
    exit 1
}

# Place order
Write-Host "`nBuoc 3: Dat lenh..." -ForegroundColor Yellow
Write-Host "[WARN] Day la lenh THAT tren Binance!" -ForegroundColor Red

$side = Read-Host "Side (buy/sell) [buy]"
if ([string]::IsNullOrEmpty($side)) { $side = "buy" }

$orderType = Read-Host "Order type (market/limit) [market]"
if ([string]::IsNullOrEmpty($orderType)) { $orderType = "market" }

$amount = $null
$price = $null

$amountInput = Read-Host "Amount (Enter de dung amount tu config)"
if (-not [string]::IsNullOrEmpty($amountInput)) {
    $amount = [double]$amountInput
}

if ($orderType -eq "limit") {
    $priceInput = Read-Host "Price"
    if (-not [string]::IsNullOrEmpty($priceInput)) {
        $price = [double]$priceInput
    }
}

$body = @{
    bot_config_id = $selectedConfig.id
    side = $side
    order_type = $orderType
}

if ($amount) { $body.amount = $amount }
if ($price) { $body.price = $price }

$jsonBody = $body | ConvertTo-Json

Write-Host "`nPayload:" -ForegroundColor Yellow
Write-Host $jsonBody

$confirm = Read-Host "`n[WARN] Xac nhan dat lenh THAT? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Da huy." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nDang dat lenh..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/trading/place-order" -Method Post -Headers $headers -Body $jsonBody -ContentType "application/json"
    
    Write-Host "`n[OK] Dat lenh thanh cong!" -ForegroundColor Green
    Write-Host "Order ID: $($response.order_id)" -ForegroundColor White
    Write-Host "Exchange Order ID: $($response.exchange_order_id)" -ForegroundColor White
    Write-Host "Price: $($response.filled_price)" -ForegroundColor White
    Write-Host "Stop Loss: $($response.stop_loss)" -ForegroundColor White
    Write-Host "Take Profit: $($response.take_profit)" -ForegroundColor White
    
} catch {
    Write-Host "`n[ERROR] Dat lenh that bai!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan

