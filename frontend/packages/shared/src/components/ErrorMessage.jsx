export default function ErrorMessage({ message = "Something went wrong" }) {
  return (
    <div role="alert">
      {message}
    </div>
  );
}
