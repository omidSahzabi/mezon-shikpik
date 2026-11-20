import type { AppColor, AppNativeProps } from "../app-contract";
import { AppBadgeAxes, AppBadgeStyles } from "./AppBadge.styles";
import type { ColorVariant } from "@/lib/color-variants";

export type AppBadgeProps = AppNativeProps<"span"> & {
  color?: AppColor;
  variant?: ColorVariant;
  size?: (typeof AppBadgeAxes.size)[number];
};

export function AppBadge({ color = "raw", variant = "filled", size = "sm", ...props }: AppBadgeProps) {
  return <span {...props} className={AppBadgeStyles(color, variant, size)} />;
}
