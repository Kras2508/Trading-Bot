# Bỏ Qua Ngrok Warning Page

## Vấn Đề

Ngrok free plan hiển thị warning page khi truy cập lần đầu. Đây là tính năng bảo mật của ngrok.

## Giải Pháp

### Cách 1: Click "Visit Site" (Đơn Giản Nhất)

1. Click nút **"Visit Site"** trên warning page
2. Trang sẽ tự động bỏ qua warning và vào site
3. **Lưu ý**: Mỗi visitor chỉ thấy warning 1 lần

### Cách 2: Set Header trong Browser (Cho Developer)

#### Chrome/Edge Extension

Cài extension **ModHeader** hoặc **Requestly**:
- **ModHeader**: https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj
- **Requestly**: https://chrome.google.com/webstore/detail/requestly/mdnleldcmiljblolnjhpnblkcekpdkpa

Sau khi cài, thêm header:
- **Header name**: `ngrok-skip-browser-warning`
- **Header value**: `true` (hoặc bất kỳ giá trị nào)

#### Firefox Extension

Cài **Modify Headers**:
- https://addons.mozilla.org/en-US/firefox/addon/modify-headers/

Thêm header tương tự.

### Cách 3: Dùng Custom User-Agent

Thay đổi User-Agent của browser:
- Chrome: F12 → Network conditions → User agent → Custom
- Hoặc dùng extension để set custom User-Agent

### Cách 4: Upgrade Paid Plan (Loại Bỏ Hoàn Toàn)

Upgrade lên paid plan để:
- ✅ Không có warning page
- ✅ URL tĩnh (không đổi)
- ✅ Nhiều sessions cùng lúc
- ✅ Không giới hạn requests

Upgrade tại: https://dashboard.ngrok.com/billing/choose-a-plan

---

## Cho Developer

### Test API với Header

Khi test API, thêm header:

```bash
curl -H "ngrok-skip-browser-warning: true" https://b138a66a2bed.ngrok-free.app/api/health
```

### JavaScript/Fetch

```javascript
fetch('https://b138a66a2bed.ngrok-free.app/api/config/', {
  headers: {
    'ngrok-skip-browser-warning': 'true',
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
```

### Axios

```javascript
axios.get('https://b138a66a2bed.ngrok-free.app/api/config/', {
  headers: {
    'ngrok-skip-browser-warning': 'true',
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
```

---

## Lưu Ý

1. **Warning chỉ hiện 1 lần** cho mỗi visitor
2. **API requests** tự động bỏ qua warning (không cần header)
3. **Browser requests** cần click "Visit Site" hoặc set header
4. **Free plan** luôn có warning page
5. **Paid plan** không có warning page

---

## Khuyến Nghị

- **Cho testing**: Click "Visit Site" là đủ
- **Cho development**: Dùng extension ModHeader
- **Cho production**: Upgrade paid plan

---

## URL Hiện Tại

**HTTPS**: `https://b138a66a2bed.ngrok-free.app`

Sau khi click "Visit Site", bạn có thể truy cập bình thường!

