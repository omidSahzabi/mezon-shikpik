import type { CSSProperties } from "react";
import type { AppNativeProps } from "../app-contract";
import type { SectionSpacing } from "@/lib/responsive-layout";
import { AppSectionStyles } from "./AppSection.styles";

export type AppSectionProps = AppNativeProps<"section"> & {
  as?: "section" | "div";
  spacing?: SectionSpacing;
};

export function AppSection({ as: Tag = "section", spacing = "section", ref, ...props }: AppSectionProps) {
  const layout = AppSectionStyles(spacing);
  return <Tag {...props} ref={ref as React.Ref<HTMLElement> & React.Ref<HTMLDivElement>} className={layout.className} style={layout.style as CSSProperties} />;
}
