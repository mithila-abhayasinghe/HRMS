import { useSearch } from "@tanstack/react-router";
import ErrorPage from "./error";

export default function ErrorRoutePage() {
  const search = useSearch({ strict: false }) as {
    message?: string;
    from?: string;
    statusCode?: string;
  };

  // Determine error message based on context
  let errorMessage = search.message || "Something went wrong. Please try again.";
  let errorTitle = "Whoops!";
  let statusCode: number | undefined;

  // Parse status code if provided
  if (search.statusCode) {
    statusCode = parseInt(search.statusCode, 10);
  }

  // Customize based on where the error came from
  if (search.from === "login") {
    errorTitle = "Login Failed";
    if (!search.message) {
      errorMessage =
        "Unable to verify your credentials. Please check your connection and try again.";
    }
  }

  return (
    <ErrorPage
      title={errorTitle}
      message={errorMessage}
      statusCode={statusCode}
      showBackButton={true}
    />
  );
}
