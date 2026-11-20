import type { AppNativeProps } from "../app-contract";
import { AppBox, type AppBoxProps } from "../AppBox/AppBox";
import { AppContainer, type AppContainerProps } from "../AppContainer/AppContainer";
import { AppSection, type AppSectionProps } from "../AppSection/AppSection";
import { SECTION_BOX_PADDING } from "./AppSectionBox.styles";

export type AppSectionBoxProps = AppNativeProps<"section">
  & Pick<AppBoxProps, "color" | "variant" | "paddingInline" | "paddingBlock">
  & Pick<AppContainerProps, "width" | "gutters">
  & Pick<AppSectionProps, "as" | "spacing">;

export function AppSectionBox({
  as = "section", spacing = "section", width = "page", gutters = true,
  color = "raw", variant = "raw", paddingInline = SECTION_BOX_PADDING, paddingBlock = SECTION_BOX_PADDING,
  children, ...props
}: AppSectionBoxProps) {
  return (
    <AppSection {...props} as={as} spacing={spacing}>
      <AppContainer width={width} gutters={gutters}>
        <AppBox color={color} variant={variant} paddingInline={paddingInline} paddingBlock={paddingBlock}>
          {children}
        </AppBox>
      </AppContainer>
    </AppSection>
  );
}
