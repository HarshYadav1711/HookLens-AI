/** Normalize FastAPI / fetch error payloads into a single user-facing string. */
export function formatApiErrorDetail(detail: unknown): string {
  if (detail == null) return "Request failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: string }).msg);
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }
  if (typeof detail === "object" && "message" in detail) {
    return String((detail as { message: string }).message);
  }
  return String(detail);
}

export function isNetworkError(err: unknown): boolean {
  return (
    err instanceof TypeError &&
    (err.message === "Failed to fetch" || err.message.includes("NetworkError"))
  );
}

export function friendlyErrorMessage(err: unknown, fallback: string): string {
  if (isNetworkError(err)) {
    return "Cannot reach the API. Confirm the backend is running and NEXT_PUBLIC_API_URL is correct.";
  }
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}
