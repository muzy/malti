# Malti Dashboard

A modern React dashboard for visualizing telemetry data from the Malti backend.

## Features

- **Authentication**: Secure login with API keys
- **Real-time Metrics**: Live telemetry data visualization
- **Interactive Filtering**: Filter by service, node, endpoint, and time range
- **Modern UI**: Built with Material-UI following design best practices
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

## Quick Start

### Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Access the dashboard:**
   Open http://localhost:3000 in your browser

### Production

1. **Build the static files:**
   ```bash
   npm run build
   ```

2. **Files are built to `../app/static/`** and served by the Malti backend at `/static/`

## Authentication

The dashboard uses API key authentication. 

## API Integration

The dashboard connects to the Malti backend API:

- **Development**: Uses Vite proxy to `http://localhost:8000`
- **Production**: Served from the same origin as the backend

### Key Endpoints

- `GET /api/v1/auth/test` - Validate API key
- `GET /api/v1/metrics/aggregate` - Get aggregated metrics data

## Dashboard Features

### Filters & Controls
- **Service & Node Selector**: Hierarchical filtering
- **Time Range**: Quick time range selection (6h, 24h, 7d, 30d, 3m, 6m, 1y)
- **Endpoint Filter**: Filter by specific endpoints

### Visualizations
- **Metrics Overview**: Key metrics cards (requests, latency stats)
- **Status Indicator**: System health overview
- **Latency Time Series**: Response time trends over time
- **Endpoints Chart**: Top endpoints by request count
- **Consumer Distribution**: Request distribution by consumer

### Mobile Support
- Fully responsive design
- Touch-friendly interface
- Optimized layouts for smaller screens

## Technology Stack

- **Framework**: React 19 + Vite
- **UI Library**: Material-UI v7
- **Charts**: Recharts
- **State Management**: Zustand + React Context
- **Styling**: Emotion (via MUI)

## Development Notes

- The dashboard requires the Malti backend to be running
- All API requests include the `X-API-Key` header
- Time calculations are done in UTC
- Data is fetched automatically when filters change
- No server-side rendering - pure client-side app