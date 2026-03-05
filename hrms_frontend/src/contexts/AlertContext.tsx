import React, { createContext, useContext, useState, useCallback } from "react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { CheckCircle2, XCircle, Info } from "lucide-react";

type AlertVariant = "default" | "destructive" | "success";

interface AlertMessage {
  id: string;
  title?: string;
  message: string;
  variant: AlertVariant;
}

interface AlertContextType {
  showAlert: (params: {
    title?: string;
    message: string;
    variant?: AlertVariant;
  }) => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export function AlertProvider({ children }: { children: React.ReactNode }) {
  const [alerts, setAlerts] = useState<AlertMessage[]>([]);

  const showAlert = useCallback(
    ({
      title,
      message,
      variant = "default",
    }: {
      title?: string;
      message: string;
      variant?: AlertVariant;
    }) => {
      const id = Math.random().toString(36).substring(7);
      const newAlert: AlertMessage = { id, title, message, variant };

      setAlerts((prev) => [...prev, newAlert]);

      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        setAlerts((prev) => prev.filter((alert) => alert.id !== id));
      }, 5000);
    },
    []
  );

  const getIcon = (variant: AlertVariant) => {
    switch (variant) {
      case "success":
        return <CheckCircle2 className="text-green-600" />;
      case "destructive":
        return <XCircle />;
      default:
        return <Info />;
    }
  };

  return (
    <AlertContext.Provider value={{ showAlert }}>
      {children}
      {/* Alert Portal */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-96 max-w-[calc(100vw-2rem)]">
        {alerts.map((alert) => (
          <Alert
            key={alert.id}
            variant={alert.variant === "success" ? "default" : alert.variant}
            className={
              alert.variant === "success"
                ? "border-green-600 bg-green-50 text-green-900"
                : ""
            }
          >
            {getIcon(alert.variant)}
            {alert.title && <AlertTitle>{alert.title}</AlertTitle>}
            <AlertDescription>{alert.message}</AlertDescription>
          </Alert>
        ))}
      </div>
    </AlertContext.Provider>
  );
}

export function useAlert() {
  const context = useContext(AlertContext);
  if (context === undefined) {
    throw new Error("useAlert must be used within an AlertProvider");
  }
  return context;
}
