import type { ComponentPropsWithRef, ElementType } from "react";
import { colorIntents, getColorVariantClasses, type ColorVariant } from "@/lib/color-variants";

export const appColors = ["raw", ...colorIntents] as const;
export type AppColor = (typeof appColors)[number];
export type AppNativeProps<T extends ElementType> = Omit<ComponentPropsWithRef<T>, "className" | "style" | "color" | "size" | "asChild">;

export const focusClasses = "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

const tones = {
  raw: ["text-inherit","border-input text-foreground","border-border bg-surface text-foreground","border-foreground bg-foreground text-background"],
  primary: ["text-primary-strong","border-primary-solid text-primary-strong","border-primary-soft-edge bg-primary-soft text-primary-strong","border-primary-solid bg-primary-solid text-primary-on-solid"],
  secondary: ["text-secondary-strong","border-secondary-solid text-secondary-strong","border-secondary-soft-edge bg-secondary-soft text-secondary-strong","border-secondary-solid bg-secondary-solid text-secondary-on-solid"],
  accent: ["text-accent-strong","border-accent-solid text-accent-strong","border-accent-soft-edge bg-accent-soft text-accent-strong","border-accent-solid bg-accent-solid text-accent-on-solid"],
  success: ["text-success-strong","border-success-solid text-success-strong","border-success-soft-edge bg-success-soft text-success-strong","border-success-solid bg-success-solid text-success-on-solid"],
  error: ["text-error-strong","border-error-solid text-error-strong","border-error-soft-edge bg-error-soft text-error-strong","border-error-solid bg-error-solid text-error-on-solid"],
  warning: ["text-warning-strong","border-warning-solid text-warning-strong","border-warning-soft-edge bg-warning-soft text-warning-strong","border-warning-solid bg-warning-solid text-warning-on-solid"],
  info: ["text-info-strong","border-info-solid text-info-strong","border-info-soft-edge bg-info-soft text-info-strong","border-info-solid bg-info-solid text-info-on-solid"],
  destructive: ["text-destructive-strong","border-destructive-solid text-destructive-strong","border-destructive-soft-edge bg-destructive-soft text-destructive-strong","border-destructive-solid bg-destructive-solid text-destructive-on-solid"],
} as const;

export function textTone(color: AppColor) {
  return tones[color][0];
}

export function surfaceTone(color: AppColor, variant: ColorVariant) {
  if (variant === "raw") return "border-transparent bg-transparent text-inherit";
  if (variant === "outline") return tones[color][1];
  if (variant === "filled") return tones[color][2];
  return tones[color][3];
}

export function actionTone(color: AppColor, variant: ColorVariant, disabled: boolean) {
  if (color !== "raw" || disabled || variant === "raw") {
    return getColorVariantClasses({ intent: color === "raw" ? undefined : color, variant, disabled });
  }
  return [
    surfaceTone(color, variant),
    focusClasses,
    variant === "fullFilled"
      ? "hover:bg-copy-secondary active:bg-copy-muted"
      : "hover:bg-muted active:border-input",
  ].join(" ");
}
