import type { AppColor, AppNativeProps } from "../app-contract";
import type { ColorVariant } from "@/lib/color-variants";
import { Button } from "@/components/ui/button";
import { AppButtonAxes, AppButtonStyles } from "./AppButton.styles";

type AppButtonOptions = AppNativeProps<"button"> & {
  color?: AppColor;
  variant?: ColorVariant;
  size?: (typeof AppButtonAxes.size)[number];
  loading?: boolean;
};

export type AppButtonProps = AppButtonOptions & (
  | { iconOnly?: false }
  | { iconOnly: true; "aria-label": string }
);

export function AppButton({
  type = "button", color = "primary", variant = "fullFilled", size = "md",
  loading = false, disabled = false, iconOnly = false, children, "aria-busy": busy, ...props
}: AppButtonProps) {
  const unavailable = disabled || loading;
  return (
    <Button {...props} variant={variant} size={size} type={type} disabled={unavailable} aria-busy={loading || busy}
      data-loading={loading ? "" : undefined} className={AppButtonStyles(color, variant, size, unavailable, iconOnly)}>
      <span className={loading ? "inline-flex min-w-0 items-center justify-center gap-2 opacity-0" : "inline-flex min-w-0 items-center justify-center gap-2"}>{children}</span>
      {loading && <span aria-hidden="true" className="absolute size-4 rounded-pill border-2 border-current border-e-transparent motion-safe:animate-spin" />}
    </Button>
  );
}
