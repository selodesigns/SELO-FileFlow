import { useState, useEffect } from 'react';
import { Activity, Play, Square, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';
import type { WatcherStatus } from '../types';

export default function WatcherPanel() {
  const [status, setStatus] = useState<WatcherStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadStatus = async () => {
    try {
      const watcherStatus = await apiClient.getWatcherStatus();
      setStatus(watcherStatus);
    } catch (error) {
      console.error('Failed to load watcher status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    
    // Poll status every 5 seconds
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    try {
      setActionLoading(true);
      setMessage(null);

      const response = await apiClient.startWatcher();
      setMessage({ type: 'success', text: response.message });
      await loadStatus();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to start watcher',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    try {
      setActionLoading(true);
      setMessage(null);

      const response = await apiClient.stopWatcher();
      setMessage({ type: 'success', text: response.message });
      await loadStatus();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to stop watcher',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const formatUptime = (seconds?: number): string => {
    if (!seconds) return 'N/A';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Message Display */}
      {message && (
        <div
          className={`
            p-4 rounded-lg flex items-center gap-3
            ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}
          `}
        >
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Watcher Status */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-lg ${status?.running ? 'bg-green-100' : 'bg-gray-100'}`}>
            <Activity className={`w-6 h-6 ${status?.running ? 'text-green-600' : 'text-gray-600'}`} />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold">File Watcher Daemon</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Automatically monitors source directories for new files
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`
                    px-3 py-1 rounded-full text-sm font-medium
                    ${status?.running ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
                  `}
                >
                  {status?.running ? 'Running' : 'Stopped'}
                </span>
              </div>
            </div>

            {/* Status Details */}
            <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="font-medium">{status?.running ? 'Active' : 'Inactive'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Uptime</p>
                <p className="font-medium">{formatUptime(status?.uptime_seconds)}</p>
              </div>
            </div>

            {/* Controls */}
            <div className="flex gap-3">
              {!status?.running ? (
                <button
                  onClick={handleStart}
                  disabled={actionLoading}
                  className="btn-primary flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  {actionLoading ? 'Starting...' : 'Start Watcher'}
                </button>
              ) : (
                <button
                  onClick={handleStop}
                  disabled={actionLoading}
                  className="btn-danger flex items-center gap-2"
                >
                  <Square className="w-4 h-4" />
                  {actionLoading ? 'Stopping...' : 'Stop Watcher'}
                </button>
              )}
              
              <button
                onClick={loadStatus}
                disabled={actionLoading}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">About File Watcher</h3>
        <ul className="space-y-2 text-sm text-blue-900">
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              The file watcher automatically monitors your configured source directories for new files.
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              When a new file is detected, it's immediately organized according to your configuration.
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              Content classification is applied automatically to media files.
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              The watcher runs in the background and doesn't require manual intervention.
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}
