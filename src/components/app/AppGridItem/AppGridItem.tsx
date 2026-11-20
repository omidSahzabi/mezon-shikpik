import type { CSSProperties } from "react";
import type { AppNativeProps } from "../app-contract";
import type { GridItemOptions } from "@/lib/responsive-layout";
import type { AppGridOwner } from "../AppGrid/AppGrid";
export type AppGridItemProps = AppNativeProps<"div"> & GridItemOptions & { owner: AppGridOwner };
import { AppGridItemStyles } from "./AppGridItem.styles";

export function AppGridItem({ owner, span = 1, start = "auto", order = 0, visibility = "visible", ...props }: AppGridItemProps) {
  const layout = AppGridItemStyles(owner, { span, start, order, visibility });
  return <div {...props} className={layout.className} style={layout.style as CSSProperties} />;
}
