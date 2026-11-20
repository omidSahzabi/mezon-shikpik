import type { ComponentProps } from "react";
import { cx } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";

type ButtonProps = ComponentProps<"button"> & {
  asChild?: boolean;
  variant: string;
  size: string;
};

// Adapted from the shadcn New York v4 Button. Callers supply the theme recipe.
export function Button({ asChild = false, variant, size, className, ...nativeProps }: ButtonProps) {
  const Element = asChild ? Slot : "button";

  return (
    <Element
      {...nativeProps}
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cx("[&_svg]:pointer-events-none [&_svg]:shrink-0", className)}
    />
  );
}
