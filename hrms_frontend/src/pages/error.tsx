import { Button } from "@/components/ui/button";
import { useNavigate } from "@tanstack/react-router";

interface ErrorPageProps {
  title?: string;
  message?: string;
  statusCode?: number;
  showBackButton?: boolean;
}

export default function ErrorPage({
  title = "Whoops!",
  message = "The page you're looking for isn't found. We suggest you go back to home.",
  statusCode,
  showBackButton = true,
}: ErrorPageProps) {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate({ to: "/" });
  };

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      <div className="flex flex-col items-center justify-center px-4 py-8 text-center">
        {statusCode && (
          <p className="text-muted-foreground mb-2 text-sm font-medium">
            Error {statusCode}
          </p>
        )}
        <h2 className="mb-6 text-5xl font-semibold">{title}</h2>
        <h3 className="mb-1.5 text-3xl font-semibold">Something went wrong</h3>
        <p className="text-muted-foreground mb-6 max-w-sm">{message}</p>
        {showBackButton && (
          <Button
            size="lg"
            className="rounded-lg text-base shadow-sm bg-black text-white hover:bg-gray-800"
            onClick={handleGoHome}
          >
            Back to home page
          </Button>
        )}
      </div>

      {/* Right Section: Illustration */}
      <div className="relative max-h-screen w-full p-2 max-lg:hidden">
        <div className="h-full w-full rounded-2xl bg-black"></div>
        <img
          src="https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/error/image-1.png"
          alt="Error illustration"
          className="absolute top-1/2 left-1/2 h-[clamp(260px,25vw,406px)] -translate-x-1/2 -translate-y-1/2"
        />
      </div>
    </div>
  );
}
