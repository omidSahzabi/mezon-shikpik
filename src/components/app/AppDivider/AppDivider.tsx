import type { AppNativeProps } from "../app-contract";
import { AppDividerStyles } from "./AppDivider.styles";

export type AppDividerProps =
  | (AppNativeProps<"hr"> & { decorative?: false; orientation?: "horizontal" })
  | (AppNativeProps<"span"> & { decorative: true; orientation?: "horizontal" | "vertical" });

export function AppDivider(props: AppDividerProps) {
  if (props.decorative) {
    const { decorative, orientation = "horizontal", ...span } = props;
    return <span {...span} aria-hidden={decorative} className={AppDividerStyles({ orientation })} />;
  }
  const { decorative, orientation, ...rule } = props;
  return <hr {...rule} data-decorative={decorative} className={AppDividerStyles({ orientation })} />;
}
