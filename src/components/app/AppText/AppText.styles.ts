import { cva } from "class-variance-authority";
import { appColors, textTone, type AppColor } from "../app-contract";

export const AppTextAxes = {
  color: appColors,
  variant: ["default", "muted", "raw"],
  size: ["body","body-lg","label","caption","helper"],
} as const;

const recipe = cva("", {
  variants: {
    size: { "body": "text-body", "body-lg": "text-body-lg", "label": "text-label", "caption": "text-caption", "helper": "text-helper" },
  },
});

export function AppTextStyles(color: AppColor, variant: (typeof AppTextAxes.variant)[number], size: (typeof AppTextAxes.size)[number]) {
  if (variant === "raw") return "";
  return recipe({ size, className: variant === "muted" ? "text-copy-muted" : textTone(color) });
}
