import { useState } from 'react';
import { Brain, Save, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { apiClient } from '../api/client';
import type { FileFlowConfig, ContentClassificationConfig } from '../types';

interface ClassificationPanelProps {
  config: FileFlowConfig;
  onUpdate: () => void;
}

export default function ClassificationPanel({ config, onUpdate }: ClassificationPanelProps) {
  const [classification, setClassification] = useState<ContentClassificationConfig>(
    config.content_classification || {
      enabled: true,
      use_filename_analysis: true,
      use_visual_analysis: true,
      classify_media_only: true,
      notify_nsfw_moves: false,
      visual_analysis_threshold: 0.6,
    }
  );
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleToggle = (key: keyof ContentClassificationConfig) => {
    setClassification({
      ...classification,
      [key]: !classification[key],
    });
  };

  const handleThresholdChange = (value: number) => {
    setClassification({
      ...classification,
      visual_analysis_threshold: value / 100,
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage(null);

      await apiClient.updateConfig({
        content_classification: classification,
      });

      setMessage({ type: 'success', text: 'Classification settings saved successfully!' });
      onUpdate();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to save settings',
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

      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-900">
          <p className="font-medium mb-1">Advanced Content Classification</p>
          <p>
            FileFlow uses multi-layered analysis to automatically separate NSFW and SFW content
            using filename patterns, visual analysis, and metadata inspection.
          </p>
        </div>
      </div>

      {/* Main Settings */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary-600" />
          Classification Settings
        </h2>

        <div className="space-y-6">
          {/* Master Toggle */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium">Enable Content Classification</h3>
              <p className="text-sm text-gray-600">
                Master switch for all content classification features
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={classification.enabled}
                onChange={() => handleToggle('enabled')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          {/* Analysis Methods */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Analysis Methods</h3>
            
            <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium">Filename Pattern Analysis</p>
                <p className="text-sm text-gray-600">
                  Analyze filenames for NSFW/SFW keywords
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={classification.use_filename_analysis}
                  onChange={() => handleToggle('use_filename_analysis')}
                  disabled={!classification.enabled}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer disabled:opacity-50 disabled:cursor-not-allowed peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium">Visual Content Analysis</p>
                <p className="text-sm text-gray-600">
                  Use computer vision for skin detection and color analysis
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={classification.use_visual_analysis}
                  onChange={() => handleToggle('use_visual_analysis')}
                  disabled={!classification.enabled}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer disabled:opacity-50 disabled:cursor-not-allowed peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>

          {/* Classification Scope */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Classification Scope</h3>
            
            <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium">Classify Media Files Only</p>
                <p className="text-sm text-gray-600">
                  Only classify images and videos, skip other file types
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={classification.classify_media_only}
                  onChange={() => handleToggle('classify_media_only')}
                  disabled={!classification.enabled}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer disabled:opacity-50 disabled:cursor-not-allowed peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>

          {/* Privacy */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Privacy & Notifications</h3>
            
            <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium">Enable NSFW Move Notifications</p>
                <p className="text-sm text-gray-600">
                  Show notifications when NSFW content is detected (disabled by default for privacy)
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={classification.notify_nsfw_moves}
                  onChange={() => handleToggle('notify_nsfw_moves')}
                  disabled={!classification.enabled}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer disabled:opacity-50 disabled:cursor-not-allowed peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>

          {/* Threshold Slider */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900">Visual Analysis Threshold</h3>
            <p className="text-sm text-gray-600">
              Adjust sensitivity level (higher = more conservative)
            </p>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="30"
                max="90"
                value={(classification.visual_analysis_threshold || 0.6) * 100}
                onChange={(e) => handleThresholdChange(parseInt(e.target.value))}
                disabled={!classification.enabled || !classification.use_visual_analysis}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <span className="text-sm font-medium w-12 text-center">
                {Math.round((classification.visual_analysis_threshold || 0.6) * 100)}%
              </span>
            </div>
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
          {saving ? 'Saving...' : 'Save Classification Settings'}
        </button>
      </div>
    </div>
  );
}
