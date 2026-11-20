import { cva } from "class-variance-authority";
import { colorVariants } from "@/lib/color-variants";
import { resolveVisibility } from "@/lib/responsive-layout";
import { appColors, surfaceTone } from "../app-contract";
import type { AppBoxProps } from "./AppBox";

export const AppBoxAxes = { color: appColors, variant: colorVariants } as const;

export const blockPadding = {
  0: "py-0", 1: "py-1", 2: "py-2", 3: "py-3", 4: "py-4", 5: "py-5", 6: "py-6",
  8: "py-8", 10: "py-10", 12: "py-12", 16: "py-16", 20: "py-20", 24: "py-24",
} as const;
export const inlinePadding = {
  0: "px-0", 1: "px-1", 2: "px-2", 3: "px-3", 4: "px-4", 5: "px-5", 6: "px-6",
  8: "px-8", 10: "px-10", 12: "px-12", 16: "px-16", 20: "px-20", 24: "px-24",
} as const;

const recipe = cva("min-w-0", {
  variants: {
    variant: { raw: "", outline: "rounded-xl border", filled: "rounded-xl border", fullFilled: "rounded-xl border" },
  },
});

export function appBoxStyles({ color = "raw", variant = "raw", paddingInline = 0, paddingBlock = 0, visibility }: AppBoxProps) {
  const layout = resolveVisibility(visibility);
  return {
    style: layout.style,
    className: recipe({ variant, className: [layout.className, surfaceTone(color, variant), inlinePadding[paddingInline], blockPadding[paddingBlock]] }),
  };
}
