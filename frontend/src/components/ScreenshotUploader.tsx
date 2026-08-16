import { useRef, useState, type ChangeEvent, type DragEvent } from "react";

import axios from "axios";
import { uploadScreenshots } from "../services/api";

const MAX_UPLOAD_COUNT = 50;
const ALLOWED_TYPES = new Set([
  "image/png",
  "image/jpeg",
  "image/jpg",
  "image/webp",
]);
const ALLOWED_EXTENSIONS = new Set(["png", "jpg", "jpeg", "webp"]);

interface ScreenshotUploaderProps {
  onUploadComplete: () => void;
}

function isAllowedFile(file: File): boolean {
  if (ALLOWED_TYPES.has(file.type)) {
    return true;
  }
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  return ALLOWED_EXTENSIONS.has(extension);
}

export function ScreenshotUploader({ onUploadComplete }: ScreenshotUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = async (fileList: FileList | File[]) => {
    const selectedFiles = Array.from(fileList);
    if (selectedFiles.length === 0) {
      return;
    }

    if (selectedFiles.length > MAX_UPLOAD_COUNT) {
      setError(`Maximum ${MAX_UPLOAD_COUNT} files allowed per upload.`);
      return;
    }

    const invalidFiles = selectedFiles.filter((file) => !isAllowedFile(file));
    if (invalidFiles.length > 0) {
      setError(
        `Invalid file type: ${invalidFiles.map((file) => file.name).join(", ")}. Use PNG, JPG, or WEBP.`,
      );
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      await uploadScreenshots(selectedFiles);
      onUploadComplete();
    } catch (uploadError) {
      let message = "Upload failed. Please try again.";
      if (axios.isAxiosError(uploadError)) {
        const detail = uploadError.response?.data?.detail;
        if (typeof detail === "string") {
          message = detail;
        }
      } else if (uploadError instanceof Error) {
        message = uploadError.message;
      }
      setError(message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      handleFiles(event.target.files);
    }
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    if (event.dataTransfer.files.length > 0) {
      handleFiles(event.dataTransfer.files);
    }
  };

  return (
    <section className="upload-section" aria-labelledby="upload-heading">
      <div
        className={`upload-dropzone${isDragActive ? " upload-dropzone-active" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        data-testid="upload-dropzone"
      >
        <p className="upload-dropzone-text">Drop screenshots here</p>
        <input
          ref={fileInputRef}
          id="screenshot-file-input"
          type="file"
          accept="image/png,image/jpeg,image/webp"
          multiple
          className="upload-file-input"
          onChange={handleInputChange}
          disabled={isUploading}
          aria-label="Select screenshot files"
          data-testid="screenshot-file-input"
        />
        <button
          type="button"
          className="upload-select-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          data-testid="upload-select-button"
        >
          {isUploading ? "Uploading…" : "Select Screenshots"}
        </button>
      </div>

      {isUploading && (
        <p className="upload-status" role="status" aria-live="polite">
          Uploading files…
        </p>
      )}

      {error && (
        <p className="upload-error" role="alert" data-testid="upload-error">
          {error}
        </p>
      )}
    </section>
  );
}
