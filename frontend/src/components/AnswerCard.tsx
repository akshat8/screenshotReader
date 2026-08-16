interface AnswerCardProps {
  answer: string;
  found: boolean;
}

export function AnswerCard({ answer, found }: AnswerCardProps) {
  return (
    <section
      className="answer-card"
      aria-labelledby="answer-heading"
      data-testid="answer-card"
    >
      <h2 id="answer-heading" className="section-subtitle">Answer</h2>
      <div
        className={found ? "answer-text" : "answer-text answer-not-found"}
        role="status"
        aria-live="polite"
        data-testid="answer-text"
      >
        {answer}
      </div>
    </section>
  );
}
