import type { ProcessingStatus } from "../types/screenshot";

const STATUS_LABELS: Record<ProcessingStatus, string> = {
  completed: "Processed",
  processing: "Processing",
  pending: "Processing",
  failed: "Failed",
};

interface UploadProgressProps {
  filename: string;
  status: ProcessingStatus;
  errorMessage?: string;
}

export function UploadProgress({
  filename,
  status,
  errorMessage,
}: UploadProgressProps) {
  const statusClass = `status-badge status-${status}`;
  const statusLabel = STATUS_LABELS[status];

  return (
    <div className="upload-progress-row" data-testid="upload-progress-row">
      <span className="upload-progress-filename">{filename}</span>
      <span className={statusClass} aria-label={`Status: ${statusLabel}`}>
        {status === "completed" && "✓ Processed"}
        {(status === "processing" || status === "pending") && "⏳ Processing"}
        {status === "failed" && "✗ Failed"}
      </span>
      {status === "failed" && errorMessage && (
        <span className="upload-progress-error" title={errorMessage}>
          {errorMessage.length > 80
            ? `${errorMessage.slice(0, 80)}…`
            : errorMessage}
        </span>
      )}
    </div>
  );
}
