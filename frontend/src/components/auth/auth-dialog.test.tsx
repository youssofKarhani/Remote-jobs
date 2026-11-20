import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthDialog } from "./auth-dialog";

const login = vi.fn();
const register = vi.fn();

vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({ login, register, loginAsDemo: vi.fn(), logout: vi.fn() }),
}));

describe("AuthDialog", () => {
  beforeEach(() => {
    login.mockReset();
    register.mockReset();
  });

  it("opens on the sign-in tab and switches to registration", async () => {
    const user = userEvent.setup();
    render(<AuthDialog />);

    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(screen.getByRole("heading", { name: "Welcome Back" })).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: "Register" }));
    expect(screen.getByRole("heading", { name: "Create Candidate Account" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("e.g. Alex Morgan")).toBeInTheDocument();
  });

  it("submits credentials and shows the server's error message on failure", async () => {
    login.mockRejectedValue(new Error("API Error [401]: Incorrect email or password"));
    const user = userEvent.setup();
    render(<AuthDialog />);

    await user.click(screen.getByRole("button", { name: /sign in/i }));
    await user.type(screen.getByPlaceholderText("candidate@example.com"), "someone@example.com");
    await user.type(screen.getByPlaceholderText("••••••••"), "wrong-password");
    await user.click(screen.getAllByRole("button", { name: /^sign in$/i }).at(-1)!);

    expect(login).toHaveBeenCalledWith("someone@example.com", "wrong-password");
    expect(await screen.findByText(/Incorrect email or password/)).toBeInTheDocument();
  });
});
