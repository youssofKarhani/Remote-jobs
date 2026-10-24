"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { LogOut, User } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { vcopy } from "@/lib/verification-copy";

export interface SignOutDialogProps {
  children?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onConfirm?: () => void;
}

export function SignOutDialog({
  children,
  open: controlledOpen,
  onOpenChange: setControlledOpen,
  onConfirm,
}: SignOutDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;

  const setOpen = (next: boolean) => {
    if (isControlled) {
      setControlledOpen?.(next);
    } else {
      setInternalOpen(next);
    }
  };

  const { user, logout } = useAuth();

  const handleConfirm = () => {
    logout();
    onConfirm?.();
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {children && <DialogTrigger asChild>{children}</DialogTrigger>}
      <DialogContent className="sm:max-w-md bg-zinc-950 border-zinc-800 text-zinc-100">
        <DialogHeader className="space-y-3 text-left">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 shrink-0">
              <LogOut className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-zinc-100">
                Confirm Sign Out
              </DialogTitle>
              <DialogDescription className="text-xs text-zinc-400 mt-0.5">
                Are you sure you want to end your current session?
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {user && (
          <div className="p-3 rounded-lg bg-zinc-900/70 border border-zinc-800/80 flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400 shrink-0">
              <User className="h-4 w-4" />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-semibold text-zinc-200 truncate">
                {user.full_name || "Active Candidate"}
              </span>
              <span className="text-[11px] text-zinc-400 font-mono truncate">
                {user.email}
              </span>
            </div>
          </div>
        )}

        <p className="text-xs text-zinc-400 leading-relaxed">
          {vcopy("signOut.dialogDescription")}
        </p>

        <DialogFooter className="gap-2 sm:gap-2 pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setOpen(false)}
            className="border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 text-xs"
          >
            Cancel
          </Button>
          <Button
            type="button"
            size="sm"
            onClick={handleConfirm}
            className="bg-red-600 hover:bg-red-500 text-white text-xs gap-1.5 shadow-sm shadow-red-900/20"
          >
            <LogOut className="h-3.5 w-3.5" />
            Yes, Sign Out
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
