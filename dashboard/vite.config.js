import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../app/static',
    emptyOutDir: true,
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]',
        manualChunks: {
          // Split React core libraries
          'react-vendor': ['react', 'react-dom'],
          // Split MUI into its own chunk (large library)
          'mui-vendor': [
            '@mui/material',
            '@mui/icons-material',
            '@mui/x-tree-view',
            '@emotion/react',
            '@emotion/styled'
          ],
          // Split Recharts (charting library)
          'charts-vendor': ['recharts'],
          // Split state management
          'state-vendor': ['zustand']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  base: '/static/'
})
