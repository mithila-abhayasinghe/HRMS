import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import {
  Outlet,
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { AsgardeoProvider } from "@asgardeo/react";

import "./styles.css";
import reportWebVitals from "./reportWebVitals.ts";
import { AlertProvider } from "./contexts/AlertContext.tsx";

import App from "./App.tsx";
import LoginPage from "./pages/login.tsx";
import ErrorRoutePage from "./pages/error-route.tsx";
import NotFoundPage from "./pages/404.tsx";
import ProfilePage from "./pages/profile.tsx";
import JWTTokenPage from "./pages/jwt-token.tsx";
import RouterErrorComponent from "./components/router-error.tsx";

const rootRoute = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
  notFoundComponent: NotFoundPage,
  errorComponent: RouterErrorComponent,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: App,
  errorComponent: RouterErrorComponent,
  beforeLoad: () => {
    document.title = "HRMS - Home";
  },
});

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/login",
  component: LoginPage,
  errorComponent: RouterErrorComponent,
  beforeLoad: () => {
    document.title = "Login - HRMS";
  },
});

const errorRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/error",
  component: ErrorRoutePage,
  beforeLoad: () => {
    document.title = "Error - HRMS";
  },
});

const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/profile",
  component: ProfilePage,
  errorComponent: RouterErrorComponent,
  beforeLoad: () => {
    document.title = "Profile - HRMS";
  },
});

const jwtTokenRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/jwt-token",
  component: JWTTokenPage,
  errorComponent: RouterErrorComponent,
  beforeLoad: () => {
    document.title = "JWT Token - HRMS";
  },
});

const notFoundRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "*",
  component: NotFoundPage,
  beforeLoad: () => {
    document.title = "404 Not Found - HRMS";
  },
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  errorRoute,
  profileRoute,
  jwtTokenRoute,
  notFoundRoute,
]);

const router = createRouter({
  routeTree,
  context: {},
  defaultPreload: "intent",
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,
  defaultNotFoundComponent: NotFoundPage,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const rootElement = document.getElementById("app");
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <AsgardeoProvider
        clientId={import.meta.env.VITE_CLIENT_ID || ""}
        baseUrl={import.meta.env.VITE_ORG_BASE_URL || ""}
      >
        <AlertProvider>
          <RouterProvider router={router} />
        </AlertProvider>
      </AsgardeoProvider>
    </StrictMode>,
  );
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
