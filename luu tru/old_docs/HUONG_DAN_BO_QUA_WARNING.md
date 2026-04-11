# Hướng Dẫn Bỏ Qua Ngrok Warning Page

## ⚠️ Warning Page

Ngrok free plan hiển thị warning page khi truy cập. Đây là bình thường!

## ✅ Cách Bỏ Qua (Đơn Giản)

### Cách 1: Click "Visit Site"

1. Trên warning page, click nút **"Visit Site"**
2. Trang sẽ vào frontend của bạn
3. **Lưu ý**: Mỗi người chỉ thấy warning 1 lần

### Cách 2: Dùng Extension (Cho Developer)

#### Cài ModHeader Extension

1. **Chrome/Edge**: 
   - Truy cập: https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj
   - Click "Add to Chrome"

2. **Cấu hình**:
   - Click icon ModHeader trên toolbar
   - Click "Add header"
   - **Name**: `ngrok-skip-browser-warning`
   - **Value**: `true`
   - Click "Save"

3. **Sử dụng**:
   - Bật ModHeader (toggle ON)
   - Truy cập ngrok URL → Không còn warning!

---

## 🔧 Cho API Requests

API requests tự động bỏ qua warning, không cần làm gì.

Nếu muốn chắc chắn, thêm header:

```bash
curl -H "ngrok-skip-browser-warning: true" https://b138a66a2bed.ngrok-free.app/api/health
```

---

## 📝 URL Hiện Tại

**HTTPS**: `https://b138a66a2bed.ngrok-free.app`

**Lưu ý**: URL này sẽ thay đổi mỗi lần restart ngrok (free plan)

---

## 💡 Tips

1. **Lần đầu**: Click "Visit Site" → Vào được ngay
2. **Lần sau**: Không còn warning nữa
3. **Chia sẻ**: Người khác cũng chỉ thấy warning 1 lần
4. **API**: Tự động bỏ qua, không cần header

---

## 🚀 Upgrade Paid Plan

Nếu muốn loại bỏ hoàn toàn warning page:
- Upgrade tại: https://dashboard.ngrok.com/billing/choose-a-plan
- Có thêm: URL tĩnh, nhiều sessions, không giới hạn

---

## ✅ Kết Luận

**Cách đơn giản nhất**: Click nút **"Visit Site"** trên warning page!

Sau đó bạn có thể truy cập frontend bình thường tại:
`https://b138a66a2bed.ngrok-free.app`

