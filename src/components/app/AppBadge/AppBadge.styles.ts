import { cva } from "class-variance-authority";
import { colorVariants, type ColorVariant } from "@/lib/color-variants";
import { appColors, surfaceTone, type AppColor } from "../app-contract";

export const AppBadgeAxes = { color: appColors, variant: colorVariants, size: ["sm", "md"] } as const;
const recipe = cva("inline-flex max-w-full items-center break-words", {
  variants: {
    size: { sm: "text-caption", md: "text-label" },
    decorated: { true: "rounded-pill border px-2 py-1", false: "" },
  },
});

export function AppBadgeStyles(color: AppColor, variant: ColorVariant, size: (typeof AppBadgeAxes.size)[number]) {
  return recipe({ size, decorated: variant !== "raw", className: surfaceTone(color, variant) });
}
