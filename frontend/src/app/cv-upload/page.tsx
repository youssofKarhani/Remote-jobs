"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle2, AlertCircle, Sparkles, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { vcopy } from "@/lib/verification-copy";
import { CvExtractionPreview } from "@/components/cv/cv-extraction-preview";
import { useGatedCvExtraction } from "@/lib/use-gated-cv-extraction";

export default function CVUploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState("");
  const [extractionResult, setExtractionResult] = useState<{
    experiencesCount: number;
    skillsCount: number;
    projectsCount: number;
    educationCount: number;
    certificationsCount: number;
  } | null>(null);

  const extraction = useGatedCvExtraction((summary) => {
    setSelectedFile(null);
    setRawText("");
    setExtractionResult({
      experiencesCount: summary.experiences_extracted,
      skillsCount: summary.skills_extracted,
      projectsCount: summary.projects_extracted,
      educationCount: summary.education_extracted,
      certificationsCount: summary.certifications_extracted,
    });
  });
  const isProcessing = extraction.isBusy && !extraction.preview;
  const errorMessage = extraction.preview ? null : extraction.error;
  const currentStep =
    extraction.phase === "saving" ? "Saving your CV to your profile..." : "Reading and extracting your CV...";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      extraction.setError(null);
    }
  };

  const handleStartExtraction = () => {
    if (selectedFile) {
      void extraction.extract({ kind: "file", file: selectedFile });
    } else if (rawText.trim()) {
      void extraction.extract({ kind: "text", text: rawText, label: "Pasted resume text" });
    } else {
      extraction.setError("Please select a file or paste your resume text.");
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="CV Ingestion & Parsing"
        subtitle={vcopy("cvUpload.pageSubtitle")}
      />

      {errorMessage && (
        <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 flex items-center gap-3 text-destructive text-sm">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Guided Onboarding Callout */}
      <div className="p-4 rounded-2xl border border-violet-500/30 bg-violet-950/20 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-violet-950/80 border border-violet-800/40 text-violet-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-zinc-100">Guided Onboarding Flow Available</h4>
            <p className="text-xs text-zinc-400">{vcopy("cvUpload.streamlinedSetup")}</p>
          </div>
        </div>
        <Link href="/onboarding">
          <Button size="sm" className="bg-violet-600 hover:bg-violet-500 text-white text-xs rounded-full px-5 h-9 shrink-0 gap-1.5 shadow-md shadow-violet-600/30">
            <span>Launch Flow</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </Link>
      </div>

      {extraction.preview ? (
        <CvExtractionPreview
          result={extraction.preview}
          phase={extraction.phase}
          error={extraction.error}
          onDiscard={extraction.discard}
          onRetrySave={extraction.retrySave}
        />
      ) : !extractionResult ? (
        <Card>
          <CardHeader>
            <CardTitle>Choose Ingestion Method</CardTitle>
            <CardDescription>
              Select your resume document or supply raw text. The system parses facts into normalized records with stable IDs.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Tabs defaultValue="upload" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="upload">File Upload</TabsTrigger>
                <TabsTrigger value="paste">Paste Plain Text</TabsTrigger>
              </TabsList>

              <TabsContent value="upload" className="space-y-4 pt-4">
                <label className="border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-colors bg-muted/20 hover:bg-muted/40">
                  <UploadCloud className="h-12 w-12 text-muted-foreground mb-3" />
                  <span className="font-medium text-sm">
                    {selectedFile ? selectedFile.name : "Click to browse or drag and drop your resume"}
                  </span>
                  <span className="text-xs text-muted-foreground mt-1">
                    Supports PDF, DOCX, TXT (Max 15 MB)
                  </span>
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,.doc,.txt,.md"
                    onChange={handleFileChange}
                  />
                </label>
              </TabsContent>

              <TabsContent value="paste" className="space-y-4 pt-4">
                <Textarea
                  placeholder="Paste the raw text of your resume here..."
                  className="min-h-[220px] font-mono text-xs"
                  value={rawText}
                  onChange={(e) => {
                    setRawText(e.target.value);
                    extraction.setError(null);
                  }}
                />
              </TabsContent>
            </Tabs>

            {isProcessing && (
              <div className="space-y-3 pt-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-muted-foreground flex items-center gap-1.5">
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                    {currentStep}
                  </span>
                </div>
                <Progress value={extraction.phase === "saving" ? 85 : 45} className="h-2" />
              </div>
            )}
          </CardContent>

          <CardFooter className="flex justify-end gap-3 border-t pt-4">
            <Button
              onClick={handleStartExtraction}
              disabled={(!selectedFile && !rawText.trim()) || isProcessing}
              className="gap-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Processing Extraction...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Start Structured Extraction
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <Card className="border-emerald-500/30 bg-emerald-50/10">
          <CardHeader>
            <div className="flex items-center gap-2 text-emerald-600 font-semibold text-lg">
              <CheckCircle2 className="h-6 w-6" />
              Extraction Successful
            </div>
            <CardDescription>
              Your resume was normalized into structured entities with stable immutable IDs.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="border rounded-lg p-3 text-center bg-card">
                <div className="text-2xl font-bold text-primary">{extractionResult.experiencesCount}</div>
                <div className="text-xs text-muted-foreground">Experience Roles</div>
              </div>
              <div className="border rounded-lg p-3 text-center bg-card">
                <div className="text-2xl font-bold text-primary">{extractionResult.skillsCount}</div>
                <div className="text-xs text-muted-foreground">Skills</div>
              </div>
              <div className="border rounded-lg p-3 text-center bg-card">
                <div className="text-2xl font-bold text-primary">{extractionResult.projectsCount}</div>
                <div className="text-xs text-muted-foreground">Projects</div>
              </div>
              <div className="border rounded-lg p-3 text-center bg-card">
                <div className="text-2xl font-bold text-primary">{extractionResult.educationCount}</div>
                <div className="text-xs text-muted-foreground">Degrees</div>
              </div>
              <div className="border rounded-lg p-3 text-center bg-card">
                <div className="text-2xl font-bold text-primary">{extractionResult.certificationsCount}</div>
                <div className="text-xs text-muted-foreground">Certifications</div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-3 border-t pt-4">
            <Button variant="outline" onClick={() => setExtractionResult(null)}>
              Upload Another
            </Button>
            <div className="flex items-center gap-2">
              <Link href="/profile">
                <Button variant="outline" className="border-zinc-800 text-xs gap-1.5">
                  {vcopy("cvUpload.reviewBankButton")}
                </Button>
              </Link>
              <Link href="/jobs">
                <Button className="bg-violet-600 hover:bg-violet-500 text-white text-xs gap-1.5 shadow-md shadow-violet-600/30">
                  <Sparkles className="h-3.5 w-3.5" />
                  Explore Jobs &amp; Curate
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}
