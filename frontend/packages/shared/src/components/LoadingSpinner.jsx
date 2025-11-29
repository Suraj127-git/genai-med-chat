export default function LoadingSpinner({ text = "Loading..." }) {
  return (
    <div role="status" aria-live="polite">
      {text}
    </div>
  );
}
