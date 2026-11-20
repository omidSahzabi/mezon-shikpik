import { cva } from "class-variance-authority";
import { textTone, type AppColor } from "../app-contract";

export const AppHeadingAxes = {
  color: ["raw"] as const,
  variant: ["default", "muted", "raw"],
  size: ["heading","heading-sm","title","display"],
} as const;

const recipe = cva("", {
  variants: {
    size: { "heading": "text-heading", "heading-sm": "text-heading-sm", "title": "text-title", "display": "text-display" },
  },
});

export function AppHeadingStyles(color: AppColor, variant: (typeof AppHeadingAxes.variant)[number], size: (typeof AppHeadingAxes.size)[number]) {
  if (variant === "raw") return "";
  return recipe({ size, className: variant === "muted" ? "text-copy-muted" : textTone(color) });
}
