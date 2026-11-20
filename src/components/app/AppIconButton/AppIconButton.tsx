import { AppButton, type AppButtonProps } from "../AppButton/AppButton";
import { AppIcon, type AppIconName } from "../AppIcon/AppIcon";
import { AppIconButtonAxes } from "./AppIconButton.styles";

export type AppIconButtonProps = Omit<AppButtonProps, "children" | "aria-label" | "iconOnly" | "size"> & {
  label: string;
  icon: AppIconName;
  size?: (typeof AppIconButtonAxes.size)[number];
};

export function AppIconButton({ label, icon, color = "raw", variant = "raw", size = "md", ...props }: AppIconButtonProps) {
  return (
    <AppButton {...props} aria-label={label} color={color} variant={variant} size={size} iconOnly>
      <AppIcon name={icon} size={size === "lg" ? "md" : "sm"} />
    </AppButton>
  );
}
