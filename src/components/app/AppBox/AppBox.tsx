import type { CSSProperties } from "react";
import type { AppColor, AppNativeProps } from "../app-contract";
import type { ColorVariant } from "@/lib/color-variants";
import type { Responsive, SpacingStep, Visibility } from "@/lib/responsive-layout";
import { appBoxStyles } from "./AppBox.styles";

type SemanticTag = "article" | "aside" | "main" | "header" | "footer";

type BoxOptions = {
  color?: AppColor;
  variant?: ColorVariant;
  paddingInline?: SpacingStep;
  paddingBlock?: SpacingStep;
  visibility?: Responsive<Visibility>;
};

export type AppBoxProps = BoxOptions & (
  | (AppNativeProps<"div"> & { as?: "div" })
  | (AppNativeProps<SemanticTag> & { as: SemanticTag })
);

export function AppBox(props: AppBoxProps) {
  const { color, variant, paddingInline, paddingBlock, visibility, ...nativeProps } = props;
  const { className, style } = appBoxStyles({ color, variant, paddingInline, paddingBlock, visibility });

  if (nativeProps.as === undefined || nativeProps.as === "div") {
    const { as: Tag = "div", ...native } = nativeProps;
    return <Tag {...native} className={className} style={style as CSSProperties} />;
  }

  const { as: Tag, ...native } = nativeProps;
  return <Tag {...native} className={className} style={style as CSSProperties} />;
}
