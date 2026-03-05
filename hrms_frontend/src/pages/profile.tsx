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

interface BasicUserInfo {
  email?: string;
  username?: string;
  displayName?: string;
  allowedScopes?: string;
  tenantDomain?: string;
  sessionState?: string;
  sub?: string;
  preferred_username?: string;
  org_id?: string;
  org_name?: string;
}

export default function ProfilePage() {
  const { getDecodedIdToken, isSignedIn, getAccessToken } = useAsgardeo();
  const [userInfo, setUserInfo] = useState<BasicUserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authStatus, setAuthStatus] = useState<
    "checking" | "active" | "inactive"
  >("checking");
  const [isMounted, setIsMounted] = useState(false);

  console.log("Access Token:", getAccessToken());

  // Ensure component is mounted before rendering dynamic content
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Fetch user information from decoded ID token
  useEffect(() => {
    if (!isMounted) return;

    const fetchUserInfo = async () => {
      if (!isSignedIn) {
        setIsLoading(false);
        setAuthStatus("inactive");
        return;
      }

      try {
        setIsLoading(true);
        const decodedToken = await getDecodedIdToken();

        // Extract basic user info from decoded token
        const basicInfo: BasicUserInfo = {
          email: decodedToken?.email as string,
          username: decodedToken?.username as string,
          displayName:
            (decodedToken?.preferred_username as string) ||
            (decodedToken?.sub as string),
          allowedScopes: decodedToken?.scope as string,
          tenantDomain: decodedToken?.tenant_domain as string,
          sessionState: decodedToken?.session_state as string,
          sub: decodedToken?.sub as string,
          preferred_username: decodedToken?.preferred_username as string,
          org_id: decodedToken?.org_id as string,
          org_name: decodedToken?.org_name as string,
        };

        setUserInfo(basicInfo);
        setAuthStatus("active");
      } catch (error) {
        console.error("Error fetching user info:", error);
        setAuthStatus("inactive");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMounted, isSignedIn]);

  // Helper to safely display values
  const displayValue = (
    value: string | undefined,
    fallback = "Not available",
  ) => {
    return value && value.trim() !== "" ? value : fallback;
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
                    <BreadcrumbPage>Profile</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
            <div className="grid auto-rows-min gap-4 md:grid-cols-3">
              <div className="bg-muted/50 aspect-video rounded-xl p-6 flex flex-col justify-center">
                <div className="h-6 w-32 mb-2">
                  <Skeleton className="h-full w-full" />
                </div>
                <div className="h-4 w-full">
                  <Skeleton className="h-full w-full" />
                </div>
              </div>
              <div className="bg-muted/50 aspect-video rounded-xl p-6 flex flex-col justify-center">
                <div className="h-6 w-32 mb-2">
                  <Skeleton className="h-full w-full" />
                </div>
                <div className="h-4 w-full">
                  <Skeleton className="h-full w-full" />
                </div>
              </div>
              <div className="bg-muted/50 aspect-video rounded-xl p-6 flex flex-col justify-center">
                <div className="h-6 w-32 mb-2">
                  <Skeleton className="h-full w-full" />
                </div>
                <div className="h-4 w-full">
                  <Skeleton className="h-full w-full" />
                </div>
              </div>
            </div>
            <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min p-6">
              <div className="h-8 w-48 mb-6">
                <Skeleton className="h-full w-full" />
              </div>
              <div className="space-y-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-6 w-full" />
                  </div>
                ))}
              </div>
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
                  <BreadcrumbPage>Profile</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="grid auto-rows-min gap-4 md:grid-cols-3">
            <div className="bg-muted/50 aspect-video rounded-xl p-6 flex flex-col justify-center">
              <h3 className="font-semibold mb-2">Welcome Back!</h3>
              {isLoading ? (
                <Skeleton className="h-4 w-full" />
              ) : (
                <p className="text-sm text-muted-foreground">
                  {userInfo?.displayName
                    ? `Hello, ${userInfo.displayName}!`
                    : "You're successfully logged in with Asgardeo."}
                </p>
              )}
            </div>
            <div className="bg-muted/50 aspect-video rounded-xl p-6 flex flex-col justify-center">
              <h3 className="font-semibold mb-2">Profile Status</h3>
              <div className="flex items-center gap-2">
                <div
                  className={`h-2 w-2 rounded-full ${
                    authStatus === "active"
                      ? "bg-green-500"
                      : authStatus === "inactive"
                        ? "bg-red-500"
                        : "bg-yellow-500"
                  }`}
                />
                <p className="text-sm text-muted-foreground">
                  Authentication:{" "}
                  {authStatus === "checking"
                    ? "Checking..."
                    : authStatus === "active"
                      ? "Active"
                      : "Inactive"}
                </p>
              </div>
            </div>
            <div className="bg-muted/50 aspect-video rounded-xl p-6 flex flex-col justify-center">
              <h3 className="font-semibold mb-2">Quick Actions</h3>
              <p className="text-sm text-muted-foreground">
                Manage your account settings and preferences.
              </p>
            </div>
          </div>
          <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min p-6">
            <h2 className="text-2xl font-bold mb-6">User Information</h2>
            {isLoading ? (
              <div className="space-y-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i}>
                    <Skeleton className="h-4 w-32 mb-2" />
                    <Skeleton className="h-6 w-full" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Display Name
                    </label>
                    <p className="text-lg mt-1">
                      {displayValue(userInfo?.displayName)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Username
                    </label>
                    <p className="text-lg mt-1">
                      {displayValue(userInfo?.username)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Email
                    </label>
                    <p className="text-lg mt-1">
                      {displayValue(userInfo?.email)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Subject (Sub)
                    </label>
                    <p className="text-lg mt-1 break-all">
                      {displayValue(userInfo?.sub)}
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Tenant Domain
                    </label>
                    <p className="text-lg mt-1">
                      {displayValue(userInfo?.tenantDomain)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Organization ID
                    </label>
                    <p className="text-lg mt-1 break-all">
                      {displayValue(userInfo?.org_id)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Organization Name
                    </label>
                    <p className="text-lg mt-1">
                      {displayValue(userInfo?.org_name)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Session State
                    </label>
                    <p className="text-lg mt-1 break-all">
                      {displayValue(userInfo?.sessionState)}
                    </p>
                  </div>
                </div>
                <div className="md:col-span-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Allowed Scopes
                  </label>
                  <p className="text-lg mt-1 break-words">
                    {displayValue(userInfo?.allowedScopes)}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
