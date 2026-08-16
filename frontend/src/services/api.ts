import axios from "axios";

import type {
  QueryResponse,
  ScreenshotListResponse,
  UploadResponse,
} from "../types/screenshot";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

const apiClient = axios.create({
  baseURL: apiBaseUrl,
});

export async function uploadScreenshots(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await apiClient.post<UploadResponse>(
    "/api/screenshots/upload",
    formData,
  );
  return response.data;
}

export async function getScreenshots(): Promise<ScreenshotListResponse> {
  const response = await apiClient.get<ScreenshotListResponse>(
    "/api/screenshots",
  );
  return response.data;
}

export function getScreenshotImageUrl(screenshotId: string): string {
  return `${apiBaseUrl}/api/screenshots/${screenshotId}/image`;
}

export async function queryScreenshots(query: string): Promise<QueryResponse> {
  const response = await apiClient.post<QueryResponse>("/api/query", {
    query,
  });
  return response.data;
}
