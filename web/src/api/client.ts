/**
 * FileFlow API Client
 * 
 * Provides typed API methods for interacting with the FileFlow backend.
 */

import type {
  ConfigResponse,
  ConfigUpdate,
  OrganizeRequest,
  ReorganizeRequest,
  OrganizePathRequest,
  OrganizeResponse,
  WatcherStatus,
  HealthStatus,
  ApiError
} from '../types';

const API_BASE = import.meta.env.DEV ? 'http://localhost:9001' : '';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  }

  // Health & Status
  async getHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health');
  }

  // Configuration
  async getConfig(): Promise<ConfigResponse> {
    return this.request<ConfigResponse>('/api/config');
  }

  async updateConfig(config: ConfigUpdate): Promise<{ status: string; message: string }> {
    return this.request('/api/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  // File Organization
  async organize(request: OrganizeRequest = {}): Promise<OrganizeResponse> {
    return this.request<OrganizeResponse>('/api/organize', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async reorganize(request: ReorganizeRequest = {}): Promise<OrganizeResponse> {
    return this.request<OrganizeResponse>('/api/reorganize', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async organizePath(request: OrganizePathRequest): Promise<OrganizeResponse> {
    return this.request<OrganizeResponse>('/api/organize/path', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Watcher Control
  async startWatcher(): Promise<{ status: string; message: string }> {
    return this.request('/api/watch/start', {
      method: 'POST',
    });
  }

  async stopWatcher(): Promise<{ status: string; message: string }> {
    return this.request('/api/watch/stop', {
      method: 'POST',
    });
  }

  async getWatcherStatus(): Promise<WatcherStatus> {
    return this.request<WatcherStatus>('/api/watch/status');
  }
}

export const apiClient = new ApiClient();
