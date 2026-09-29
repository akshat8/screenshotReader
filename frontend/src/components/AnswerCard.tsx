interface AnswerCardProps {
  answer: string;
  found: boolean;
  needsClarification?: boolean;
}

export function AnswerCard({
  answer,
  found,
  needsClarification = false,
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
    </section>
  );
}
