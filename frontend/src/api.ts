const BASE = "/api";

function getInitData(): string {
  try {
    return window.Telegram?.WebApp?.initData || "";
  } catch {
    return "";
  }
}

export async function apiFetch<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(BASE + path, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v) url.searchParams.set(k, v);
    });
  }

  const res = await fetch(url.toString(), {
    headers: {
      "X-Telegram-Init-Data": getInitData(),
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        initDataUnsafe: {
          user?: { id: number; first_name: string };
        };
        ready: () => void;
        expand: () => void;
        setHeaderColor: (color: string) => void;
        setBackgroundColor: (color: string) => void;
        themeParams: Record<string, string>;
      };
    };
  }
}
