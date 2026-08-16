import { useCallback, useEffect, useRef, useState } from "react";

import { getScreenshots } from "../services/api";
import type { ScreenshotSummary } from "../types/screenshot";
import { UploadProgress } from "./UploadProgress";

const POLL_INTERVAL_MS = 2500;

const ACTIVE_STATUSES = new Set(["pending", "processing"]);

interface ScreenshotListProps {
  refreshToken: number;
}

export function ScreenshotList({ refreshToken }: ScreenshotListProps) {
  const [screenshots, setScreenshots] = useState<ScreenshotSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const fetchScreenshots = useCallback(async () => {
    try {
      const response = await getScreenshots();
      setScreenshots(response.screenshots);
      setError(null);
    } catch (fetchError) {
      const message =
        fetchError instanceof Error
          ? fetchError.message
          : "Failed to load screenshots.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchScreenshots();
  }, [fetchScreenshots, refreshToken]);

  useEffect(() => {
    const needsPolling = screenshots.some((item) =>
      ACTIVE_STATUSES.has(item.status),
    );

    if (!needsPolling) {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    if (intervalRef.current === null) {
      intervalRef.current = window.setInterval(() => {
        fetchScreenshots();
      }, POLL_INTERVAL_MS);
    }

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [screenshots, fetchScreenshots]);

  if (loading) {
    return <p className="screenshot-list-loading">Loading screenshots…</p>;
  }

  if (error) {
    return (
      <p className="screenshot-list-error" role="alert">
        {error}
      </p>
    );
  }

  if (screenshots.length === 0) {
    return (
      <p className="screenshot-list-empty">No screenshots uploaded yet.</p>
    );
  }

  return (
    <div className="screenshot-list" data-testid="screenshot-list">
      <h2 className="section-subtitle">Uploaded Screenshots</h2>
      <ul className="screenshot-list-items">
        {screenshots.map((screenshot) => (
          <li key={screenshot.id}>
            <UploadProgress filename={screenshot.filename} status={screenshot.status} />
          </li>
        ))}
      </ul>
    </div>
  );
}
