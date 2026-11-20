import { beforeEach, describe, expect, it, vi } from "vitest";
import { clearAuthToken, fetchApi, getAuthToken, setAuthToken } from "./api";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    statusText: status === 200 ? "OK" : "Error",
    headers: { "Content-Type": "application/json" },
  });
}

describe("auth token storage", () => {
  it("stores, reads and clears the token", () => {
    expect(getAuthToken()).toBeNull();
    setAuthToken("abc");
    expect(getAuthToken()).toBe("abc");
    clearAuthToken();
    expect(getAuthToken()).toBeNull();
  });
});

describe("fetchApi", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("sends the stored token as a Bearer header", async () => {
    setAuthToken("stored-token");
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }));

    await fetchApi("/api/v1/auth/me");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer stored-token");
  });

  it("sends no Authorization header when token is explicitly null", async () => {
    setAuthToken("stored-token");
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }));

    await fetchApi("/api/v1/cv/preview-text", { method: "POST", token: null });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBeUndefined();
  });

  it("sets JSON content type for JSON bodies but not for file uploads", async () => {
    fetchMock.mockImplementation(async () => jsonResponse({ ok: true }));

    await fetchApi("/x", { method: "POST", body: JSON.stringify({ a: 1 }) });
    await fetchApi("/y", { method: "POST", body: new FormData() });

    expect(fetchMock.mock.calls[0][1].headers["Content-Type"]).toBe("application/json");
    expect(fetchMock.mock.calls[1][1].headers["Content-Type"]).toBeUndefined();
  });

  it("returns the parsed JSON body on success", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ id: 7, name: "Ada" }));
    await expect(fetchApi<{ id: number }>("/thing")).resolves.toEqual({ id: 7, name: "Ada" });
  });

  it("throws with the status and the server's detail message", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: "Incorrect email or password" }, 401));
    await expect(fetchApi("/api/v1/auth/login/json")).rejects.toThrow(
      "API Error [401]: Incorrect email or password"
    );
  });

  it("falls back to the status text when the error body isn't JSON", async () => {
    fetchMock.mockResolvedValue(new Response("<html>bad gateway</html>", { status: 502, statusText: "Bad Gateway" }));
    await expect(fetchApi("/thing")).rejects.toThrow("API Error [502]: Bad Gateway");
  });
});
