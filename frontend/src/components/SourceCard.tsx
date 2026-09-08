import { useState } from "react";

import { getScreenshotImageUrl } from "../services/api";
import type { QuerySource } from "../types/screenshot";

interface SourceCardProps {
  source: QuerySource;
}

export function SourceCard({ source }: SourceCardProps) {
  const [imageFailed, setImageFailed] = useState(false);
  const imageUrl = getScreenshotImageUrl(source.id);

  return (
    <article className="source-card" data-testid="source-card">
      <div className="source-thumbnail-wrap">
        {imageFailed ? (
          <p className="source-thumbnail-fallback" data-testid="source-thumbnail-fallback">
            Preview unavailable
          </p>
        ) : (
          <img
            src={imageUrl}
            alt={`Screenshot source: ${source.filename}`}
            className="source-thumbnail"
            loading="lazy"
            data-testid="source-thumbnail"
            onError={() => setImageFailed(true)}
          />
        )}
      </div>
      <div className="source-meta">
        <p className="source-filename">{source.filename}</p>
        <p className="source-relevance">
          Relevance: {source.relevance.toFixed(2)}
        </p>
      </div>
    </article>
  );
}
