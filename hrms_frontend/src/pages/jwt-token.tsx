import { useEffect, useState } from "react";
import { useAsgardeo } from "@asgardeo/react";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Copy, Check } from "lucide-react";
import { useAlert } from "@/contexts/AlertContext";

export default function JWTTokenPage() {
  const { getAccessToken, isSignedIn } = useAsgardeo();
  const [accessToken, setAccessToken] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);
  const [copied, setCopied] = useState(false);
  const { showAlert } = useAlert();

  // Ensure component is mounted before rendering dynamic content
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Fetch access token
  useEffect(() => {
    if (!isMounted) return;

    const fetchToken = async () => {
      if (!isSignedIn) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const token = await getAccessToken();
        setAccessToken(token || "");
      } catch (error) {
        console.error("Error fetching access token:", error);
        showAlert({
          title: "Error",
          message: "Failed to fetch JWT token",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchToken();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMounted, isSignedIn]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(accessToken);
      setCopied(true);
      showAlert({
        title: "Success",
        message: "JWT token copied to clipboard",
        variant: "success",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
      showAlert({
        title: "Error",
        message: "Failed to copy token to clipboard",
        variant: "destructive",
      });
    }
  };

  // Prevent hydration mismatch by showing loading state on initial render
  if (!isMounted) {
    return (
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2">
            <div className="flex items-center gap-2 px-4">
              <SidebarTrigger className="-ml-1" />
              <Separator
                orientation="vertical"
                className="mr-2 data-[orientation=vertical]:h-4"
              />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem className="hidden md:block">
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="hidden md:block" />
                  <BreadcrumbItem>
                    <BreadcrumbPage>JWT Token</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
            <div className="bg-muted/50 min-h-[50vh] rounded-xl p-6">
              <Skeleton className="h-8 w-48 mb-4" />
              <Skeleton className="h-32 w-full" />
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    );
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>JWT Token</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="bg-muted/50 min-h-[50vh] rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">JWT Access Token</h2>
              {!isLoading && accessToken && (
                <Button
                  onClick={handleCopy}
                  variant="outline"
                  size="sm"
                  className="gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy Token
                    </>
                  )}
                </Button>
              )}
            </div>

            {isLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            ) : !isSignedIn ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground text-lg">
                  You need to be signed in to view the JWT token.
                </p>
              </div>
            ) : accessToken ? (
              <div className="relative">
                <div className="bg-background border rounded-lg p-4 pr-12 overflow-auto">
                  <code className="text-sm break-all whitespace-pre-wrap font-mono">
                    {accessToken}
                  </code>
                </div>
                <Button
                  onClick={handleCopy}
                  variant="ghost"
                  size="icon"
                  className="absolute top-2 right-2 h-8 w-8"
                  title="Copy to clipboard"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground text-lg">
                  No JWT token available.
                </p>
              </div>
            )}

            <div className="mt-8 space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">About JWT Token</h3>
                <p className="text-sm text-muted-foreground">
                  This is your JSON Web Token (JWT) access token. It contains
                  encoded information about your authentication session and is
                  used to authorize API requests. Keep this token secure and do
                  not share it publicly.
                </p>
              </div>
              <div className="bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
                  ⚠️ Security Warning
                </p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  Never share your JWT token with untrusted parties or expose it
                  in client-side code where it can be accessed by malicious
                  actors.
                </p>
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
