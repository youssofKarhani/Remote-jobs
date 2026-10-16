"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Check,
  ShieldCheck,
  Plus,
  ExternalLink,
  Calendar,
  MapPin,
  Briefcase,
  CheckCircle2,
  RefreshCw,
  Loader2,
  Sparkles,
  FileUp,
  Database,
  AlertCircle,
  Edit2,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { profileApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { AuthDialog } from "@/components/auth/auth-dialog";
import {
  AddBulletDialog,
  EditBulletDialog,
  AddExperienceDialog,
  AddSkillDialog,
  AddProjectDialog,
  AddEducationDialog,
  AddCertificationDialog,
} from "@/components/profile/profile-dialogs";

export default function ProfilePage() {
  const { isAuthenticated, loginAsDemo } = useAuth();
  const [activeTab, setActiveTab] = useState("experience");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isEditingHeader, setIsEditingHeader] = useState(false);

  // Profile metadata
  const [profile, setProfile] = useState({
    full_name: "",
    headline: "",
    location: "",
    summary: "",
  });

  // Evidence Bank Collections
  const [experiences, setExperiences] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [education, setEducation] = useState<any[]>([]);
  const [certifications, setCertifications] = useState<any[]>([]);

  // Dialog States
  const [activeExpIdForBullet, setActiveExpIdForBullet] = useState<string | null>(null);
  const [bulletToEdit, setBulletToEdit] = useState<{ id: string; raw_text: string } | null>(null);
  const [showAddExperience, setShowAddExperience] = useState(false);
  const [showAddSkill, setShowAddSkill] = useState(false);
  const [showAddProject, setShowAddProject] = useState(false);
  const [showAddEducation, setShowAddEducation] = useState(false);
  const [showAddCertification, setShowAddCertification] = useState(false);

  const loadData = useCallback(async () => {
    if (!isAuthenticated) {
      setProfile({ full_name: "", headline: "", location: "", summary: "" });
      setExperiences([]);
      setSkills([]);
      setProjects([]);
      setEducation([]);
      setCertifications([]);
      return;
    }
    setIsLoading(true);
    try {
      const res = await profileApi.getProfile();
      if (res) {
        setProfile({
          full_name: res.full_name || "",
          headline: res.headline || "",
          location: res.location || "",
          summary: res.summary || "",
        });

        if (res.evidence_bank) {
          setExperiences(res.evidence_bank.experiences || []);
          setSkills(res.evidence_bank.skills || []);
          setProjects(res.evidence_bank.projects || []);
          setEducation(res.evidence_bank.education || []);
          setCertifications(res.evidence_bank.certifications || []);
        }
      }
    } catch (err: any) {
      console.log("No stored profile loaded from API yet:", err?.message);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleToggleVerifyBullet = async (expId: string, stableId: string, currentStatus: boolean) => {
    const nextStatus = !currentStatus;
    setExperiences((prev) =>
      prev.map((exp) => ({
        ...exp,
        bullets: exp.bullets?.map((b: any) =>
          b.stable_id === stableId ? { ...b, is_verified: nextStatus } : b
        ),
      }))
    );

    try {
      await profileApi.verifyEvidence(stableId, "experience_bullet", nextStatus);
    } catch (err) {
      console.warn("Backend verify sync offline, updated local state.");
    }
  };

  const handleToggleVerifySkill = async (stableId: string, currentStatus: boolean) => {
    const nextStatus = !currentStatus;
    setSkills((prev) =>
      prev.map((s) => (s.stable_id === stableId ? { ...s, is_verified: nextStatus } : s))
    );

    try {
      await profileApi.verifyEvidence(stableId, "skill", nextStatus);
    } catch (err) {
      console.warn("Backend verify sync offline, updated local state.");
    }
  };

  const handleDeleteEvidence = async (id: string) => {
    try {
      await profileApi.deleteEvidence(id);
      loadData();
    } catch (err) {
      console.error("Delete evidence error:", err);
    }
  };

  const handleDeleteExperience = async (id: string) => {
    try {
      await profileApi.deleteExperience(id);
      loadData();
    } catch (err) {
      console.error("Delete experience error:", err);
    }
  };

  const handleDeleteSkill = async (id: string) => {
    try {
      await profileApi.deleteSkill(id);
      loadData();
    } catch (err) {
      console.error("Delete skill error:", err);
    }
  };

  const handleDeleteProject = async (id: string) => {
    try {
      await profileApi.deleteProject(id);
      loadData();
    } catch (err) {
      console.error("Delete project error:", err);
    }
  };

  const handleDeleteEducation = async (id: string) => {
    try {
      await profileApi.deleteEducation(id);
      loadData();
    } catch (err) {
      console.error("Delete education error:", err);
    }
  };

  const handleDeleteCertification = async (id: string) => {
    try {
      await profileApi.deleteCertification(id);
      loadData();
    } catch (err) {
      console.error("Delete certification error:", err);
    }
  };

  const handleVerifyAll = async () => {
    setExperiences((prev) =>
      prev.map((exp) => ({
        ...exp,
        bullets: exp.bullets?.map((b: any) => ({ ...b, is_verified: true })),
      }))
    );
    setSkills((prev) => prev.map((s) => ({ ...s, is_verified: true })));
    setProjects((prev) => prev.map((p) => ({ ...p, is_verified: true })));
    setEducation((prev) => prev.map((e) => ({ ...e, is_verified: true })));
    setCertifications((prev) => prev.map((c) => ({ ...c, is_verified: true })));

    try {
      await profileApi.verifyAll();
    } catch (err) {
      console.warn("Verify-all sync error, updated local state.");
    }
  };

  const handleSaveHeader = async () => {
    setIsSaving(true);
    try {
      await profileApi.updateProfile({
        full_name: profile.full_name,
        headline: profile.headline,
        location: profile.location,
        summary: profile.summary,
      });
      setIsEditingHeader(false);
    } catch (err) {
      console.warn("Save profile offline, updated local state.");
      setIsEditingHeader(false);
    } finally {
      setIsSaving(false);
    }
  };

  const totalBullets = experiences.reduce((acc, exp) => acc + (exp.bullets?.length || 0), 0);
  const totalItems = totalBullets + skills.length + projects.length + education.length + certifications.length;
  const verifiedBullets = experiences.reduce(
    (acc, exp) => acc + (exp.bullets?.filter((b: any) => b.is_verified).length || 0),
    0
  );
  const verifiedItems =
    verifiedBullets +
    skills.filter((s) => s.is_verified).length +
    projects.filter((p) => p.is_verified).length +
    education.filter((e) => e.is_verified).length +
    certifications.filter((c) => c.is_verified).length;

  const percentVerified = totalItems > 0 ? Math.round((verifiedItems / totalItems) * 100) : 0;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Candidate Evidence Bank"
        subtitle="Manage your canonical profile and immutable evidence items (stable IDs) used for deterministic CV rendering."
      >
        <div className="flex items-center gap-3">
          {totalItems > 0 && (
            <Button size="sm" variant="outline" onClick={handleVerifyAll} className="gap-1.5 text-xs border-zinc-800 bg-zinc-900 text-zinc-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              Verify All Evidence
            </Button>
          )}
          <Badge variant="success" className="gap-1.5 py-1 px-3 text-xs bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
            <ShieldCheck className="h-4 w-4" />
            {percentVerified}% Verified ({verifiedItems}/{totalItems})
          </Badge>
        </div>
      </PageHeader>

      {!isAuthenticated && (
        <Card className="p-8 text-center glass-card border-dashed border-zinc-800 bg-zinc-950/40 space-y-4">
          <div className="h-10 w-10 rounded-xl bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400 mx-auto">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-zinc-200">Sign in to Access Your Evidence Bank</h3>
            <p className="text-xs text-zinc-400 max-w-md mx-auto">
              Your canonical Candidate Evidence Bank stores immutable, verified experience bullets, skills, and projects with stable IDs. Sign in or initialize a demo candidate profile to view and verify evidence.
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Button size="sm" onClick={loginAsDemo} className="text-xs gap-1.5 bg-violet-600 hover:bg-violet-500 text-white">
              <Sparkles className="h-3.5 w-3.5" />
              One-Click Demo Mode
            </Button>
            <AuthDialog>
              <Button size="sm" variant="outline" className="text-xs border-zinc-800 bg-zinc-900/60 text-zinc-300">
                Sign In / Register
              </Button>
            </AuthDialog>
          </div>
        </Card>
      )}

      {/* Profile Overview Card */}
      <Card className="glass-card border-zinc-800/80 bg-zinc-950/70">
        <CardHeader className="pb-3">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div>
              {isEditingHeader ? (
                <div className="space-y-2 max-w-md">
                  <Input
                    value={profile.full_name}
                    onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                    placeholder="Full Name (e.g. Alex Rivera)"
                    className="font-bold text-lg bg-zinc-900 border-zinc-800"
                  />
                  <Input
                    value={profile.headline}
                    onChange={(e) => setProfile({ ...profile, headline: e.target.value })}
                    placeholder="Professional Headline (e.g. Senior Backend Engineer)"
                    className="text-xs bg-zinc-900 border-zinc-800"
                  />
                  <Input
                    value={profile.location}
                    onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                    placeholder="Location (e.g. Berlin, Germany / Remote)"
                    className="text-xs bg-zinc-900 border-zinc-800"
                  />
                </div>
              ) : (
                <>
                  <CardTitle className="text-xl text-zinc-100">
                    {profile.full_name || "Candidate Profile"}
                  </CardTitle>
                  <CardDescription className="text-sm font-medium text-zinc-400">
                    {profile.headline ? `${profile.headline} • ` : ""}
                    {profile.location || "No location set"}
                  </CardDescription>
                </>
              )}
            </div>
            {isEditingHeader ? (
              <div className="flex gap-2">
                <Button size="sm" onClick={handleSaveHeader} disabled={isSaving} className="text-xs bg-violet-600 hover:bg-violet-500 text-white">
                  {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save"}
                </Button>
                <Button size="sm" variant="outline" onClick={() => setIsEditingHeader(false)} className="text-xs border-zinc-800 text-zinc-300">
                  Cancel
                </Button>
              </div>
            ) : (
              <Button size="sm" variant="outline" onClick={() => setIsEditingHeader(true)} className="text-xs border-zinc-800 bg-zinc-900/60 text-zinc-300">
                Edit Basic Info
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isEditingHeader ? (
            <Textarea
              value={profile.summary}
              onChange={(e) => setProfile({ ...profile, summary: e.target.value })}
              placeholder="Executive summary / professional bio..."
              className="mt-2 text-xs bg-zinc-900 border-zinc-800 text-zinc-200"
            />
          ) : (
            <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
              {profile.summary || "No executive summary configured. Click 'Edit Basic Info' or upload your CV to automatically generate a profile summary."}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Loading state */}
      {isLoading ? (
        <div className="p-12 text-center text-zinc-400 flex flex-col items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin text-violet-400" />
          <span className="text-sm font-mono">Loading Candidate Evidence Bank...</span>
        </div>
      ) : totalItems === 0 ? (
        /* Empty State */
        <Card className="p-8 text-center glass-card border-dashed border-zinc-800 bg-zinc-950/40 space-y-4">
          <div className="h-12 w-12 rounded-2xl bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400 mx-auto">
            <Database className="h-6 w-6" />
          </div>
          <div className="space-y-1 max-w-md mx-auto">
            <h3 className="text-base font-semibold text-zinc-200">No Evidence Bank Entries Found</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Upload your base CV to deconstruct your experience into canonical immutable items with stable IDs (<code className="text-violet-400 font-mono">EXP_001</code>, <code className="text-indigo-400 font-mono">SKILL_001</code>).
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Link href="/cv-upload">
              <Button className="gap-2 text-xs bg-violet-600 hover:bg-violet-500 text-white">
                <FileUp className="h-3.5 w-3.5" />
                Upload CV to Populate
              </Button>
            </Link>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAddExperience(true)}
              className="text-xs border-zinc-800 bg-zinc-900 text-zinc-300"
            >
              <Plus className="h-3.5 w-3.5 mr-1" />
              Add Experience Manually
            </Button>
          </div>
        </Card>
      ) : (
        /* Tabs Collections */
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 bg-zinc-900/80 border border-zinc-800/80 p-1">
            <TabsTrigger value="experience" className="text-xs data-[state=active]:bg-zinc-800 text-zinc-300">
              Experience ({experiences.length})
            </TabsTrigger>
            <TabsTrigger value="skills" className="text-xs data-[state=active]:bg-zinc-800 text-zinc-300">
              Skills ({skills.length})
            </TabsTrigger>
            <TabsTrigger value="projects" className="text-xs data-[state=active]:bg-zinc-800 text-zinc-300">
              Projects ({projects.length})
            </TabsTrigger>
            <TabsTrigger value="education" className="text-xs data-[state=active]:bg-zinc-800 text-zinc-300">
              Education ({education.length})
            </TabsTrigger>
            <TabsTrigger value="certifications" className="text-xs data-[state=active]:bg-zinc-800 text-zinc-300">
              Certifications ({certifications.length})
            </TabsTrigger>
          </TabsList>

          {/* Experience Tab */}
          <TabsContent value="experience" className="space-y-4 pt-4">
            <div className="flex justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowAddExperience(true)}
                className="text-xs gap-1.5 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white"
              >
                <Plus className="h-3.5 w-3.5 text-violet-400" />
                <span>Add Role</span>
              </Button>
            </div>

            {experiences.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No work experience entries recorded.</div>
            ) : (
              experiences.map((exp) => (
                <Card key={exp.id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">{exp.role_title}</CardTitle>
                        <CardDescription className="font-medium text-zinc-300 text-xs mt-0.5">
                          {exp.company_name} &bull; {exp.location}
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs font-mono border-zinc-800 text-zinc-300">
                          {exp.start_date} - {exp.end_date || "Present"}
                        </Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteExperience(exp.id)}
                          title="Delete role"
                          className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-zinc-400">
                          Verifiable Achievement Bullets
                        </span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setActiveExpIdForBullet(exp.id)}
                          className="h-6 px-2 text-[11px] text-violet-400 hover:text-violet-300 hover:bg-violet-950/30 gap-1 font-mono"
                        >
                          <Plus className="h-3 w-3" />
                          <span>Add Bullet</span>
                        </Button>
                      </div>

                      {exp.bullets?.map((bullet: any) => (
                        <div
                          key={bullet.id || bullet.stable_id}
                          className={`p-3 rounded-lg border flex items-start justify-between gap-3 text-sm transition-colors ${
                            bullet.is_verified ? "bg-zinc-900/60 border-zinc-800" : "bg-amber-950/20 border-amber-800/40"
                          }`}
                        >
                          <div className="space-y-1 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-xs font-bold text-violet-400 px-1.5 py-0.5 bg-violet-500/10 rounded border border-violet-500/20">
                                {bullet.stable_id}
                              </span>
                              {bullet.is_verified ? (
                                <Badge variant="success" className="text-[10px] py-0 px-1.5 bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                                  Verified
                                </Badge>
                              ) : (
                                <Badge variant="secondary" className="text-[10px] py-0 px-1.5 text-amber-400 bg-amber-950/60 border border-amber-800/40">
                                  Draft / Unverified
                                </Badge>
                              )}
                            </div>
                            <p className="text-zinc-200 leading-relaxed text-xs">{bullet.raw_text || bullet.text}</p>
                          </div>

                          <div className="flex items-center gap-1 shrink-0">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setBulletToEdit({ id: bullet.id || bullet.stable_id, raw_text: bullet.raw_text || bullet.text })}
                              title="Edit bullet"
                              className="h-7 w-7 p-0 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
                            >
                              <Edit2 className="h-3 w-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleDeleteEvidence(bullet.id || bullet.stable_id)}
                              title="Delete bullet"
                              className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant={bullet.is_verified ? "secondary" : "outline"}
                              onClick={() => handleToggleVerifyBullet(exp.id, bullet.stable_id, bullet.is_verified)}
                              className="text-xs h-7 px-2 border-zinc-800"
                            >
                              {bullet.is_verified ? "Verified ✓" : "Verify"}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          {/* Skills Tab */}
          <TabsContent value="skills" className="pt-4 space-y-4">
            <div className="flex justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowAddSkill(true)}
                className="text-xs gap-1.5 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white"
              >
                <Plus className="h-3.5 w-3.5 text-violet-400" />
                <span>Add Skill</span>
              </Button>
            </div>

            <Card className="glass-card border-zinc-800/80 bg-zinc-950/70">
              <CardHeader>
                <CardTitle className="text-base text-zinc-100">Technical & Domain Skills</CardTitle>
                <CardDescription className="text-xs text-zinc-400">
                  Verified skills indexed with immutable stable IDs for semantic matching.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {skills.length === 0 ? (
                  <div className="p-8 text-center text-zinc-500 text-xs font-mono">No skills recorded.</div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {skills.map((skill) => (
                      <div
                        key={skill.id || skill.stable_id}
                        className="flex items-center justify-between p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/60"
                      >
                        <div className="flex items-center gap-2 truncate">
                          <span className="font-mono text-xs font-semibold text-violet-400">{skill.stable_id}</span>
                          <span className="text-xs font-medium text-zinc-200 truncate">{skill.name}</span>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteSkill(skill.id || skill.stable_id)}
                            title="Delete skill"
                            className="h-6 w-6 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant={skill.is_verified ? "ghost" : "outline"}
                            onClick={() => handleToggleVerifySkill(skill.stable_id, skill.is_verified)}
                            className={`h-6 px-1.5 text-xs ${skill.is_verified ? "text-emerald-400 font-bold" : "border-zinc-800"}`}
                          >
                            {skill.is_verified ? "✓" : "Verify"}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Projects Tab */}
          <TabsContent value="projects" className="space-y-4 pt-4">
            <div className="flex justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowAddProject(true)}
                className="text-xs gap-1.5 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white"
              >
                <Plus className="h-3.5 w-3.5 text-violet-400" />
                <span>Add Project</span>
              </Button>
            </div>

            {projects.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No projects recorded.</div>
            ) : (
              projects.map((proj) => (
                <Card key={proj.id || proj.stable_id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-emerald-400 px-1.5 py-0.5 bg-emerald-500/10 rounded border border-emerald-500/20">
                          {proj.stable_id}
                        </span>
                        <CardTitle className="text-base text-zinc-100">{proj.title}</CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="success" className="text-[10px] bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                          Verified
                        </Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteProject(proj.id || proj.stable_id)}
                          title="Delete project"
                          className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-xs text-zinc-300 leading-relaxed">{proj.description}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {proj.technologies?.map((tech: string) => (
                        <Badge key={tech} variant="secondary" className="text-[11px] font-mono bg-zinc-900 border-zinc-800 text-zinc-300">
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          {/* Education Tab */}
          <TabsContent value="education" className="space-y-4 pt-4">
            <div className="flex justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowAddEducation(true)}
                className="text-xs gap-1.5 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white"
              >
                <Plus className="h-3.5 w-3.5 text-violet-400" />
                <span>Add Education</span>
              </Button>
            </div>

            {education.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No education credentials recorded.</div>
            ) : (
              education.map((edu) => (
                <Card key={edu.id || edu.stable_id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-violet-400 px-1.5 py-0.5 bg-violet-500/10 rounded border border-violet-500/20">
                          {edu.stable_id}
                        </span>
                        <CardTitle className="text-base text-zinc-100">{edu.degree} in {edu.field_of_study}</CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="success" className="text-[10px] bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">Verified</Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteEducation(edu.id || edu.stable_id)}
                          title="Delete education"
                          className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                    <CardDescription className="text-xs text-zinc-400 mt-1">{edu.institution}</CardDescription>
                  </CardHeader>
                </Card>
              ))
            )}
          </TabsContent>

          {/* Certifications Tab */}
          <TabsContent value="certifications" className="space-y-4 pt-4">
            <div className="flex justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowAddCertification(true)}
                className="text-xs gap-1.5 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white"
              >
                <Plus className="h-3.5 w-3.5 text-violet-400" />
                <span>Add Certification</span>
              </Button>
            </div>

            {certifications.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No certifications recorded.</div>
            ) : (
              certifications.map((cert) => (
                <Card key={cert.id || cert.stable_id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-indigo-400 px-1.5 py-0.5 bg-indigo-500/10 rounded border border-indigo-500/20">
                          {cert.stable_id}
                        </span>
                        <CardTitle className="text-base text-zinc-100">{cert.name}</CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="success" className="text-[10px] bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">Verified</Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteCertification(cert.id || cert.stable_id)}
                          title="Delete certification"
                          className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                    <CardDescription className="text-xs text-zinc-400 mt-1">{cert.issuing_organization}</CardDescription>
                  </CardHeader>
                </Card>
              ))
            )}
          </TabsContent>
        </Tabs>
      )}

      {/* CRUD Dialogs */}
      <AddBulletDialog
        experienceId={activeExpIdForBullet}
        isOpen={Boolean(activeExpIdForBullet)}
        onClose={() => setActiveExpIdForBullet(null)}
        onSuccess={loadData}
      />

      <EditBulletDialog
        bullet={bulletToEdit}
        isOpen={Boolean(bulletToEdit)}
        onClose={() => setBulletToEdit(null)}
        onSuccess={loadData}
      />

      <AddExperienceDialog
        isOpen={showAddExperience}
        onClose={() => setShowAddExperience(false)}
        onSuccess={loadData}
      />

      <AddSkillDialog
        isOpen={showAddSkill}
        onClose={() => setShowAddSkill(false)}
        onSuccess={loadData}
      />

      <AddProjectDialog
        isOpen={showAddProject}
        onClose={() => setShowAddProject(false)}
        onSuccess={loadData}
      />

      <AddEducationDialog
        isOpen={showAddEducation}
        onClose={() => setShowAddEducation(false)}
        onSuccess={loadData}
      />

      <AddCertificationDialog
        isOpen={showAddCertification}
        onClose={() => setShowAddCertification(false)}
        onSuccess={loadData}
      />
    </div>
  );
}
