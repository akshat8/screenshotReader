import type { AgentDecision } from "../types/screenshot";

interface AnswerCardProps {
  answer: string;
  found: boolean;
  needsClarification?: boolean;
  decisions?: AgentDecision[];
}

export function AnswerCard({
  answer,
  found,
  needsClarification = false,
  decisions = [],
}: AnswerCardProps) {
  const heading = needsClarification ? "Clarifying Question" : "Answer";
  let textClassName = "answer-text";
  if (needsClarification) {
    textClassName = "answer-text answer-clarification";
  } else if (!found) {
    textClassName = "answer-text answer-not-found";
  }

  return (
    <section
      className="answer-card"
      aria-labelledby="answer-heading"
      data-testid="answer-card"
    >
      <h2 id="answer-heading" className="section-subtitle">
        {heading}
      </h2>
      <div
        className={textClassName}
        role="status"
        aria-live="polite"
        data-testid="answer-text"
      >
        {answer}
      </div>
      {decisions.length > 0 && (
        <div data-testid="agent-decisions">
          <h3 className="section-subtitle">Agent decisions</h3>
          <ol className="decision-list">
            {decisions.map((item, index) => (
              <li key={`${item.step}-${index}`} data-testid="agent-decision-item">
                <span className="decision-step">{item.step}</span>
                <span>{item.decision}</span>
                {item.reason ? (
                  <span className="decision-reason">{item.reason}</span>
                ) : null}
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
