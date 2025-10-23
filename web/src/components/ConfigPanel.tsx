import { useState } from 'react';
import { FolderPlus, Trash2, Save, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';
import type { FileFlowConfig } from '../types';

interface ConfigPanelProps {
  config: FileFlowConfig;
  onUpdate: () => void;
}

export default function ConfigPanel({ config, onUpdate }: ConfigPanelProps) {
  const [sources, setSources] = useState<string[]>(config.source_directories || []);
  const [destinations, setDestinations] = useState<Record<string, string>>(
    config.destination_directories || {}
  );
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [newSource, setNewSource] = useState('');
  const [newDestCategory, setNewDestCategory] = useState('');
  const [newDestPath, setNewDestPath] = useState('');

  const handleAddSource = () => {
    if (newSource.trim() && !sources.includes(newSource.trim())) {
      setSources([...sources, newSource.trim()]);
      setNewSource('');
    }
  };

  const handleRemoveSource = (index: number) => {
    setSources(sources.filter((_, i) => i !== index));
  };

  const handleAddDestination = () => {
    if (newDestCategory.trim() && newDestPath.trim()) {
      setDestinations({
        ...destinations,
        [newDestCategory.trim()]: newDestPath.trim(),
      });
      setNewDestCategory('');
      setNewDestPath('');
    }
  };

  const handleRemoveDestination = (category: string) => {
    const updated = { ...destinations };
    delete updated[category];
    setDestinations(updated);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage(null);

      await apiClient.updateConfig({
        source_directories: sources,
        destination_directories: destinations,
      });

      setMessage({ type: 'success', text: 'Configuration saved successfully!' });
      onUpdate();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to save configuration',
      });
    } finally {
      setSaving(false);
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

      {/* Source Directories */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <FolderPlus className="w-5 h-5 text-primary-600" />
          Source Directories
        </h2>
        <p className="text-gray-600 text-sm mb-4">
          Directories that FileFlow monitors for files to organize.
        </p>

        <div className="space-y-3">
          {sources.map((source, index) => (
            <div key={index} className="flex items-center gap-2">
              <input
                type="text"
                value={source}
                readOnly
                className="input-field flex-1 bg-gray-50"
              />
              <button
                onClick={() => handleRemoveSource(index)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                title="Remove"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newSource}
              onChange={(e) => setNewSource(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSource()}
              placeholder="/path/to/source/directory"
              className="input-field flex-1"
            />
            <button onClick={handleAddSource} className="btn-primary">
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Destination Directories */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <FolderPlus className="w-5 h-5 text-primary-600" />
          Destination Directories
        </h2>
        <p className="text-gray-600 text-sm mb-4">
          Category-based destination folders for organized files.
        </p>

        <div className="space-y-3">
          {Object.entries(destinations).map(([category, path]) => (
            <div key={category} className="flex items-center gap-2">
              <input
                type="text"
                value={`${category}: ${path}`}
                readOnly
                className="input-field flex-1 bg-gray-50"
              />
              <button
                onClick={() => handleRemoveDestination(category)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                title="Remove"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}

          <div className="grid grid-cols-3 gap-2">
            <input
              type="text"
              value={newDestCategory}
              onChange={(e) => setNewDestCategory(e.target.value)}
              placeholder="Category (e.g., images)"
              className="input-field"
            />
            <input
              type="text"
              value={newDestPath}
              onChange={(e) => setNewDestPath(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddDestination()}
              placeholder="/path/to/destination"
              className="input-field"
            />
            <button onClick={handleAddDestination} className="btn-primary">
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
}
