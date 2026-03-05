import ErrorPage from "./error";

export default function NotFoundPage() {
  return (
    <ErrorPage
      title="404"
      message="The page you're looking for doesn't exist. Please check the URL or return to the home page."
      statusCode={404}
    />
  );
}
