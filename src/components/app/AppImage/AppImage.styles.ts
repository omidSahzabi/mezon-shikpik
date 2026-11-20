import { cva } from "class-variance-authority";

export const appImageVariants = ["default", "rounded"] as const;
export const AppImageStyles = cva("object-contain", {
  variants: {
    variant: { default: "", rounded: "rounded-xl" },
    fill: { false: "h-auto max-w-full", true: "" },
  },
  defaultVariants: { variant: "default", fill: false },
});
