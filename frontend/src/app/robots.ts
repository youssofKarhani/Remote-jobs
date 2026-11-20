import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        // Signed-in areas have nothing for search engines and shouldn't be indexed.
        disallow: ["/profile", "/preferences", "/applications", "/jobs"],
      },
    ],
    sitemap: "https://findjobfit.de/sitemap.xml",
    host: "https://findjobfit.de",
  };
}
