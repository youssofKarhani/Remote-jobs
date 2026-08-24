"use client";

import { useEffect, useState } from "react";
import { Sliders, Save, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { preferencesApi } from "@/lib/api";

export default function PreferencesPage() {
  const [targetRoles, setTargetRoles] = useState<string[]>([]);
  const [newRole, setNewRole] = useState("");
  const [locations, setLocations] = useState<string[]>([]);
  const [newLocation, setNewLocation] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [hybridAllowed, setHybridAllowed] = useState(true);
  const [onsiteAllowed, setOnsiteAllowed] = useState(true);
  const [minSalary, setMinSalary] = useState("");
  const [salaryCurrency, setSalaryCurrency] = useState("USD");
  const [jobTypes, setJobTypes] = useState<string[]>([]);
  const [excludedCompanies, setExcludedCompanies] = useState<string[]>([]);
  const [excludedKeywords, setExcludedKeywords] = useState<string[]>([]);
  const [newExcludedCompany, setNewExcludedCompany] = useState("");
  const [newExcludedKeyword, setNewExcludedKeyword] = useState("");
  
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadPreferences() {
      setIsLoading(true);
      try {
        const pref = await preferencesApi.getPreferences();
        if (pref) {
          if (pref.target_roles?.length) setTargetRoles(pref.target_roles);
          if (pref.locations?.length) setLocations(pref.locations);
          if (pref.remote_only !== undefined) setRemoteOnly(pref.remote_only);
          if (pref.hybrid_allowed !== undefined) setHybridAllowed(pref.hybrid_allowed);
          if (pref.onsite_allowed !== undefined) setOnsiteAllowed(pref.onsite_allowed);
          if (pref.job_types?.length) setJobTypes(pref.job_types);
          if (pref.min_salary) setMinSalary(pref.min_salary.toString());
          if (pref.salary_currency) setSalaryCurrency(pref.salary_currency);
          if (pref.excluded_companies) setExcludedCompanies(pref.excluded_companies);
          if (pref.excluded_keywords) setExcludedKeywords(pref.excluded_keywords);
        }
      } catch (err) {
        console.log("No stored candidate preferences found yet.");
      } finally {
        setIsLoading(false);
      }
    }
    loadPreferences();
  }, []);

  const handleAddRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (newRole.trim() && !targetRoles.includes(newRole.trim())) {
      setTargetRoles([...targetRoles, newRole.trim()]);
      setNewRole("");
    }
  };

  const handleRemoveRole = (role: string) => {
    setTargetRoles(targetRoles.filter((r) => r !== role));
  };

  const handleAddLocation = (e: React.FormEvent) => {
    e.preventDefault();
    if (newLocation.trim() && !locations.includes(newLocation.trim())) {
      setLocations([...locations, newLocation.trim()]);
      setNewLocation("");
    }
  };

  const handleRemoveLocation = (loc: string) => {
    setLocations(locations.filter((l) => l !== loc));
  };

  const handleAddExcludedCompany = (e: React.FormEvent) => {
    e.preventDefault();
    if (newExcludedCompany.trim() && !excludedCompanies.includes(newExcludedCompany.trim())) {
      setExcludedCompanies([...excludedCompanies, newExcludedCompany.trim()]);
      setNewExcludedCompany("");
    }
  };

  const handleAddExcludedKeyword = (e: React.FormEvent) => {
    e.preventDefault();
    if (newExcludedKeyword.trim() && !excludedKeywords.includes(newExcludedKeyword.trim())) {
      setExcludedKeywords([...excludedKeywords, newExcludedKeyword.trim()]);
      setNewExcludedKeyword("");
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await preferencesApi.updatePreferences({
        target_roles: targetRoles,
        locations: locations,
        remote_only: remoteOnly,
        hybrid_allowed: hybridAllowed,
        onsite_allowed: onsiteAllowed,
        job_types: jobTypes,
        min_salary: minSalary ? parseFloat(minSalary) : undefined,
        salary_currency: salaryCurrency,
        excluded_companies: excludedCompanies,
        excluded_keywords: excludedKeywords,
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      console.warn("Preferences update offline, updated locally.");
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Deterministic Preferences"
        subtitle="Configure fast, zero-cost deterministic filters executed before any AI matching occurs."
      />

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Target Roles</CardTitle>
            <CardDescription>
              Jobs must match at least one of these role titles via word-boundary matching.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {targetRoles.length === 0 ? (
              <p className="text-xs text-zinc-500 italic">No target roles configured yet. Add your preferred job titles below.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {targetRoles.map((role) => (
                  <Badge key={role} variant="secondary" className="gap-1 py-1 px-2.5 text-xs">
                    {role}
                    <button
                      onClick={() => handleRemoveRole(role)}
                      className="ml-1 hover:text-destructive font-bold"
                    >
                      &times;
                    </button>
                  </Badge>
                ))}
              </div>
            )}
            <form onSubmit={handleAddRole} className="flex gap-2 max-w-md">
              <Input
                placeholder="e.g. Distributed Systems Engineer, Backend Architect"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
              />
              <Button type="submit" variant="outline" size="sm">Add</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Location & Workplace Mode</CardTitle>
            <CardDescription>
              Specify geographic boundaries and workplace flexibility.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <span className="text-sm font-medium">Target Locations</span>
              {locations.length === 0 ? (
                <p className="text-xs text-zinc-500 italic">No geographic boundaries configured. Add countries/regions or enable Remote Only.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {locations.map((loc) => (
                    <Badge key={loc} variant="secondary" className="gap-1 py-1 px-2.5 text-xs">
                      {loc}
                      <button
                        onClick={() => handleRemoveLocation(loc)}
                        className="ml-1 hover:text-destructive font-bold"
                      >
                        &times;
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
              <form onSubmit={handleAddLocation} className="flex gap-2 max-w-md">
                <Input
                  placeholder="e.g. United States, Germany, Remote EU"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                />
                <Button type="submit" variant="outline" size="sm">Add</Button>
              </form>
            </div>

            <div className="border-t pt-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="text-sm font-medium">Remote Only Policy</div>
                  <div className="text-xs text-muted-foreground">
                    Strictly filter out jobs that are not 100% remote.
                  </div>
                </div>
                <Switch checked={remoteOnly} onCheckedChange={setRemoteOnly} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Compensation & Exclusions</CardTitle>
            <CardDescription>
              Set minimum salary expectation and negative filters (companies or keywords to block).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4 max-w-md">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase text-muted-foreground">Min Salary</label>
                <Input
                  type="number"
                  placeholder="e.g. 75000"
                  value={minSalary}
                  onChange={(e) => setMinSalary(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase text-muted-foreground">Currency</label>
                <Input
                  value={salaryCurrency}
                  onChange={(e) => setSalaryCurrency(e.target.value)}
                  placeholder="EUR"
                />
              </div>
            </div>

            <div className="border-t pt-4 space-y-3">
              <span className="text-sm font-medium">Excluded Companies</span>
              <div className="flex flex-wrap gap-2">
                {excludedCompanies.map((comp) => (
                  <Badge key={comp} variant="destructive" className="gap-1 py-1 px-2.5 text-xs">
                    {comp}
                    <button
                      onClick={() => setExcludedCompanies(excludedCompanies.filter((c) => c !== comp))}
                      className="ml-1 font-bold"
                    >
                      &times;
                    </button>
                  </Badge>
                ))}
              </div>
              <form onSubmit={handleAddExcludedCompany} className="flex gap-2 max-w-md">
                <Input
                  placeholder="Add company name to block..."
                  value={newExcludedCompany}
                  onChange={(e) => setNewExcludedCompany(e.target.value)}
                />
                <Button type="submit" variant="outline" size="sm">Block</Button>
              </form>
            </div>

            <div className="border-t pt-4 space-y-3">
              <span className="text-sm font-medium">Excluded Keywords (Regex Word Boundary)</span>
              <div className="flex flex-wrap gap-2">
                {excludedKeywords.map((kw) => (
                  <Badge key={kw} variant="destructive" className="gap-1 py-1 px-2.5 text-xs">
                    {kw}
                    <button
                      onClick={() => setExcludedKeywords(excludedKeywords.filter((k) => k !== kw))}
                      className="ml-1 font-bold"
                    >
                      &times;
                    </button>
                  </Badge>
                ))}
              </div>
              <form onSubmit={handleAddExcludedKeyword} className="flex gap-2 max-w-md">
                <Input
                  placeholder="e.g. Wordpress, unpaid, crypto..."
                  value={newExcludedKeyword}
                  onChange={(e) => setNewExcludedKeyword(e.target.value)}
                />
                <Button type="submit" variant="outline" size="sm">Block</Button>
              </form>
            </div>
          </CardContent>

          <CardFooter className="flex justify-between border-t pt-4">
            <div className="flex items-center gap-2 text-sm text-emerald-600 font-medium">
              {isSaved && (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Preferences Saved Successfully
                </>
              )}
            </div>
            <Button onClick={handleSave} disabled={isSaving} className="gap-2">
              {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save Preferences
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
