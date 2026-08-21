"use client";

import { useEffect, useState } from "react";
import { Check, ShieldCheck, Plus, ExternalLink, Calendar, MapPin, Briefcase, CheckCircle2, RefreshCw, Loader2, Sparkles } from "lucide-react";
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

  // Profile metadata
  const [profile, setProfile] = useState({
    full_name: "Youssof El Karhani",
    headline: "AI & Automation Lead / Full-Stack Engineer",
    location: "Munich, Germany",
    summary: "Specialized in distributed AI systems, backend microservices, and LLM orchestration with production experience.",
  });

  // Evidence Bank Collections
  const [experiences, setExperiences] = useState<any[]>([
    {
      id: "exp-1",
      company_name: "RUYA Advisory",
      role_title: "AI & Automation Lead",
      location: "Munich, Germany",
      start_date: "2023-01",
      end_date: "Present",
      is_current: true,
      bullets: [
        {
          id: "b-1",
          stable_id: "EXP_001",
          raw_text: "Architected the Ruya Central Hub, an event-driven automation middleware utilizing Python, Flask, and Gunicorn.",
          is_verified: true,
          variants: {
            EXP_001_SHORT: "Architected event-driven automation middleware in Python & Flask.",
          },
        },
        {
          id: "b-2",
          stable_id: "EXP_002",
          raw_text: "Developed a secure headless payment system integrating external fintech APIs and OAuth2 authentication.",
          is_verified: true,
        },
      ],
    },
  ]);

  const [skills, setSkills] = useState<any[]>([
    { id: "sk-1", stable_id: "SKILL_001", name: "Python", category: "programming", is_verified: true },
    { id: "sk-2", stable_id: "SKILL_002", name: "FastAPI", category: "backend", is_verified: true },
    { id: "sk-3", stable_id: "SKILL_003", name: "PostgreSQL", category: "backend", is_verified: true },
    { id: "sk-4", stable_id: "SKILL_004", name: "Next.js", category: "frontend", is_verified: true },
  ]);

  const [projects, setProjects] = useState<any[]>([
    {
      id: "pr-1",
      stable_id: "PROJ_001",
      title: "Sentimental Chatbot (S.Cb.)",
      description: "Developed a Discord companion integrating Gemini 1.5 Flash for natural language generation and custom Bi-GRU neural network.",
      technologies: ["Python", "TensorFlow", "FastAPI", "PostgreSQL"],
      is_verified: true,
    },
  ]);

  const [education, setEducation] = useState<any[]>([
    {
      id: "ed-1",
      stable_id: "EDU_001",
      institution: "University of Balamand",
      degree: "Bachelor of Science",
      field_of_study: "Computer Science",
      is_verified: true,
    },
  ]);

  const [certifications, setCertifications] = useState<any[]>([
    {
      id: "ce-1",
      stable_id: "CERT_001",
      name: "Model Context Protocol (MCP) + Applied MCP",
      issuing_organization: "DeepLearning.AI",
      is_verified: true,
    },
  ]);

  // Load profile from backend
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const res = await profileApi.getProfile();
        if (res) {
          setProfile((prev) => ({
            full_name: res.full_name || prev.full_name,
            headline: res.headline || prev.headline,
            location: res.location || prev.location,
            summary: res.summary || prev.summary,
          }));

          if (res.evidence_bank) {
            if (res.evidence_bank.experiences?.length > 0) {
              setExperiences(res.evidence_bank.experiences);
            }
            if (res.evidence_bank.skills?.length > 0) {
              setSkills(res.evidence_bank.skills);
            }
            if (res.evidence_bank.projects?.length > 0) {
              setProjects(res.evidence_bank.projects);
            }
            if (res.evidence_bank.education?.length > 0) {
              setEducation(res.evidence_bank.education);
            }
            if (res.evidence_bank.certifications?.length > 0) {
              setCertifications(res.evidence_bank.certifications);
            }
          }
        }
      } catch (err) {
        console.log("Using initial verified evidence profile state.");
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

  const percentVerified = totalItems > 0 ? Math.round((verifiedItems / totalItems) * 100) : 100;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Candidate Evidence Bank"
        subtitle="Manage your canonical profile and immutable evidence items (stable IDs) used for deterministic CV rendering."
      >
        <div className="flex items-center gap-3">
          <Button size="sm" variant="outline" onClick={handleVerifyAll} className="gap-1.5 text-xs">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            Verify All Evidence
          </Button>
          <Badge variant="success" className="gap-1.5 py-1 px-3 text-xs">
            <ShieldCheck className="h-4 w-4" />
            {percentVerified}% Verified ({verifiedItems}/{totalItems})
          </Badge>
        </div>
      </PageHeader>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div>
              {isEditingHeader ? (
                <div className="space-y-2 max-w-md">
                  <Input
                    value={profile.full_name}
                    onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                    placeholder="Full Name"
                    className="font-bold text-lg"
                  />
                  <Input
                    value={profile.headline}
                    onChange={(e) => setProfile({ ...profile, headline: e.target.value })}
                    placeholder="Professional Headline"
                  />
                  <Input
                    value={profile.location}
                    onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                    placeholder="Location"
                  />
                </div>
              ) : (
                <>
                  <CardTitle className="text-xl">{profile.full_name}</CardTitle>
                  <CardDescription className="text-sm font-medium text-foreground">
                    {profile.headline} &bull; {profile.location}
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
              <Button size="sm" variant="outline" onClick={() => setIsEditingHeader(true)}>
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
              placeholder="Executive summary / bio..."
              className="mt-2"
            />
          ) : (
            <p className="text-sm text-muted-foreground">{profile.summary}</p>
          )}
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="experience">Experience ({experiences.length})</TabsTrigger>
          <TabsTrigger value="skills">Skills ({skills.length})</TabsTrigger>
          <TabsTrigger value="projects">Projects ({projects.length})</TabsTrigger>
          <TabsTrigger value="education">Education ({education.length})</TabsTrigger>
          <TabsTrigger value="certifications">Certifications ({certifications.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="experience" className="space-y-4 pt-4">
          {experiences.map((exp) => (
            <Card key={exp.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{exp.role_title}</CardTitle>
                    <CardDescription className="font-medium text-foreground">
                      {exp.company_name} &bull; {exp.location}
                    </CardDescription>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {exp.start_date} - {exp.end_date || "Present"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Verifiable Achievement Bullets
                  </span>
                  {exp.bullets?.map((bullet: any) => (
                    <div
                      key={bullet.id || bullet.stable_id}
                      className={`p-3 rounded-lg border flex items-start justify-between gap-3 text-sm transition-colors ${
                        bullet.is_verified ? "bg-card border-border" : "bg-amber-50/20 border-amber-500/30"
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-primary px-1.5 py-0.5 bg-primary/10 rounded">
                            {bullet.stable_id}
                          </span>
                          {bullet.is_verified ? (
                            <Badge variant="success" className="text-[10px] py-0 px-1.5">
                              Verified
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-[10px] py-0 px-1.5 text-amber-600 bg-amber-100/50">
                              Draft / Unverified
                            </Badge>
                          )}
                        </div>
                        <p className="text-foreground/90 leading-relaxed">{bullet.raw_text || bullet.text}</p>
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
          ))}
        </TabsContent>

        <TabsContent value="skills" className="pt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Technical & Domain Skills</CardTitle>
              <CardDescription>
                Verified skills indexed with immutable stable IDs for semantic matching.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {skills.map((skill) => (
                  <div
                    key={skill.id || skill.stable_id}
                    className="flex items-center justify-between p-2.5 rounded-lg border bg-card"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-primary">{skill.stable_id}</span>
                      <span className="text-sm font-medium">{skill.name}</span>
                    </div>
                    <Button
                      size="sm"
                      variant={skill.is_verified ? "ghost" : "outline"}
                      onClick={() => handleToggleVerifySkill(skill.stable_id, skill.is_verified)}
                      className={`h-7 px-2 text-xs ${skill.is_verified ? "text-emerald-600 font-bold" : ""}`}
                    >
                      {skill.is_verified ? "✓" : "Verify"}
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="projects" className="space-y-4 pt-4">
          {projects.map((proj) => (
            <Card key={proj.id || proj.stable_id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-primary px-1.5 py-0.5 bg-primary/10 rounded">
                      {proj.stable_id}
                    </span>
                    <CardTitle className="text-base">{proj.title}</CardTitle>
                  </div>
                  <Badge variant="success" className="text-[10px]">
                    Verified
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">{proj.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  {proj.technologies?.map((tech: string) => (
                    <Badge key={tech} variant="secondary" className="text-xs font-mono">
                      {tech}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="education" className="space-y-4 pt-4">
          {education.map((edu) => (
            <Card key={edu.id || edu.stable_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-primary px-1.5 py-0.5 bg-primary/10 rounded">
                      {edu.stable_id}
                    </span>
                    <CardTitle className="text-base">{edu.degree} in {edu.field_of_study}</CardTitle>
                  </div>
                  <Badge variant="success" className="text-[10px]">Verified</Badge>
                </div>
                <CardDescription>{edu.institution}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="certifications" className="space-y-4 pt-4">
          {certifications.map((cert) => (
            <Card key={cert.id || cert.stable_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-primary px-1.5 py-0.5 bg-primary/10 rounded">
                      {cert.stable_id}
                    </span>
                    <CardTitle className="text-base">{cert.name}</CardTitle>
                  </div>
                  <Badge variant="success" className="text-[10px]">Verified</Badge>
                </div>
                <CardDescription>{cert.issuing_organization}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
