import { useState } from 'react';
import { Play, RefreshCw, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { apiClient } from '../api/client';

export default function ActionsPanel() {
  const [organizing, setOrganizing] = useState(false);
  const [reorganizing, setReorganizing] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleOrganize = async () => {
    try {
      setOrganizing(true);
      setMessage(null);

      const response = await apiClient.organize();
      setMessage({ type: 'success', text: response.message });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to start organization',
      });
    } finally {
      setOrganizing(false);
    }
  };

  const handleReorganize = async () => {
    try {
      setReorganizing(true);
      setMessage(null);

      const response = await apiClient.reorganize();
      setMessage({ type: 'success', text: response.message });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to start reorganization',
      });
    } finally {
      setReorganizing(false);
    }
  };

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

      {/* Organize Files */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary-100 rounded-lg">
            <Play className="w-6 h-6 text-primary-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold mb-2">Organize Files</h2>
            <p className="text-gray-600 mb-4">
              Process files from your configured source directories and organize them into
              destination folders based on file type and content classification.
            </p>
            <button
              onClick={handleOrganize}
              disabled={organizing}
              className="btn-primary flex items-center gap-2"
            >
              {organizing ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Organizing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Start Organization
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Reorganize Files */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-100 rounded-lg">
            <RefreshCw className="w-6 h-6 text-purple-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold mb-2">Reorganize Existing Files</h2>
            <p className="text-gray-600 mb-4">
              Apply enhanced content classification to files that have already been organized.
              This will separate existing files into SFW and NSFW subdirectories using advanced
              analysis.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-yellow-900">
                <strong>Note:</strong> This operation may take some time depending on the number of files.
                Visual analysis will be performed on all media files.
              </p>
            </div>
            <button
              onClick={handleReorganize}
              disabled={reorganizing}
              className="btn-primary flex items-center gap-2 bg-purple-600 hover:bg-purple-700"
            >
              {reorganizing ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Reorganizing...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Start Reorganization
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">How It Works</h3>
        <ul className="space-y-2 text-sm text-blue-900">
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              <strong>Organization:</strong> Scans source directories for new files and moves them to
              appropriate destinations based on file type and content.
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              <strong>Reorganization:</strong> Re-analyzes files already in destination directories
              using enhanced content classification to create SFW/NSFW subdirectories.
            </span>
          </li>
          <li className="flex gap-2">
            <span className="text-blue-600">•</span>
            <span>
              All operations run in the background and won't block the UI.
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}
