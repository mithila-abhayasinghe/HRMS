import { Link } from "@tanstack/react-router";
import { House } from "lucide-react";
import { useAsgardeo } from "@asgardeo/react";
import { useEffect, useRef } from "react";
import { Button } from "./components/ui/button";
import { useAlert } from "./contexts/AlertContext";
import { AnimatedThemeToggler } from "./components/ui/animated-theme-toggler";

function App() {
  const { isSignedIn } = useAsgardeo();
  const { showAlert } = useAlert();
  const hasShownLoginAlert = useRef(false);

  // Show alert when user successfully logs in
  useEffect(() => {
    if (isSignedIn && !hasShownLoginAlert.current) {
      // Check if this is a fresh login (from session storage flag)
      const justLoggedIn = sessionStorage.getItem("justLoggedIn");
      if (justLoggedIn === "true") {
        showAlert({
          title: "Login Successful",
          message: "Welcome back! You have successfully logged in.",
          variant: "success",
        });
        sessionStorage.removeItem("justLoggedIn");
        hasShownLoginAlert.current = true;
      }
    }
  }, [isSignedIn, showAlert]);

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center gap-6 p-6">
      <div className="fixed top-4 right-4 z-50">
        <AnimatedThemeToggler className="flex items-center justify-center size-10 rounded-lg border bg-background hover:bg-accent transition-colors" />
      </div>
      <House className="size-12 text-black dark:text-white" />
      <div className="flex flex-col items-center gap-4 text-center">
        <h1 className="text-4xl font-bold">Welcome to HRMS</h1>
        <p className="text-muted-foreground text-lg">
          Human Resource Management System
        </p>
        <div className="mt-4 flex gap-4">
          {isSignedIn ? (
            <Link to="/profile">
              <Button size="lg" className="px-10 py-5 text-lg font-semibold">
                Go to Profile
              </Button>
            </Link>
          ) : (
            <Link to="/login">
              <Button size="lg" className="px-10 py-5 text-lg font-semibold">
                Go to Login
              </Button>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
