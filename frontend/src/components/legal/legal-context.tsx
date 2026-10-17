"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type LegalLanguage = "en" | "de";

interface LegalLanguageContextType {
  language: LegalLanguage;
  setLanguage: (lang: LegalLanguage) => void;
  toggleLanguage: () => void;
}

const LegalLanguageContext = createContext<LegalLanguageContextType>({
  language: "en",
  setLanguage: () => {},
  toggleLanguage: () => {},
});

const STORAGE_KEY = "findjobfit_legal_language";

export function LegalLanguageProvider({ children }: { children: React.ReactNode }) {
  // Default to English as requested
  const [language, setLanguageState] = useState<LegalLanguage>("en");
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Check URL search params first (e.g. ?lang=de or ?lang=en)
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const urlLang = params.get("lang");

      if (urlLang === "de" || urlLang === "en") {
        setLanguageState(urlLang);
        try {
          localStorage.setItem(STORAGE_KEY, urlLang);
        } catch {
          // ignore localStorage error in private mode
        }
      } else {
        // Check localStorage
        try {
          const stored = localStorage.getItem(STORAGE_KEY);
          if (stored === "de" || stored === "en") {
            setLanguageState(stored);
          }
        } catch {
          // default to en
        }
      }
      setIsInitialized(true);
    }
  }, []);

  const setLanguage = (lang: LegalLanguage) => {
    setLanguageState(lang);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, lang);
      } catch {
        // ignore
      }

      // Update URL search param seamlessly without reload
      const url = new URL(window.location.href);
      if (lang === "en") {
        url.searchParams.delete("lang");
      } else {
        url.searchParams.set("lang", "de");
      }
      window.history.replaceState({}, "", url.toString());
    }
  };

  const toggleLanguage = () => {
    setLanguage(language === "en" ? "de" : "en");
  };

  return (
    <LegalLanguageContext.Provider value={{ language, setLanguage, toggleLanguage }}>
      <div data-legal-lang={language} className={!isInitialized ? "opacity-95" : "opacity-100 transition-opacity duration-200"}>
        {children}
      </div>
    </LegalLanguageContext.Provider>
  );
}

export function useLegalLanguage() {
  return useContext(LegalLanguageContext);
}
