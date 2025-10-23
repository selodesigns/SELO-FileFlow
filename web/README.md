# FileFlow Web UI

Modern React-based web interface for FileFlow file organizer.

## Features

- **Configuration Management**: Configure source/destination directories, file types, and classification settings
- **Real-time Watcher Control**: Start/stop the file watcher daemon from the web interface
- **File Organization**: Trigger one-time organization or reorganization operations
- **Content Classification**: Configure advanced NSFW/SFW classification settings
- **Responsive Design**: Modern, clean UI built with React and TailwindCSS

## Setup

### Prerequisites

- Node.js 18+ and npm (or yarn/pnpm)
- FileFlow backend API server running (see parent directory)

### Installation

1. Install dependencies:
```bash
cd web
npm install
```

2. Start the development server:
```bash
npm run dev
```

The web UI will be available at `http://localhost:5173`

### Production Build

Build for production:
```bash
npm run build
```

The built files will be in the `dist/` directory and can be served statically.

## Architecture

### Tech Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Full type safety
- **Vite**: Fast development and optimized builds
- **TailwindCSS**: Utility-first styling
- **Lucide React**: Modern icon library

### Project Structure

```
web/
├── src/
│   ├── api/
│   │   └── client.ts          # API client with typed methods
│   ├── components/
│   │   ├── ConfigPanel.tsx    # Source/destination configuration
│   │   ├── FileTypesPanel.tsx # File type category management
│   │   ├── ClassificationPanel.tsx # Content classification settings
│   │   ├── ActionsPanel.tsx   # Organization actions
│   │   └── WatcherPanel.tsx   # Watcher control
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   ├── App.tsx                # Main application component
│   ├── main.tsx               # Application entry point
│   └── index.css              # Global styles
├── public/                     # Static assets
├── index.html                  # HTML entry point
└── package.json                # Dependencies and scripts
```

## API Integration

The web UI communicates with the FileFlow FastAPI backend:

- **Configuration**: `GET/PUT /api/config`
- **Organization**: `POST /api/organize`
- **Reorganization**: `POST /api/reorganize`
- **Watcher**: `POST /api/watch/start`, `POST /api/watch/stop`, `GET /api/watch/status`

Vite's proxy is configured to forward `/api` and `/health` requests to `http://localhost:9001`.

## Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

### Environment

The application automatically detects development mode and uses the appropriate API base URL:
- **Development**: Proxied through Vite to `http://localhost:9001`
- **Production**: Relative URLs (served from same origin as API)

## Configuration

Edit `vite.config.ts` to modify:
- Dev server port (default: 5173)
- API proxy configuration
- Build output directory

## Browser Support

Modern browsers with ES2020 support:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### API Connection Errors

1. Ensure the FileFlow API server is running:
```bash
python -m fileflow.main --web
# or
python scripts/run_web_server.py
```

2. Check that the API is accessible at `http://localhost:9001/health`

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## License

Same as parent FileFlow project.
