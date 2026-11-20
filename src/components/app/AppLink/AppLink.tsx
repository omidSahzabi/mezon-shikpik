import Link from "next/link";
import type { AppColor, AppNativeProps } from "../app-contract";
import { AppLinkAxes, AppLinkStyles } from "./AppLink.styles";

export type AppLinkProps = Omit<AppNativeProps<"a">, "href" | "target"> & {
  href: string;
  external?: boolean;
  newWindow?: boolean;
  color?: AppColor;
  variant?: (typeof AppLinkAxes.variant)[number];
  size?: (typeof AppLinkAxes.size)[number];
};

export function AppLink({
  href, external = false, newWindow = false, color = "primary", variant = "default",
  size = "body", rel, ...props
}: AppLinkProps) {
  const className = AppLinkStyles(color, variant, size);
  const target = newWindow ? "_blank" : undefined;
  const safeRel = newWindow ? [rel, "noopener", "noreferrer"].filter(Boolean).join(" ") : rel;
  const useNative = external || !href.startsWith("/") || href.startsWith("//");
  if (useNative) return <a {...props} href={href} target={target} rel={safeRel} className={className} />;
  return <Link {...props} href={href} target={target} rel={safeRel} className={className} />;
}
