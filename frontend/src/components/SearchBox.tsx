import { useState, type FormEvent } from "react";

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export function SearchBox({ onSearch, isLoading }: SearchBoxProps) {
  const [queryText, setQueryText] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuery = queryText.trim();
    if (!trimmedQuery || isLoading) {
      return;
    }
    onSearch(trimmedQuery);
  };

  return (
    <section className="search-section" aria-labelledby="search-heading">
      <h2 id="search-heading" className="section-subtitle">
        Search Your Screenshots
      </h2>
      <form className="search-form" onSubmit={handleSubmit} data-testid="search-form">
        <label className="search-label" htmlFor="search-query-input">
          Ask a question about your screenshots
        </label>
        <div className="search-controls">
          <input
            id="search-query-input"
            type="text"
            className="search-input"
            value={queryText}
            onChange={(event) => setQueryText(event.target.value)}
            placeholder="What was the AC repair person's number?"
            disabled={isLoading}
            aria-label="Search query"
            data-testid="search-query-input"
          />
          <button
            type="submit"
            className="search-ask-button"
            disabled={isLoading || queryText.trim().length < 2}
            data-testid="search-ask-button"
          >
            {isLoading ? "Asking…" : "Ask"}
          </button>
        </div>
        {isLoading && (
          <p className="search-loading" role="status" aria-live="polite">
            Searching your screenshots…
          </p>
        )}
      </form>
    </section>
  );
}
