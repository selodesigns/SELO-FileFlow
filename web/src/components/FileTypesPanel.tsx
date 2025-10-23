import { useState } from 'react';
import { FileType, Save, Plus, Trash2, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';
import type { FileFlowConfig } from '../types';

interface FileTypesPanelProps {
  config: FileFlowConfig;
  onUpdate: () => void;
}

export default function FileTypesPanel({ config, onUpdate }: FileTypesPanelProps) {
  const [fileTypes, setFileTypes] = useState<Record<string, string[]>>(
    config.file_types || {}
  );
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [newCategory, setNewCategory] = useState('');
  const [editingCategory, setEditingCategory] = useState<string | null>(null);
  const [editingExtensions, setEditingExtensions] = useState('');

  const handleAddCategory = () => {
    if (newCategory.trim() && !fileTypes[newCategory.trim()]) {
      setFileTypes({
        ...fileTypes,
        [newCategory.trim()]: [],
      });
      setNewCategory('');
    }
  };

  const handleRemoveCategory = (category: string) => {
    const updated = { ...fileTypes };
    delete updated[category];
    setFileTypes(updated);
  };

  const handleEditExtensions = (category: string) => {
    setEditingCategory(category);
    setEditingExtensions(fileTypes[category].join(', '));
  };

  const handleSaveExtensions = () => {
    if (editingCategory) {
      const extensions = editingExtensions
        .split(',')
        .map((ext) => ext.trim())
        .filter((ext) => ext.length > 0)
        .map((ext) => (ext.startsWith('.') ? ext : `.${ext}`));

      setFileTypes({
        ...fileTypes,
        [editingCategory]: extensions,
      });
      setEditingCategory(null);
      setEditingExtensions('');
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage(null);

      await apiClient.updateConfig({
        file_types: fileTypes,
      });

      setMessage({ type: 'success', text: 'File types saved successfully!' });
      onUpdate();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to save file types',
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

      {/* File Type Categories */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <FileType className="w-5 h-5 text-primary-600" />
          File Type Categories
        </h2>
        <p className="text-gray-600 text-sm mb-4">
          Define which file extensions belong to each category.
        </p>

        <div className="space-y-4">
          {Object.entries(fileTypes).map(([category, extensions]) => (
            <div key={category} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-lg capitalize">{category}</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEditExtensions(category)}
                    className="px-3 py-1 text-sm bg-primary-100 text-primary-700 rounded hover:bg-primary-200 transition"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleRemoveCategory(category)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              {editingCategory === category ? (
                <div className="space-y-2">
                  <input
                    type="text"
                    value={editingExtensions}
                    onChange={(e) => setEditingExtensions(e.target.value)}
                    placeholder=".jpg, .png, .gif"
                    className="input-field"
                  />
                  <div className="flex gap-2">
                    <button onClick={handleSaveExtensions} className="btn-primary text-sm">
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditingCategory(null);
                        setEditingExtensions('');
                      }}
                      className="btn-secondary text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {extensions.length > 0 ? (
                    extensions.map((ext) => (
                      <span
                        key={ext}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                      >
                        {ext}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-400 text-sm italic">No extensions defined</span>
                  )}
                </div>
              )}
            </div>
          ))}

          {/* Add New Category */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCategory()}
              placeholder="New category name"
              className="input-field flex-1"
            />
            <button onClick={handleAddCategory} className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Category
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
          {saving ? 'Saving...' : 'Save File Types'}
        </button>
      </div>
    </div>
  );
}
