import { ImageResponse } from "next/og";

export const alt = "FindJobFit: tailored applications grounded in your real CV";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

// Social preview card used by link unfurls (LinkedIn, Slack, X, WhatsApp).
export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px 80px",
          background: "linear-gradient(135deg, #09090b 0%, #1e1b4b 100%)",
          color: "#f4f4f5",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 14,
              background: "#7c3aed",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 34,
              fontWeight: 700,
            }}
          >
            F
          </div>
          <div style={{ fontSize: 34, fontWeight: 600 }}>FindJobFit</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ fontSize: 64, fontWeight: 700, lineHeight: 1.1, maxWidth: 980 }}>
            Tailored applications, built only from your real experience.
          </div>
          <div style={{ fontSize: 28, color: "#a1a1aa" }}>
            Upload your CV · match remote jobs · generate CVs and cover letters
          </div>
        </div>
        <div style={{ fontSize: 24, color: "#a78bfa" }}>findjobfit.de</div>
      </div>
    ),
    size
  );
}
