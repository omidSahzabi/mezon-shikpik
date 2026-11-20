import type { AppNativeProps } from "../app-contract";
import { AppHeadingStyles, AppHeadingAxes } from "./AppHeading.styles";

const headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] as const;
export type AppHeadingProps = AppNativeProps<"h1"> & {
  level: 1 | 2 | 3 | 4 | 5 | 6;
  variant?: (typeof AppHeadingAxes.variant)[number];
  size?: (typeof AppHeadingAxes.size)[number];
};

export function AppHeading({ level, variant = "default", size = "heading", ...props }: AppHeadingProps) {
  const Tag = headings[level - 1];
  return <Tag {...props} className={AppHeadingStyles("raw", variant, size)} />;
}
