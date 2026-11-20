import type { ReactNode } from "react";
import { AppText } from "@/components/app/AppText/AppText";
import { AppHeading } from "@/components/app/AppHeading/AppHeading";
import { AppBox } from "@/components/app/AppBox/AppBox";
import { AppContainer } from "@/components/app/AppContainer/AppContainer";
import { AppSection } from "@/components/app/AppSection/AppSection";
import { AppSectionBox } from "@/components/app/AppSectionBox/AppSectionBox";
import { AppStack } from "@/components/app/AppStack/AppStack";
import { AppGrid, createAppGridOwner } from "@/components/app/AppGrid/AppGrid";
import { AppGridItem } from "@/components/app/AppGridItem/AppGridItem";
import { AppDivider } from "@/components/app/AppDivider/AppDivider";
import { AppIcon } from "@/components/app/AppIcon/AppIcon";
import { AppImage } from "@/components/app/AppImage/AppImage";
import { AppBadge } from "@/components/app/AppBadge/AppBadge";
import { AppLink } from "@/components/app/AppLink/AppLink";
import { AppButton } from "@/components/app/AppButton/AppButton";
import { AppIconButton } from "@/components/app/AppIconButton/AppIconButton";
import { AppTextAxes } from "@/components/app/AppText/AppText.styles";
import { AppHeadingAxes } from "@/components/app/AppHeading/AppHeading.styles";
import { AppBoxAxes } from "@/components/app/AppBox/AppBox.styles";
import { AppSectionBoxAxes } from "@/components/app/AppSectionBox/AppSectionBox.styles";
import { AppBadgeAxes } from "@/components/app/AppBadge/AppBadge.styles";
import { AppLinkAxes } from "@/components/app/AppLink/AppLink.styles";
import { AppButtonAxes } from "@/components/app/AppButton/AppButton.styles";
import { AppIconButtonAxes } from "@/components/app/AppIconButton/AppIconButton.styles";
import { AppContainerWidths } from "@/components/app/AppContainer/AppContainer.styles";
import { appIconSizes } from "@/components/app/AppIcon/AppIcon.styles";
import { appImageVariants } from "@/components/app/AppImage/AppImage.styles";

type MatrixAxes<C extends string, V extends string, S extends string | undefined> = {
  color: readonly C[];
  variant: readonly V[];
  size: readonly S[];
};

function matrix<C extends string, V extends string, S extends string | undefined>(
  axes: MatrixAxes<C, V, S>,
  render: (selection: { color: C; variant: V; size: S }) => ReactNode,
) {
  return axes.color.flatMap((color) => axes.variant.flatMap((variant) => axes.size.map((size) => {
    const label = [color, variant, size].filter(Boolean).join(" / ");
    return (
      <li key={label} className="min-w-0 space-y-1 rounded-md border border-border p-2">
        <bdi dir="ltr" className="block break-words text-caption text-copy-secondary">{label}</bdi>
        {render({ color, variant, size })}
      </li>
    );
  })));
}

function specimen(label: string, content: ReactNode) {
  return (
    <li key={label} className="min-w-0 space-y-1 rounded-md border border-border p-2">
      <bdi dir="ltr" className="block break-words text-caption text-copy-secondary">{label}</bdi>
      {content}
    </li>
  );
}

const owner = createAppGridOwner({ columns: { base: 2, md: 4 }, gap: 2 });
const withoutSize = [undefined] as const;
const previewText = "نمونهٔ دوخت";

const appPreviews = {
  AppText: () => matrix(AppTextAxes, (props) => <AppText {...props}>{previewText}</AppText>),
  AppHeading: () => matrix(AppHeadingAxes, ({ size, variant }) => <AppHeading level={5} size={size} variant={variant}>{previewText}</AppHeading>),
  AppBox: () => matrix({ ...AppBoxAxes, size: withoutSize }, ({ color, variant }) => (
    <AppBox color={color} variant={variant} paddingInline={2} paddingBlock={2}>{previewText}</AppBox>
  )),
  AppContainer: () => AppContainerWidths.flatMap((width) => [true, false].map((gutters) =>
    specimen(`${width} / gutters ${gutters}`, <AppContainer width={width} gutters={gutters}>{previewText}</AppContainer>),
  )),
  AppSection: () => [
    specimen("section", <AppSection aria-label="نمونهٔ بخش">{previewText}</AppSection>),
    specimen("none", <AppSection as="div" spacing="none">{previewText}</AppSection>),
    specimen("spacing step 3", <AppSection as="div" spacing={3}>{previewText}</AppSection>),
  ],
  AppSectionBox: () => matrix({ ...AppSectionBoxAxes, size: withoutSize }, ({ color, variant }) => (
    <AppSectionBox as="div" spacing="none" gutters={false} color={color} variant={variant}>{previewText}</AppSectionBox>
  )),
  AppStack: () => [
    specimen("column", <AppStack gap={2}><AppText>الف</AppText><AppText>ب</AppText></AppStack>),
    specimen("row / wrap", <AppStack direction="row" wrap="wrap" gap={2}><AppText>الف</AppText><AppText>ب</AppText></AppStack>),
    specimen("column → row / RTL", <AppStack dir="rtl" direction={{ base: "column", md: "row" }} gap={2}><AppText>۱</AppText><AppText>۲</AppText></AppStack>),
    specimen("column → row / LTR", <AppStack dir="ltr" direction={{ base: "column", md: "row" }} gap={2}><AppText>1</AppText><AppText>2</AppText></AppStack>),
  ],
  AppGrid: () => [
    specimen("default tracks", <AppGrid><AppText>۱</AppText><AppText>۲</AppText></AppGrid>),
    specimen("custom tracks", <AppGrid owner={owner}><AppText>۱</AppText><AppText>۲</AppText></AppGrid>),
  ],
  AppGridItem: () => (["rtl", "ltr"] as const).map((dir) => specimen(`logical start / ${dir}`, (
    <AppGrid owner={owner} dir={dir}>
      <AppGridItem owner={owner} start={1}>۱</AppGridItem>
      <AppGridItem owner={owner} span="full">عرض کامل</AppGridItem>
    </AppGrid>
  ))),
  AppDivider: () => [
    specimen("native horizontal", <AppDivider />),
    specimen("decorative horizontal", <AppDivider decorative />),
    specimen("decorative vertical", <AppStack direction="row"><AppText>الف</AppText><AppDivider decorative orientation="vertical" /><AppText>ب</AppText></AppStack>),
  ],
  AppIcon: () => appIconSizes.flatMap((size) => [
    specimen(`${size} / decorative`, <AppIcon name="check" size={size} />),
    specimen(`${size} / labeled`, <AppIcon name="check" size={size} decorative={false} label="تأیید" />),
  ]),
  AppImage: () => appImageVariants.flatMap((variant) => [
    specimen(`${variant} / intrinsic`, <AppImage src="/favicon.ico" alt="نشان نمونه" width={48} height={48} unoptimized variant={variant} />),
    specimen(`${variant} / fill`, (
      <div className="relative size-control-lg">
        <AppImage src="/favicon.ico" alt="" fill sizes="3rem" unoptimized variant={variant} />
      </div>
    )),
  ]),
  AppBadge: () => matrix(AppBadgeAxes, (props) => <AppBadge {...props}>آماده</AppBadge>),
  AppLink: () => matrix(AppLinkAxes, (props) => <AppLink {...props} href="#review-app-components">{previewText}</AppLink>),
  AppButton: () => [
    ...matrix(AppButtonAxes, (props) => <AppButton {...props}>{previewText}</AppButton>),
    specimen("disabled", <AppButton disabled>غیرفعال</AppButton>),
    specimen("loading", <AppButton loading>در حال ذخیره</AppButton>),
    specimen("pressed", <AppButton aria-pressed={true}>انتخاب‌شده</AppButton>),
  ],
  AppIconButton: () => [
    ...matrix(AppIconButtonAxes, (props) => <AppIconButton {...props} icon="check" label="تأیید" />),
    specimen("disabled", <AppIconButton icon="check" label="تأیید" disabled />),
    specimen("loading", <AppIconButton icon="check" label="تأیید" loading />),
    specimen("pressed", <AppIconButton icon="check" label="تأیید" aria-pressed={true} />),
  ],
};

export function AppComponentsShowcase() {
  return (
    <section id="review-app-components" aria-labelledby="review-app-components-heading" className="space-y-4">
      <AppHeading id="review-app-components-heading" level={2} size="heading-sm">اجزای پایه</AppHeading>
      <AppText size="helper" variant="muted">برای بررسی حالت‌های تعاملی از نشانگر، فشار و کلید Tab استفاده کنید.</AppText>
      {(["light", "dark"] as const).map((theme) => (
        <div key={theme} className={`${theme} space-y-4 rounded-xl border border-border bg-background p-3 text-foreground`}>
          <AppHeading level={3} size="title">{theme === "light" ? "تم روشن" : "تم تیره"}</AppHeading>
          {Object.entries(appPreviews).map(([name, render]) => (
            <section key={name} aria-label={name} className="space-y-2">
              <AppHeading level={4} size="title"><bdi dir="ltr">{name}</bdi></AppHeading>
              <ul className="grid min-w-0 gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">{render()}</ul>
            </section>
          ))}
        </div>
      ))}
    </section>
  );
}
