export const colorIntents = ["primary", "secondary", "accent", "success", "error", "warning", "info", "destructive"] as const;
export const colorVariants = ["raw", "outline", "filled", "fullFilled"] as const;
export const colorRoles = ["solid", "hover", "active", "soft", "soft-edge", "strong", "on-solid"] as const;

export type ColorIntent = (typeof colorIntents)[number];
export type ColorVariant = (typeof colorVariants)[number];

const intentClasses = {
  primary: {
    outline: "border-primary-solid text-primary-strong hover:bg-primary-soft active:bg-primary-soft-edge aria-pressed:bg-primary-soft",
    filled: "border-primary-soft-edge bg-primary-soft text-primary-strong hover:bg-primary-soft-edge active:border-primary-solid active:bg-primary-soft-edge aria-pressed:border-primary-solid",
    fullFilled: "border-primary-solid bg-primary-solid text-primary-on-solid hover:border-primary-hover hover:bg-primary-hover active:border-primary-active active:bg-primary-active",
  },
  secondary: {
    outline: "border-secondary-solid text-secondary-strong hover:bg-secondary-soft active:bg-secondary-soft-edge aria-pressed:bg-secondary-soft",
    filled: "border-secondary-soft-edge bg-secondary-soft text-secondary-strong hover:bg-secondary-soft-edge active:border-secondary-solid active:bg-secondary-soft-edge aria-pressed:border-secondary-solid",
    fullFilled: "border-secondary-solid bg-secondary-solid text-secondary-on-solid hover:border-secondary-hover hover:bg-secondary-hover active:border-secondary-active active:bg-secondary-active",
  },
  accent: {
    outline: "border-accent-solid text-accent-strong hover:bg-accent-soft active:bg-accent-soft-edge aria-pressed:bg-accent-soft",
    filled: "border-accent-soft-edge bg-accent-soft text-accent-strong hover:bg-accent-soft-edge active:border-accent-solid active:bg-accent-soft-edge aria-pressed:border-accent-solid",
    fullFilled: "border-accent-solid bg-accent-solid text-accent-on-solid hover:border-accent-hover hover:bg-accent-hover active:border-accent-active active:bg-accent-active",
  },
  success: {
    outline: "border-success-solid text-success-strong hover:bg-success-soft active:bg-success-soft-edge aria-pressed:bg-success-soft",
    filled: "border-success-soft-edge bg-success-soft text-success-strong hover:bg-success-soft-edge active:border-success-solid active:bg-success-soft-edge aria-pressed:border-success-solid",
    fullFilled: "border-success-solid bg-success-solid text-success-on-solid hover:border-success-hover hover:bg-success-hover active:border-success-active active:bg-success-active",
  },
  error: {
    outline: "border-error-solid text-error-strong hover:bg-error-soft active:bg-error-soft-edge aria-pressed:bg-error-soft",
    filled: "border-error-soft-edge bg-error-soft text-error-strong hover:bg-error-soft-edge active:border-error-solid active:bg-error-soft-edge aria-pressed:border-error-solid",
    fullFilled: "border-error-solid bg-error-solid text-error-on-solid hover:border-error-hover hover:bg-error-hover active:border-error-active active:bg-error-active",
  },
  warning: {
    outline: "border-warning-solid text-warning-strong hover:bg-warning-soft active:bg-warning-soft-edge aria-pressed:bg-warning-soft",
    filled: "border-warning-soft-edge bg-warning-soft text-warning-strong hover:bg-warning-soft-edge active:border-warning-solid active:bg-warning-soft-edge aria-pressed:border-warning-solid",
    fullFilled: "border-warning-solid bg-warning-solid text-warning-on-solid hover:border-warning-hover hover:bg-warning-hover active:border-warning-active active:bg-warning-active",
  },
  info: {
    outline: "border-info-solid text-info-strong hover:bg-info-soft active:bg-info-soft-edge aria-pressed:bg-info-soft",
    filled: "border-info-soft-edge bg-info-soft text-info-strong hover:bg-info-soft-edge active:border-info-solid active:bg-info-soft-edge aria-pressed:border-info-solid",
    fullFilled: "border-info-solid bg-info-solid text-info-on-solid hover:border-info-hover hover:bg-info-hover active:border-info-active active:bg-info-active",
  },
  destructive: {
    outline: "border-destructive-solid text-destructive-strong hover:bg-destructive-soft active:bg-destructive-soft-edge aria-pressed:bg-destructive-soft",
    filled: "border-destructive-soft-edge bg-destructive-soft text-destructive-strong hover:bg-destructive-soft-edge active:border-destructive-solid active:bg-destructive-soft-edge aria-pressed:border-destructive-solid",
    fullFilled: "border-destructive-solid bg-destructive-solid text-destructive-on-solid hover:border-destructive-hover hover:bg-destructive-hover active:border-destructive-active active:bg-destructive-active",
  },
} satisfies Record<ColorIntent, Record<Exclude<ColorVariant, "raw">, string>>;

type ColorVariantOptions = {
  intent?: ColorIntent;
  variant?: ColorVariant;
  disabled?: boolean;
  invalid?: boolean;
};

export function getColorVariantClasses({
  intent = "primary",
  variant = "fullFilled",
  disabled = false,
  invalid = false,
}: ColorVariantOptions = {}): string {
  const focus = "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

  if (disabled) {
    if (variant === "raw") return "border-transparent bg-transparent text-inherit";
    if (variant === "outline") return "border-border bg-transparent text-copy-disabled";
    return "border-border bg-muted text-copy-disabled";
  }

  if (variant === "raw") return `border-transparent bg-transparent text-inherit ${focus}`;

  const invalidBoundary = invalid
    ? "aria-invalid:border-error-solid aria-invalid:hover:border-error-solid aria-invalid:active:border-error-solid"
    : "";

  return [intentClasses[intent][variant], focus, invalidBoundary].filter(Boolean).join(" ");
}
