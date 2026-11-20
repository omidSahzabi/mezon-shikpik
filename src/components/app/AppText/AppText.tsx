import type { AppNativeProps, AppColor } from "../app-contract";
import { AppTextStyles, AppTextAxes } from "./AppText.styles";

export type AppTextProps = AppNativeProps<"p"> & {
  as?: "p" | "span" | "small";
  color?: AppColor;
  variant?: (typeof AppTextAxes.variant)[number];
  size?: (typeof AppTextAxes.size)[number];
};

export function AppText({ as: Tag = "p", color = "raw", variant = "default", size = "body", ...props }: AppTextProps) {
  
  return <Tag {...props} className={AppTextStyles(color, variant, size)} />;
}
