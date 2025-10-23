/**
 * TypeScript type definitions for FileFlow API
 */

export interface FileFlowConfig {
  source_directories: string[];
  destination_directories: Record<string, string>;
  file_types: Record<string, string[]>;
  custom_mappings?: CustomMapping[];
  content_classification?: ContentClassificationConfig;
  notify_on_move?: boolean;
  autostart?: boolean;
}

export interface CustomMapping {
  extension: string;
  folder: string;
}

export interface ContentClassificationConfig {
  enabled: boolean;
  use_filename_analysis?: boolean;
  use_visual_analysis?: boolean;
  classify_media_only?: boolean;
  notify_nsfw_moves?: boolean;
  visual_analysis_threshold?: number;
  filename_overrides_visual?: boolean;
  create_content_subdirs?: boolean;
  cache_analysis_results?: boolean;
}

export interface ConfigResponse {
  config: FileFlowConfig;
}

export interface ConfigUpdate {
  source_directories?: string[];
  destination_directories?: Record<string, string>;
  file_types?: Record<string, string[]>;
  custom_mappings?: CustomMapping[];
  content_classification?: Partial<ContentClassificationConfig>;
  notify_on_move?: boolean;
  autostart?: boolean;
}

export interface OrganizeRequest {
  sources?: string[];
  dest?: string;
}

export interface ReorganizeRequest {
  target_dirs?: string[];
}

export interface OrganizePathRequest {
  path: string;
  dest?: string;
}

export interface OrganizeResponse {
  status: string;
  message: string;
}

export interface WatcherStatus {
  running: boolean;
  uptime_seconds?: number;
}

export interface HealthStatus {
  status: string;
  version: string;
}

export interface ApiError {
  detail: string;
}
