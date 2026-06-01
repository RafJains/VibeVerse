type ErrorStateProps = {
  title?: string;
  message: string;
};

export default function ErrorState({
  title = "Unable to load data",
  message,
}: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-800">
      <p className="font-semibold">{title}</p>
      <p className="mt-2">{message}</p>
    </div>
  );
}
