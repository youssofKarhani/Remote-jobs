"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth-context";
import { LogIn, UserPlus, Sparkles, AlertCircle, Loader2 } from "lucide-react";

interface AuthDialogProps {
  children?: React.ReactNode;
  defaultTab?: "login" | "register";
}

export function AuthDialog({ children, defaultTab = "login" }: AuthDialogProps) {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<"login" | "register">(defaultTab);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, register, loginAsDemo } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      setOpen(false);
    } catch (err: any) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register(email, password, fullName);
      setOpen(false);
    } catch (err: any) {
      setError(err.message || "Registration failed. Please check the form.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoLogin = async () => {
    setError(null);
    setIsSubmitting(true);
    try {
      await loginAsDemo();
      setOpen(false);
    } catch (err: any) {
      setError(err.message || "Could not log into demo account.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button size="sm" variant="default" className="text-xs gap-1.5 bg-blue-600 hover:bg-blue-500 text-white">
            <LogIn className="h-3.5 w-3.5" />
            Sign In
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md bg-zinc-950 border-zinc-800 text-zinc-100">
        <DialogHeader className="space-y-1.5 text-left">
          <DialogTitle className="text-xl font-bold tracking-tight text-zinc-100">
            {tab === "login" ? "Welcome Back" : "Create Candidate Account"}
          </DialogTitle>
          <DialogDescription className="text-zinc-400 text-xs">
            Authenticate to sync external jobs, manage your verified Evidence Bank, and customize deterministic filters.
          </DialogDescription>
        </DialogHeader>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-800/50 flex items-center gap-2 text-red-300 text-xs">
            <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <Tabs value={tab} onValueChange={(val) => setTab(val as "login" | "register")} className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="login" className="text-xs">
              Sign In
            </TabsTrigger>
            <TabsTrigger value="register" className="text-xs">
              Register
            </TabsTrigger>
          </TabsList>

          <TabsContent value="login" className="space-y-4 pt-4">
            <form onSubmit={handleLogin} className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-zinc-300">Email Address</label>
                <Input
                  type="email"
                  placeholder="candidate@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-zinc-900 border-zinc-800 text-xs"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-zinc-300">Password</label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-zinc-900 border-zinc-800 text-xs"
                />
              </div>
              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full text-xs font-semibold bg-blue-600 hover:bg-blue-500 gap-2 text-white"
              >
                {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <LogIn className="h-3.5 w-3.5" />}
                Sign In
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="register" className="space-y-4 pt-4">
            <form onSubmit={handleRegister} className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-zinc-300">Full Name</label>
                <Input
                  type="text"
                  placeholder="e.g. Alex Morgan"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="bg-zinc-900 border-zinc-800 text-xs"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-zinc-300">Email Address</label>
                <Input
                  type="email"
                  placeholder="alex@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-zinc-900 border-zinc-800 text-xs"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-zinc-300">Password (min 6 chars)</label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-zinc-900 border-zinc-800 text-xs"
                />
              </div>
              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 gap-2 text-white"
              >
                {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <UserPlus className="h-3.5 w-3.5" />}
                Create Account
              </Button>
              <p className="text-[11px] text-zinc-400 text-center pt-1 leading-normal">
                By registering, you agree to our{" "}
                <Link href="/terms" onClick={() => setOpen(false)} className="text-violet-400 hover:underline">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" onClick={() => setOpen(false)} className="text-violet-400 hover:underline">
                  Privacy Policy
                </Link>.
              </p>
            </form>
          </TabsContent>
        </Tabs>

        <div className="relative my-2">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-zinc-800" />
          </div>
          <div className="relative flex justify-center text-[10px] uppercase">
            <span className="bg-zinc-950 px-2 text-zinc-500 font-mono">Or quick exploration</span>
          </div>
        </div>

        <Button
          type="button"
          variant="outline"
          onClick={handleDemoLogin}
          disabled={isSubmitting}
          className="w-full border-blue-800/40 bg-blue-950/30 hover:bg-blue-900/40 text-blue-300 text-xs gap-2 font-mono"
        >
          {isSubmitting ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-400" />
          ) : (
            <Sparkles className="h-3.5 w-3.5 text-blue-400" />
          )}
          One-Click Demo Candidate Mode
        </Button>
      </DialogContent>
    </Dialog>
  );
}
