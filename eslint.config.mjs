import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const lucideImportRestriction = {
  group: ["lucide-react", "lucide-react/**"],
  message: "Use a named icon from AppIcon or AppIconButton.",
};

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    files: ["src/**/*.{ts,tsx}"],
    ignores: ["src/components/app/**", "src/components/ui/**"],
    rules: {
      "no-restricted-imports": ["error", {
        patterns: [
          lucideImportRestriction,
          { group: ["@/components/ui", "@/components/ui/**", "**/components/ui/**", "**/ui/button"], message: "Use an approved App Component instead of private UI sources." },
          { group: ["**/components/app/**/*.styles", "**/components/app/**/*.styles.ts", "**/components/app/app-contract"], message: "Import the public App Component." },
        ],
      }],
    },
  },
  {
    files: ["src/app/**/*.{ts,tsx}", "src/features/**/*.{ts,tsx}", "src/components/features/**/*.{ts,tsx}"],
    ignores: [
      "src/app/review-ui/**",
      "src/app/page.tsx",
      "src/app/layout.tsx",
      "src/app/api/**",
      "src/app/robots.ts",
      "src/app/sitemap.ts",
      "src/app/**/opengraph-image.{ts,tsx}",
      "src/app/**/twitter-image.{ts,tsx}",
    ],
    rules: {
      "no-restricted-syntax": ["error",
        {
          selector: "JSXOpeningElement > JSXIdentifier.name[name=/^[a-z]/]",
          message: "Compose product UI from approved App Components.",
        },
        {
          selector: "JSXOpeningElement[name.name=/^App[A-Z]/] > JSXAttribute[name.name=/^(className|style|asChild)$/]",
          message: "Use the App Component's named design props.",
        },
      ],
      "no-restricted-imports": ["error", {
        paths: [
          { name: "next/image", message: "Use AppImage for product UI." },
          { name: "next/link", message: "Use AppLink for product UI." },
        ],
        patterns: [
          lucideImportRestriction,
          { group: ["@/components/ui", "@/components/ui/**", "**/components/ui/**", "**/ui/button"], message: "Use an approved App Component." },
          { group: ["**/components/app/**/*.styles", "**/components/app/**/*.styles.ts", "**/components/app/app-contract"], message: "Import the public App Component." },
        ],
      }],
    },
  },
  {
    files: ["src/app/review-ui/app-components-showcase.tsx"],
    rules: {
      "no-restricted-imports": ["error", {
        patterns: [lucideImportRestriction, { group: ["@/components/ui", "@/components/ui/**", "**/components/ui/**"], message: "Preview production App Components." }],
      }],
    },
  },
  {
    files: ["src/components/{app,ui}/**/*.{ts,tsx}"],
    ignores: ["src/components/app/AppIcon/AppIcon.tsx"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [lucideImportRestriction] }],
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
