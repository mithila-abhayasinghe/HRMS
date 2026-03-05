import type { ErrorComponentProps } from "@tanstack/react-router";
import ErrorPage from "@/pages/error";

interface CustomError {
  message?: string;
  statusCode?: number;
  title?: string;
  from?: string;
}

export default function RouterErrorComponent({ error }: ErrorComponentProps) {
  // Default error values
  let errorMessage = "Something went wrong. Please try again.";
  let errorTitle = "Whoops!";
  let statusCode: number | undefined;

  // Handle custom error objects
  if (error && typeof error === "object") {
    const customError = error as CustomError;

    errorMessage = customError.message || errorMessage;
    errorTitle = customError.title || errorTitle;
    statusCode = customError.statusCode;

    // Customize based on where the error came from
    if (customError.from === "login") {
      errorTitle = customError.title || "Login Failed";
      if (!customError.message) {
        errorMessage =
          "Unable to verify your credentials. Please check your connection and try again.";
      }
    } else if (customError.from === "user" || customError.from === "profile") {
      errorTitle = customError.title || "Profile Error";
      if (!customError.message) {
        errorMessage =
          "Unable to load your profile. Please check your connection and try again.";
      }
    }
  }

  // Handle standard Error objects
  if (error instanceof Error) {
    errorMessage = error.message || errorMessage;
    errorTitle = "Application Error";
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
