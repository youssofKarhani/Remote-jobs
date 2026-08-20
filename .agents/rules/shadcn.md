# Shadcn UI & Frontend Design System Rules

When building the frontend interface in the `frontend/` directory, you must strictly adhere to the following design system rules centered around `shadcn/ui` and Tailwind CSS.

## 1. Core Component Philosophy
- **Never build complex UI primitives from scratch.** Always check if a `shadcn/ui` component exists first (e.g., Button, Card, Dialog, Table, Form).
- If a component is missing, you must instruct the user to run the installation command: `npx shadcn@latest add [component-name]`.
- All `shadcn/ui` primitives should reside in `components/ui/`.

## 2. Styling and Tailwind
- Use the `cn()` utility function (clsx + tailwind-merge) provided by shadcn for merging conditional classes safely.
- Avoid inline styles (`style={{...}}`). Strictly use Tailwind utility classes.
- Use CSS variables for colors (e.g., `bg-primary`, `text-muted-foreground`) to ensure light/dark mode compatibility, rather than hardcoding colors like `bg-blue-500`.

## 3. Forms and Validation
- Use `react-hook-form` in combination with `zod` for all form handling and validation.
- Wrap forms using the `<Form>` component provided by `shadcn/ui` to ensure consistent error states and accessibility.

## 4. Icons
- Use `lucide-react` for all icons. It is the default icon library paired with shadcn/ui.
- Example: `import { ChevronRight } from "lucide-react";`

## 5. Layout and Composition
- Prefer composition over monolithic components. 
- Example: Instead of passing a massive configuration object to a custom table component, use the composable `shadcn/ui` `<Table>`, `<TableHeader>`, `<TableRow>`, and `<TableCell>` components directly in the view.
- Maintain responsive design using Tailwind's `sm:`, `md:`, `lg:` prefixes. Assume a mobile-first approach.

## 6. Accessibility (a11y)
- Rely on the Radix UI primitives underlying `shadcn/ui` for keyboard navigation and ARIA attributes. Do not strip them out when customizing components.
