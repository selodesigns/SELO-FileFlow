/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly DEV: boolean
  readonly PROD: boolean
  readonly SSR: boolean
  // Add other env variables here if needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
