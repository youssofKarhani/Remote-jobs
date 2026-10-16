"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { profileApi } from "@/lib/api";
import { Loader2, Plus, Edit2, Trash2 } from "lucide-react";

// ---------------------------------------------------------------------------
// Add Bullet Dialog
// ---------------------------------------------------------------------------
export function AddBulletDialog({
  experienceId,
  isOpen,
  onClose,
  onSuccess,
}: {
  experienceId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || !experienceId) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await profileApi.addEvidence({
        experience_record_id: experienceId,
        raw_text: text.trim(),
        is_verified: true,
      });
      setText("");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to add evidence bullet");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[500px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Add Achievement Bullet</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Add a concrete, quantifiable achievement bullet to this experience record.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g., Architected automated PostgreSQL failover using Patroni, reducing unplanned downtime from 45 min to under 15 seconds."
            className="text-xs min-h-[90px] bg-zinc-900 border-zinc-800"
            required
          />
          <DialogFooter className="gap-2 sm:gap-0">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Add Bullet"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Edit Bullet Dialog
// ---------------------------------------------------------------------------
export function EditBulletDialog({
  bullet,
  isOpen,
  onClose,
  onSuccess,
}: {
  bullet: { id: string; raw_text: string } | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [text, setText] = useState(bullet?.raw_text || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (bullet) setText(bullet.raw_text);
  }, [bullet]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || !bullet) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await profileApi.updateEvidence(bullet.id, {
        raw_text: text.trim(),
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to update evidence bullet");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[500px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Edit Evidence Bullet</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Update the bullet content while preserving stable ID provenance.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="text-xs min-h-[90px] bg-zinc-900 border-zinc-800"
            required
          />
          <DialogFooter className="gap-2 sm:gap-0">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save Changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Add Experience Dialog
// ---------------------------------------------------------------------------
export function AddExperienceDialog({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [form, setForm] = useState({
    company_name: "",
    role_title: "",
    location: "Remote",
    start_date: "2023-01",
    end_date: "",
    is_current: true,
    description: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.company_name || !form.role_title) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await profileApi.createExperience({
        company_name: form.company_name,
        role_title: form.role_title,
        location: form.location,
        start_date: form.start_date,
        end_date: form.is_current ? undefined : form.end_date,
        is_current: form.is_current,
        description: form.description,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to create experience record");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[500px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Add Work Experience Record</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Create a new role entry in your canonical career timeline.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Job Title / Role</label>
            <Input
              value={form.role_title}
              onChange={(e) => setForm({ ...form, role_title: e.target.value })}
              placeholder="e.g. Senior Backend Engineer"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Company Name</label>
            <Input
              value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })}
              placeholder="e.g. Acme Cloud Systems"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <label className="text-[11px] font-mono text-zinc-400">Location</label>
              <Input
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                placeholder="e.g. Berlin / Remote"
                className="text-xs bg-zinc-900 border-zinc-800"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[11px] font-mono text-zinc-400">Start Date</label>
              <Input
                value={form.start_date}
                onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                placeholder="YYYY-MM (e.g. 2022-03)"
                className="text-xs bg-zinc-900 border-zinc-800"
                required
              />
            </div>
          </div>
          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save Role"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Add Skill Dialog
// ---------------------------------------------------------------------------
export function AddSkillDialog({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("technical");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await profileApi.createSkill({
        name: name.trim(),
        category,
        is_verified: true,
      });
      setName("");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to add skill");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[420px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Add Technical Skill</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Index a new technical or domain skill with stable ID provenance.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Skill Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Kubernetes, Golang, GraphQL"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Add Skill"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Add Project Dialog
// ---------------------------------------------------------------------------
export function AddProjectDialog({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [techStr, setTechStr] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const technologies = techStr
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      await profileApi.createProject({
        title: title.trim(),
        description: description.trim(),
        technologies,
        is_verified: true,
      });
      setTitle("");
      setDescription("");
      setTechStr("");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to add project");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[480px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Add Technical Project</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Document key projects, open-source work, or architectures.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Project Title</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Distributed Task Queue Engine"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Technologies (comma separated)</label>
            <Input
              value={techStr}
              onChange={(e) => setTechStr(e.target.value)}
              placeholder="e.g. Python, Redis, Docker, FastAPI"
              className="text-xs bg-zinc-900 border-zinc-800"
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Description</label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="High-throughput distributed task runner handling 25,000 tasks/second with sliding-window rate limiting."
              className="text-xs min-h-[80px] bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save Project"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Add Education Dialog
// ---------------------------------------------------------------------------
export function AddEducationDialog({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [institution, setInstitution] = useState("");
  const [degree, setDegree] = useState("");
  const [fieldOfStudy, setFieldOfStudy] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!institution || !degree) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await profileApi.createEducation({
        institution: institution.trim(),
        degree: degree.trim(),
        field_of_study: fieldOfStudy.trim(),
        is_verified: true,
      });
      setInstitution("");
      setDegree("");
      setFieldOfStudy("");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to add education");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[450px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Add Academic Credential</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Document your degree, institution, and major.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Degree</label>
            <Input
              value={degree}
              onChange={(e) => setDegree(e.target.value)}
              placeholder="e.g. B.S. or M.S."
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Field of Study</label>
            <Input
              value={fieldOfStudy}
              onChange={(e) => setFieldOfStudy(e.target.value)}
              placeholder="e.g. Computer Science & Software Engineering"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Institution</label>
            <Input
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="e.g. Technical University of Munich"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save Education"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Add Certification Dialog
// ---------------------------------------------------------------------------
export function AddCertificationDialog({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [name, setName] = useState("");
  const [org, setOrg] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !org) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await profileApi.createCertification({
        name: name.trim(),
        issuing_organization: org.trim(),
        is_verified: true,
      });
      setName("");
      setOrg("");
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to add certification");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[450px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base text-zinc-100">Add Professional Certification</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Document cloud provider or industry certifications.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          {error && <div className="text-xs text-red-400">{error}</div>}
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Certification Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. AWS Certified Solutions Architect - Professional"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-mono text-zinc-400">Issuing Organization</label>
            <Input
              value={org}
              onChange={(e) => setOrg(e.target.value)}
              placeholder="e.g. Amazon Web Services"
              className="text-xs bg-zinc-900 border-zinc-800"
              required
            />
          </div>
          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-zinc-800 text-xs">
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-violet-600 hover:bg-violet-500 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save Certification"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
