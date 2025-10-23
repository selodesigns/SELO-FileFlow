# FileFlow Web UI Guide

Complete guide for using and deploying the FileFlow web interface.

## Overview

FileFlow now includes a modern web-based interface as an alternative to the PyQt desktop application. The web UI provides the same functionality through a browser-accessible interface.

## Architecture

### Backend: FastAPI + Uvicorn

The web API is built with FastAPI, providing:
- RESTful API endpoints for all FileFlow operations
- Auto-generated OpenAPI documentation at `/docs`
- WebSocket support for real-time updates (future)
- CORS configuration for development

**Location**: `fileflow/web/`

### Frontend: React + TypeScript + Vite

The web UI is built with:
- React 18 with TypeScript for type safety
- Vite for fast development and optimized builds
- TailwindCSS for modern, responsive styling
- Lucide React for icons

**Location**: `web/`

## Quick Start

### 1. Install Backend Dependencies

```bash
# Install Python dependencies including web API packages
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, and Pydantic in addition to existing FileFlow dependencies.

### 2. Start the API Server

#### Option A: Using main module
```bash
python -m fileflow.main --web --host 127.0.0.1 --port 9001
```

#### Option B: Using dedicated script
```bash
python scripts/run_web_server.py --host 127.0.0.1 --port 9001
```

#### Option C: Production deployment with custom settings
```bash
python scripts/run_web_server.py --host 0.0.0.0 --port 9001 --public
```

**API Documentation**: Visit `http://localhost:9001/docs` for interactive API documentation.

### 3. Install Frontend Dependencies

```bash
cd web
npm install
```

### 4. Start the Frontend Development Server

```bash
npm run dev
```

The web UI will be available at `http://localhost:5173`

## API Endpoints

### Configuration
- `GET /api/config` - Retrieve current configuration
- `PUT /api/config` - Update configuration

### File Operations
- `POST /api/organize` - Start file organization
- `POST /api/reorganize` - Start reorganization with content classification
- `POST /api/organize/path` - Organize a single file

### Watcher Control
- `POST /api/watch/start` - Start file watcher daemon
- `POST /api/watch/stop` - Stop file watcher daemon
- `GET /api/watch/status` - Get watcher status and uptime

### System
- `GET /health` - Health check endpoint
- `GET /api/stats` - Organization statistics (planned)

## Web UI Features

### Configuration Panel

Manage source and destination directories:
- Add/remove source directories to monitor
- Configure destination directories by category
- Real-time validation of directory paths

### File Types Panel

Configure file type categories:
- Add custom categories
- Edit file extensions for each category
- Remove unused categories

### Classification Panel

Configure advanced content classification:
- Enable/disable content classification
- Toggle filename pattern analysis
- Toggle visual content analysis
- Adjust sensitivity thresholds
- Privacy settings for NSFW notifications

### Actions Panel

Trigger file organization operations:
- **Organize Files**: Process files from source directories
- **Reorganize Files**: Apply enhanced classification to existing files
- Background operations with progress feedback

### Watcher Panel

Control the file watcher daemon:
- Start/stop the watcher
- View current status and uptime
- Automatic status polling

## Production Deployment

### Option 1: Standalone API + Static Frontend

1. Build the frontend:
```bash
cd web
npm run build
```

2. Serve the API with static files:
```python
# Add to fileflow/web/api.py
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")
```

3. Run the server:
```bash
python -m fileflow.main --web --host 0.0.0.0 --port 9001
```

Access the full application at `http://your-server:9001`

### Option 2: Reverse Proxy (Nginx)

#### Backend
```bash
uvicorn fileflow.web.api:app --host 127.0.0.1 --port 9001
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name fileflow.example.com;

    # Frontend
    location / {
        root /path/to/web/dist;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api {
        proxy_pass http://127.0.0.1:9001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://127.0.0.1:9001;
    }
}
```

### Option 3: Docker Deployment (Future)

A Dockerfile will be provided for containerized deployment.

## Security Considerations

### Development
- CORS is enabled for `localhost:5173` and `localhost:3000`
- API runs on `127.0.0.1` by default (localhost only)

### Production
- **Never expose the API publicly without authentication**
- Consider adding authentication middleware (JWT, OAuth, etc.)
- Use HTTPS (TLS/SSL) for all connections
- Restrict CORS to your specific domain
- Run behind a reverse proxy (Nginx/Apache)
- Use systemd or supervisor for process management

### Authentication (Not Yet Implemented)

Future versions will include:
- API key authentication
- User session management
- Role-based access control

## Systemd Service (Linux)

Create `/etc/systemd/system/fileflow-web.service`:

```ini
[Unit]
Description=FileFlow Web API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/selo-fileflow
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m fileflow.main --web --host 127.0.0.1 --port 9001
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fileflow-web
sudo systemctl start fileflow-web
```

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- **Frontend**: Vite automatically reloads on file changes
- **Backend**: Add `--reload` flag to uvicorn

### API Testing

Use the built-in Swagger UI:
```
http://localhost:9001/docs
```

Or use curl:
```bash
# Get configuration
curl http://localhost:9001/api/config

# Start organization
curl -X POST http://localhost:9001/api/organize \
  -H "Content-Type: application/json" \
  -d '{}'

# Check watcher status
curl http://localhost:9001/api/watch/status
```

### Type Safety

The TypeScript frontend uses strict type checking. Update `web/src/types/index.ts` if you modify API contracts.

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 9001
lsof -i :9001

# Use a different port
python -m fileflow.main --web --port 9002
```

### CORS Errors

Ensure the frontend is configured to proxy API requests (see `web/vite.config.ts`).

### API Not Accessible

1. Check the API server is running
2. Verify firewall settings
3. Test health endpoint: `curl http://localhost:9001/health`

### Build Failures

```bash
# Clean and reinstall frontend dependencies
cd web
rm -rf node_modules package-lock.json
npm install
```

## Comparison: Web UI vs Desktop UI

| Feature | Web UI | Desktop UI (PyQt) |
|---------|--------|-------------------|
| Installation | Node.js + Python | Python + Qt |
| Access | Any browser | Local application |
| Remote Control | Yes (with proper setup) | No |
| System Integration | API-based | Native |
| Resource Usage | Lightweight | Moderate |
| Deployment | Web server | Desktop install |

## Future Enhancements

- [ ] Real-time progress updates via WebSocket
- [ ] File browser interface
- [ ] Detailed organization statistics and charts
- [ ] Authentication and multi-user support
- [ ] Dark mode
- [ ] Mobile-responsive improvements
- [ ] Export/import configuration

## Support

For issues or questions:
1. Check this guide
2. Review API documentation at `/docs`
3. Check frontend console for errors (F12 in browser)
4. Review backend logs

## License

Same as FileFlow main project.
