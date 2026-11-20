import type { CSSProperties } from "react";
import type { AppNativeProps } from "../app-contract";
import type { GridOptions } from "@/lib/responsive-layout";
export type AppGridProps = AppNativeProps<"div"> & (
  | (GridOptions & { owner?: never })
  | { owner: AppGridOwner; columns?: never; gap?: never; visibility?: never }
);
import { AppGridStyles } from "./AppGrid.styles";
import type { AppGridOwner } from "./AppGrid.styles";
export { createAppGridOwner, type AppGridOwner } from "./AppGrid.styles";
export function AppGrid({ owner, columns, gap, visibility, ...props }: AppGridProps) {
  const layout = AppGridStyles(owner ?? { columns, gap, visibility });
  return <div {...props} className={layout.className} style={layout.style as CSSProperties} />;
}
