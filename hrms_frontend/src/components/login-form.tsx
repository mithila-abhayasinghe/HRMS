import { useAsgardeo } from "@asgardeo/react";
import { Building2 } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldSeparator,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useAlert } from "@/contexts/AlertContext";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { signIn, isSignedIn } = useAsgardeo();
  const { showAlert } = useAlert();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleAsgardeoLogin = async () => {
    // Check if user is already logged in
    if (isSignedIn) {
      showAlert({
        title: "Already Logged In",
        message: "You are already logged in. Redirecting to homepage...",
        variant: "default",
      });
      setTimeout(() => {
        navigate({ to: "/" });
      }, 1500);
      return;
    }

    setIsLoading(true);
    try {
      // Set flag for login success alert
      sessionStorage.setItem("justLoggedIn", "true");
      // Trigger Asgardeo sign in
      await signIn();
    } catch (err) {
      console.error("Asgardeo login error:", err);
      sessionStorage.removeItem("justLoggedIn");
      setIsLoading(false);
      throw {
        message:
          "Unable to connect to authentication service. Please try again later.",
        from: "login",
        title: "Authentication Error",
      };
    }
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsgardeoLogin();
        }}
      >
        <FieldGroup>
          <div className="flex flex-col items-center gap-2 text-center">
            <a
              href="#"
              className="flex flex-col items-center gap-2 font-medium"
            >
              <div className="flex size-8 items-center justify-center rounded-md bg-primary">
                <Building2 className="size-6 text-primary-foreground" />
              </div>
              <span className="sr-only">HRMS</span>
            </a>
            <h1 className="text-xl font-bold">Welcome to HRMS</h1>
            <FieldDescription>
              Don&apos;t have an account?{" "}
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  throw {
                    message:
                      "Sign up is not available at this time. Please try again later.",
                    from: "login",
                    title: "Sign Up Unavailable",
                  };
                }}
              >
                Sign up
              </a>
            </FieldDescription>
          </div>
          <Field>
            <FieldLabel htmlFor="email">Email</FieldLabel>
            <Input
              id="email"
              type="email"
              placeholder="example@example.com"
              disabled
              className="opacity-50 cursor-not-allowed"
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="password">Password</FieldLabel>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              disabled
              className="opacity-50 cursor-not-allowed"
            />
          </Field>
          <Field>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-black hover:bg-black/90 text-white"
            >
              {isLoading ? "Logging in..." : "Login with Asgardeo"}
            </Button>
          </Field>
          <FieldSeparator>Or</FieldSeparator>
          <Field>
            <Button
              variant="outline"
              type="button"
              disabled={isLoading}
              onClick={() => {
                throw {
                  message:
                    "Google authentication is not available at this time. Please try again later.",
                  from: "login",
                  title: "Google Login Unavailable",
                };
              }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path
                  d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
                  fill="currentColor"
                />
              </svg>
              Continue with Google
            </Button>
          </Field>
        </FieldGroup>
      </form>
      <FieldDescription className="px-6 text-center">
        By clicking continue, you agree to our{" "}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            throw {
              message: "Terms of Service page is not available at this time.",
              from: "login",
              title: "Page Unavailable",
            };
          }}
        >
          Terms of Service
        </a>{" "}
        and{" "}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            throw {
              message: "Privacy Policy page is not available at this time.",
              from: "login",
              title: "Page Unavailable",
            };
          }}
        >
          Privacy Policy
        </a>
        .
      </FieldDescription>
    </div>
  );
}
