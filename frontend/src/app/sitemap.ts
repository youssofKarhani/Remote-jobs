import type { MetadataRoute } from "next";

const SITE_URL = "https://findjobfit.de";

// Public pages only. Signed-in areas (profile, preferences, applications, jobs) are excluded.
const PUBLIC_ROUTES: { path: string; priority: number; changeFrequency: "weekly" | "monthly" | "yearly" }[] = [
  { path: "/", priority: 1, changeFrequency: "weekly" },
  { path: "/onboarding", priority: 0.8, changeFrequency: "monthly" },
  { path: "/cv-upload", priority: 0.7, changeFrequency: "monthly" },
  { path: "/ethics", priority: 0.4, changeFrequency: "yearly" },
  { path: "/privacy", priority: 0.3, changeFrequency: "yearly" },
  { path: "/terms", priority: 0.3, changeFrequency: "yearly" },
  { path: "/impressum", priority: 0.2, changeFrequency: "yearly" },
];

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();
  return PUBLIC_ROUTES.map(({ path, priority, changeFrequency }) => ({
    url: `${SITE_URL}${path}`,
    lastModified,
    changeFrequency,
    priority,
  }));
}
