import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Cho phép truy cập từ bên ngoài
    port: 3000,
    hmr: {
      clientPort: 3000
    },
    allowedHosts: 'all', // Cho phép tất cả hosts (bao gồm ngrok)
    proxy: {
      '/api': {
        //target: 'http://localhost:80', // Port 80 - chỉ định rõ ràng
        target: 'http://localhost:8000', // Port 8000 - khớp với CHAY_SERVER.bat
        changeOrigin: true,
        secure: false
      }
    }
  }
})

