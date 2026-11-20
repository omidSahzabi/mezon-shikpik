import { ArrowLeft, ArrowRight, Check, ChevronDown, ChevronLeft, ChevronRight, Menu, Plus, Search, X } from "lucide-react";
import type { AppNativeProps } from "../app-contract";
import { AppIconStyles, appIconSizes } from "./AppIcon.styles";

const icons = {
  "arrow-left": ArrowLeft,
  "arrow-right": ArrowRight,
  check: Check,
  "chevron-down": ChevronDown,
  "chevron-left": ChevronLeft,
  "chevron-right": ChevronRight,
  menu: Menu,
  plus: Plus,
  search: Search,
  x: X,
} as const;

export type AppIconName = keyof typeof icons;

type IconAccessibility =
  | { decorative?: true; label?: never }
  | { decorative: false; label: string };

export type AppIconProps = Omit<AppNativeProps<"svg">, "children" | "name" | "role" | "focusable" | "aria-hidden" | "aria-label" | "viewBox" | "width" | "height" | "fill" | "stroke" | "strokeWidth" | "tabIndex">
  & IconAccessibility & { name: AppIconName; size?: (typeof appIconSizes)[number] };

export function AppIcon({ name, size = "md", decorative = true, label, ...props }: AppIconProps) {
  const Icon = icons[name];
  return (
    <Icon {...props} className={AppIconStyles({ size })}
      focusable="false" aria-hidden={decorative ? true : undefined}
      role={decorative ? undefined : "img"} aria-label={decorative ? undefined : label} />
  );
}
