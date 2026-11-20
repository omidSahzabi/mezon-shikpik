import { cva } from "class-variance-authority";
import { colorVariants, type ColorVariant } from "@/lib/color-variants";
import { actionTone, appColors, type AppColor } from "../app-contract";

export const AppButtonAxes = { color: appColors, variant: colorVariants, size: ["sm", "md", "lg"] } as const;

const recipe = cva(
  "relative inline-flex min-w-0 items-center justify-center gap-2 rounded-md border text-label transition-colors duration-standard ease-standard disabled:cursor-not-allowed aria-pressed:underline aria-pressed:underline-offset-2",
  {
    variants: {
      size: { sm: "min-h-control-sm", md: "min-h-control-md", lg: "min-h-control-lg" },
      iconOnly: { true: "shrink-0 p-0 aria-pressed:ring-2 aria-pressed:ring-current", false: "px-3 py-2" },
    },
    compoundVariants: [
      { size: "sm", iconOnly: true, class: "min-w-control-sm" },
      { size: "md", iconOnly: true, class: "min-w-control-md" },
      { size: "lg", iconOnly: true, class: "min-w-control-lg" },
    ],
  },
);

export function AppButtonStyles(color: AppColor, variant: ColorVariant, size: (typeof AppButtonAxes.size)[number], disabled: boolean, iconOnly: boolean) {
  return recipe({ size, iconOnly, className: actionTone(color, variant, disabled) });
}
