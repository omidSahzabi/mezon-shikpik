import type { AppNativeProps } from "../app-contract";
import type { ContainerWidth } from "@/lib/responsive-layout";
import { AppContainerStyles } from "./AppContainer.styles";

export type AppContainerProps = AppNativeProps<"div"> & {
  width?: ContainerWidth;
  gutters?: boolean;
};

export function AppContainer({ width = "page", gutters = true, ...props }: AppContainerProps) {
  return <div {...props} className={AppContainerStyles({ width, gutters })} />;
}
