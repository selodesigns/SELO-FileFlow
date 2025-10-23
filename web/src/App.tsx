import { useState, useEffect } from 'react';
import { Settings, Folder, FileType, Brain, Play, Activity } from 'lucide-react';
import { apiClient } from './api/client';
import type { FileFlowConfig } from './types';
import ConfigPanel from './components/ConfigPanel';
import FileTypesPanel from './components/FileTypesPanel';
import ClassificationPanel from './components/ClassificationPanel';
import ActionsPanel from './components/ActionsPanel';
import WatcherPanel from './components/WatcherPanel';

type TabId = 'config' | 'filetypes' | 'classification' | 'actions' | 'watcher';

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('config');
  const [config, setConfig] = useState<FileFlowConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getConfig();
      setConfig(response.config);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
      console.error('Failed to load config:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const tabs = [
    { id: 'config' as const, label: 'Configuration', icon: Folder },
    { id: 'filetypes' as const, label: 'File Types', icon: FileType },
    { id: 'classification' as const, label: 'Classification', icon: Brain },
    { id: 'actions' as const, label: 'Actions', icon: Play },
    { id: 'watcher' as const, label: 'Watcher', icon: Activity },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading FileFlow...</p>
        </div>
      </div>
    );
  }

  if (error && !config) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-red-600 mb-4">
            <Settings className="w-12 h-12 mx-auto mb-2" />
            <h2 className="text-xl font-semibold text-center">Connection Error</h2>
          </div>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={loadConfig}
            className="w-full bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700 transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Settings className="w-8 h-8 text-primary-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">FileFlow</h1>
              <span className="ml-3 px-2 py-1 text-xs bg-primary-100 text-primary-700 rounded-full">
                Web UI
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Advanced File Organizer
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center py-4 px-1 border-b-2 font-medium text-sm transition
                    ${
                      isActive
                        ? 'border-primary-600 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {config && (
          <>
            {activeTab === 'config' && <ConfigPanel config={config} onUpdate={loadConfig} />}
            {activeTab === 'filetypes' && <FileTypesPanel config={config} onUpdate={loadConfig} />}
            {activeTab === 'classification' && <ClassificationPanel config={config} onUpdate={loadConfig} />}
            {activeTab === 'actions' && <ActionsPanel />}
            {activeTab === 'watcher' && <WatcherPanel />}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
