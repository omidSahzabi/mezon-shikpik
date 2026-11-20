import Image, { type ImageProps } from "next/image";
import { AppImageStyles, appImageVariants } from "./AppImage.styles";

type ImageDimensions =
  | { fill: true; sizes: string; width?: never; height?: never }
  | { fill?: false; sizes?: string; width: NonNullable<ImageProps["width"]>; height: NonNullable<ImageProps["height"]> };

export type AppImageProps = Omit<ImageProps, "className" | "style" | "fill" | "sizes" | "width" | "height">
  & ImageDimensions & { variant?: (typeof appImageVariants)[number] };

export function AppImage({ variant = "default", alt, ...props }: AppImageProps) {
  return <Image {...props} alt={alt} className={AppImageStyles({ variant, fill: props.fill ?? false })} />;
}
