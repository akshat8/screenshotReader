import axios from "axios";
import { useState } from "react";

import { AnswerCard } from "../components/AnswerCard";
import { ScreenshotList } from "../components/ScreenshotList";
import { ScreenshotUploader } from "../components/ScreenshotUploader";
import { SearchBox } from "../components/SearchBox";
import { SourceCard } from "../components/SourceCard";
import { queryScreenshots } from "../services/api";
import type { QueryResponse } from "../types/screenshot";

export function Home() {
  const [refreshToken, setRefreshToken] = useState(0);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [isQueryLoading, setIsQueryLoading] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);

  const handleUploadComplete = () => {
    setRefreshToken((current) => current + 1);
  };

  const handleSearch = async (query: string) => {
    setIsQueryLoading(true);
    setQueryError(null);

    try {
      const result = await queryScreenshots(query);
      setQueryResult(result);
    } catch (searchError) {
      let message = "Search failed. Please try again.";
      if (axios.isAxiosError(searchError)) {
        const detail = searchError.response?.data?.detail;
        if (typeof detail === "string") {
          message = detail;
        }
      } else if (searchError instanceof Error) {
        message = searchError.message;
      }
      setQueryError(message);
      setQueryResult(null);
    } finally {
      setIsQueryLoading(false);
    }
  };

  return (
    <main className="page" id="main-content">
      <header className="page-header">
        <h1 id="upload-heading">Screenshot Memory</h1>
        <p className="page-subtitle">
          Upload screenshots and search them with natural language questions.
        </p>
      </header>

      <ScreenshotUploader onUploadComplete={handleUploadComplete} />
      <ScreenshotList refreshToken={refreshToken} />

      <SearchBox onSearch={handleSearch} isLoading={isQueryLoading} />

      {queryError && (
        <p className="search-error" role="alert" data-testid="search-error">
          {queryError}
        </p>
      )}

      {queryResult && (
        <>
          <AnswerCard answer={queryResult.answer} found={queryResult.found} />
          {queryResult.sources.length > 0 && (
            <section
              className="sources-section"
              aria-labelledby="sources-heading"
              data-testid="sources-section"
            >
              <h2 id="sources-heading" className="section-subtitle">Sources</h2>
              <div className="sources-grid">
                {queryResult.sources.map((source) => (
                  <SourceCard key={source.id} source={source} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}
