import type { CSSProperties } from "react";
import type { AppNativeProps } from "../app-contract";
import type { FlexOptions } from "@/lib/responsive-layout";
export type AppStackProps = AppNativeProps<"div"> & FlexOptions;
import { AppStackStyles } from "./AppStack.styles";

export function AppStack({ direction = "column", align = "stretch", justify = "start", wrap = "nowrap", gap = 4, visibility = "visible", ...props }: AppStackProps) {
  const layout = AppStackStyles({ direction, align, justify, wrap, gap, visibility });
  return <div {...props} className={layout.className} style={layout.style as CSSProperties} />;
}
