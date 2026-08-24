"use client";

import { useEffect, useState } from "react";
import { Check, ShieldCheck, Plus, ExternalLink, Calendar, MapPin, Briefcase, CheckCircle2, RefreshCw, Loader2, Sparkles, FileUp, Database, AlertCircle } from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { profileApi } from "@/lib/api";

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState("experience");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isEditingHeader, setIsEditingHeader] = useState(false);

  // Profile metadata (initialized without hardcoded dummy data)
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

  // Load profile from backend
  useEffect(() => {
    async function loadData() {
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
      } catch (err) {
        console.log("No stored profile loaded from API yet.");
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

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
            <Button size="sm" variant="outline" onClick={handleVerifyAll} className="gap-1.5 text-xs">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              Verify All Evidence
            </Button>
          )}
          <Badge variant="success" className="gap-1.5 py-1 px-3 text-xs">
            <ShieldCheck className="h-4 w-4" />
            {percentVerified}% Verified ({verifiedItems}/{totalItems})
          </Badge>
        </div>
      </PageHeader>

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
                    className="font-bold text-lg"
                  />
                  <Input
                    value={profile.headline}
                    onChange={(e) => setProfile({ ...profile, headline: e.target.value })}
                    placeholder="Professional Headline (e.g. Senior Backend Engineer)"
                  />
                  <Input
                    value={profile.location}
                    onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                    placeholder="Location (e.g. Berlin, Germany / Remote)"
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
                <Button size="sm" onClick={handleSaveHeader} disabled={isSaving}>
                  {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Save"}
                </Button>
                <Button size="sm" variant="outline" onClick={() => setIsEditingHeader(false)}>
                  Cancel
                </Button>
              </div>
            ) : (
              <Button size="sm" variant="outline" onClick={() => setIsEditingHeader(true)} className="text-xs">
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
              className="mt-2"
            />
          ) : (
            <p className="text-sm text-zinc-400">
              {profile.summary || "No executive summary configured. Click 'Edit Basic Info' or upload your CV to automatically generate a profile summary."}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Loading state */}
      {isLoading ? (
        <div className="p-12 text-center text-zinc-400 flex flex-col items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin text-blue-400" />
          <span className="text-sm font-mono">Loading Candidate Evidence Bank...</span>
        </div>
      ) : totalItems === 0 ? (
        /* Empty State */
        <Card className="p-8 text-center glass-card border-dashed border-zinc-800 bg-zinc-950/40 space-y-4">
          <div className="h-12 w-12 rounded-2xl bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-400 mx-auto">
            <Database className="h-6 w-6" />
          </div>
          <div className="space-y-1 max-w-md mx-auto">
            <h3 className="text-base font-semibold text-zinc-200">No Evidence Bank Entries Found</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Upload your base CV to deconstruct your experience into canonical immutable items with stable IDs (<code className="text-blue-400 font-mono">EXP_001</code>, <code className="text-purple-400 font-mono">SKILL_001</code>).
            </p>
          </div>
          <div className="pt-2">
            <Link href="/cv-upload">
              <Button className="gap-2 text-xs">
                <FileUp className="h-3.5 w-3.5" />
                Upload CV to Populate Evidence Bank
              </Button>
            </Link>
          </div>
        </Card>
      ) : (
        /* Tabs Collections */
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="experience">Experience ({experiences.length})</TabsTrigger>
            <TabsTrigger value="skills">Skills ({skills.length})</TabsTrigger>
            <TabsTrigger value="projects">Projects ({projects.length})</TabsTrigger>
            <TabsTrigger value="education">Education ({education.length})</TabsTrigger>
            <TabsTrigger value="certifications">Certifications ({certifications.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="experience" className="space-y-4 pt-4">
            {experiences.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No work experience entries recorded.</div>
            ) : (
              experiences.map((exp) => (
                <Card key={exp.id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">{exp.role_title}</CardTitle>
                        <CardDescription className="font-medium text-zinc-300">
                          {exp.company_name} &bull; {exp.location}
                        </CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs font-mono">
                        {exp.start_date} - {exp.end_date || "Present"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="space-y-2">
                      <span className="text-xs font-mono font-semibold uppercase tracking-wider text-zinc-400">
                        Verifiable Achievement Bullets
                      </span>
                      {exp.bullets?.map((bullet: any) => (
                        <div
                          key={bullet.id || bullet.stable_id}
                          className={`p-3 rounded-lg border flex items-start justify-between gap-3 text-sm transition-colors ${
                            bullet.is_verified ? "bg-zinc-900/60 border-zinc-800" : "bg-amber-950/20 border-amber-800/40"
                          }`}
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-xs font-bold text-blue-400 px-1.5 py-0.5 bg-blue-500/10 rounded border border-blue-500/20">
                                {bullet.stable_id}
                              </span>
                              {bullet.is_verified ? (
                                <Badge variant="success" className="text-[10px] py-0 px-1.5">
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
                          <Button
                            size="sm"
                            variant={bullet.is_verified ? "secondary" : "outline"}
                            onClick={() => handleToggleVerifyBullet(exp.id, bullet.stable_id, bullet.is_verified)}
                            className="shrink-0 text-xs h-8"
                          >
                            {bullet.is_verified ? "Verified ✓" : "Verify Item"}
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="skills" className="pt-4">
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
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-semibold text-purple-400">{skill.stable_id}</span>
                          <span className="text-sm font-medium text-zinc-200">{skill.name}</span>
                        </div>
                        <Button
                          size="sm"
                          variant={skill.is_verified ? "ghost" : "outline"}
                          onClick={() => handleToggleVerifySkill(skill.stable_id, skill.is_verified)}
                          className={`h-7 px-2 text-xs ${skill.is_verified ? "text-emerald-400 font-bold" : ""}`}
                        >
                          {skill.is_verified ? "✓" : "Verify"}
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="projects" className="space-y-4 pt-4">
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
                      <Badge variant="success" className="text-[10px]">
                        Verified
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-xs text-zinc-400">{proj.description}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {proj.technologies?.map((tech: string) => (
                        <Badge key={tech} variant="secondary" className="text-xs font-mono">
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="education" className="space-y-4 pt-4">
            {education.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No education credentials recorded.</div>
            ) : (
              education.map((edu) => (
                <Card key={edu.id || edu.stable_id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-blue-400 px-1.5 py-0.5 bg-blue-500/10 rounded border border-blue-500/20">
                          {edu.stable_id}
                        </span>
                        <CardTitle className="text-base text-zinc-100">{edu.degree} in {edu.field_of_study}</CardTitle>
                      </div>
                      <Badge variant="success" className="text-[10px]">Verified</Badge>
                    </div>
                    <CardDescription className="text-xs text-zinc-400">{edu.institution}</CardDescription>
                  </CardHeader>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="certifications" className="space-y-4 pt-4">
            {certifications.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs font-mono">No certifications recorded.</div>
            ) : (
              certifications.map((cert) => (
                <Card key={cert.id || cert.stable_id} className="glass-card border-zinc-800/80 bg-zinc-950/70">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-purple-400 px-1.5 py-0.5 bg-purple-500/10 rounded border border-purple-500/20">
                          {cert.stable_id}
                        </span>
                        <CardTitle className="text-base text-zinc-100">{cert.name}</CardTitle>
                      </div>
                      <Badge variant="success" className="text-[10px]">Verified</Badge>
                    </div>
                    <CardDescription className="text-xs text-zinc-400">{cert.issuing_organization}</CardDescription>
                  </CardHeader>
                </Card>
              ))
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
