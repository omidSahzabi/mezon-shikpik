import { notFound } from "next/navigation";
import { AppComponentsShowcase } from "./app-components-showcase";
import { ColorShowcase } from "./color-showcase";
import { ResponsiveLayoutShowcase } from "./responsive-layout-showcase";
import { ShapeEffectsShowcase } from "./shape-effects-showcase";
import { SpacingSizingShowcase } from "./spacing-sizing-showcase";
import { TypographyShowcase } from "./typography-showcase";

export default function ReviewUiPage() {
  if (process.env.NODE_ENV !== "development") {
    notFound();
  }

  return (
    <main lang="fa" dir="rtl" className="mx-auto w-full max-w-page space-y-section px-page-gutter py-6 text-foreground">
      <h1 className="text-heading">بازبینی سیستم طراحی</h1>
      <ColorShowcase />
      <TypographyShowcase />
      <SpacingSizingShowcase />
      <ShapeEffectsShowcase />
      <ResponsiveLayoutShowcase />
      <AppComponentsShowcase />
    </main>
  );
}
