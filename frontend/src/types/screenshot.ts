export type ProcessingStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export interface ScreenshotSummary {
  id: string;
  filename: string;
  status: ProcessingStatus;
}

export interface UploadScreenshotItem {
  id: string;
  filename: string;
  status: ProcessingStatus;
}

export interface UploadResponse {
  uploaded: number;
  screenshots: UploadScreenshotItem[];
}

export interface ScreenshotListResponse {
  screenshots: ScreenshotSummary[];
}

export interface QueryRequest {
  query: string;
}

export interface QuerySource {
  id: string;
  filename: string;
  relevance: number;
}

export interface QueryResponse {
  answer: string;
  sources: QuerySource[];
  found: boolean;
}
