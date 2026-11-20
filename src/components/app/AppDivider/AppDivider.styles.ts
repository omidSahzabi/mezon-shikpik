import { cva } from "class-variance-authority";

export const AppDividerStyles = cva("border-0 border-border", {
  variants: { orientation: { horizontal: "block w-full border-bs", vertical: "inline-block self-stretch border-s" } },
  defaultVariants: { orientation: "horizontal" },
});
