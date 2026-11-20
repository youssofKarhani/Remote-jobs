"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Download, Loader2, Trash2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

/** "Your data" controls promised by the privacy policy: download a copy, or delete the account. */
export function AccountDataCard() {
  const router = useRouter();
  const { logout } = useAuth();
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);
    try {
      const { blob, filename } = await authApi.exportMyData();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "Export failed. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await authApi.deleteMyAccount(password);
      setDeleteOpen(false);
      logout();
      router.push("/?account=deleted");
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Deletion failed. Please try again.");
      setIsDeleting(false);
    }
  };

  return (
    <Card className="border-zinc-800 bg-zinc-950/60">
      <CardHeader>
        <CardTitle className="text-base">Your data</CardTitle>
        <CardDescription>
          Download a copy of everything we store about you, or delete your account and all of its data.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {exportError && (
          <p role="alert" className="flex items-center gap-2 text-xs text-red-300">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {exportError}
          </p>
        )}
        <div className="flex flex-col sm:flex-row gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleExport}
            disabled={isExporting}
            className="border-zinc-700 bg-zinc-900/60 text-zinc-200 text-xs gap-1.5"
          >
            {isExporting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
            Download my data
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setPassword("");
              setDeleteError(null);
              setDeleteOpen(true);
            }}
            className="border-red-900/60 bg-red-950/20 text-red-300 hover:bg-red-950/40 text-xs gap-1.5"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete account
          </Button>
        </div>
      </CardContent>

      <Dialog open={deleteOpen} onOpenChange={(open) => !isDeleting && setDeleteOpen(open)}>
        <DialogContent className="sm:max-w-md bg-zinc-950 border-zinc-800 text-zinc-100">
          <DialogHeader className="text-left space-y-1.5">
            <DialogTitle>Delete your account?</DialogTitle>
            <DialogDescription className="text-zinc-400 text-xs leading-relaxed">
              This permanently deletes your profile, CV records, preferences, matches, generated documents,
              cover letters and applications. It can&apos;t be undone. Download your data first if you want a copy.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleDelete} className="space-y-3">
            <div className="space-y-1">
              <label htmlFor="delete-account-password" className="text-xs font-medium text-zinc-300">
                Enter your password to confirm
              </label>
              <Input
                id="delete-account-password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-zinc-900 border-zinc-800 text-xs"
              />
            </div>
            {deleteError && (
              <p role="alert" className="flex items-center gap-2 text-xs text-red-300">
                <AlertCircle className="h-4 w-4 shrink-0" />
                {deleteError}
              </p>
            )}
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                disabled={isDeleting}
                onClick={() => setDeleteOpen(false)}
                className="text-xs text-zinc-400"
              >
                Keep my account
              </Button>
              <Button
                type="submit"
                disabled={isDeleting || !password}
                className="bg-red-600 hover:bg-red-500 text-white text-xs gap-1.5"
              >
                {isDeleting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
                Delete permanently
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
