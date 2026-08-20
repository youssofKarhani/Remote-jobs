# Next.js App Router Best Practices

When working inside the `frontend/` directory, adhere to the following rules:

1. **App Router**: Always use the modern Next.js App Router (`app/` directory) instead of the older `pages/` directory.
2. **Server vs. Client Components**: 
   - Components are React Server Components (RSC) by default. Maximize their use for better performance.
   - Only add the `"use client";` directive at the very top of a file when you explicitly need client-side interactivity (e.g., `useState`, `useEffect`, `onClick`).
3. **Styling**: Use Tailwind CSS for all styling. Avoid custom CSS files unless strictly necessary.
4. **Data Fetching**: 
   - Do NOT connect directly to the database from the frontend.
   - All data fetching must be done by calling the FastAPI backend endpoints (e.g., via `fetch` in Server Components or `SWR`/`React Query` in Client Components).
5. **TypeScript**: Use strict TypeScript definitions for all props and state.
