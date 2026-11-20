import { cva } from "class-variance-authority";
import { appColors, focusClasses, textTone, type AppColor } from "../app-contract";

export const AppLinkAxes = { color: appColors, variant: ["default", "muted", "raw"], size: ["body", "label"] } as const;
const recipe = cva("underline underline-offset-2 hover:no-underline", {
  variants: { size: { body: "text-body", label: "text-label" } },
});

export function AppLinkStyles(color: AppColor, variant: (typeof AppLinkAxes.variant)[number], size: (typeof AppLinkAxes.size)[number]) {
  if (variant === "raw") return `underline underline-offset-2 ${focusClasses}`;
  return recipe({ size, className: [focusClasses, variant === "muted" ? "text-copy-muted" : textTone(color)] });
}
