import { cva } from "class-variance-authority";

export const appIconSizes = ["sm", "md", "lg"] as const;
export const AppIconStyles = cva("inline-block shrink-0", {
  variants: { size: { sm: "size-4", md: "size-5", lg: "size-6" } },
  defaultVariants: { size: "md" },
});
