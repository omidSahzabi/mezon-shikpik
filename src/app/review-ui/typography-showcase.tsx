import { FoundationSpecimens, type FoundationSpecimen } from "./foundation-specimens";

const typeMetrics = ["font-family", "font-size", "line-height", "font-weight", "letter-spacing"];
const familyMetrics = ["font-family", "font-weight"];

const roles = [
  { label: "text-display", classes: "text-display", content: "دوخت و طراحی" },
  { label: "text-heading", classes: "text-heading", content: "آموزش الگوسازی" },
  { label: "text-heading-sm", classes: "text-heading-sm", content: "اندازه‌گیری دقیق" },
  { label: "text-title", classes: "text-title", content: "الگوی مانتو" },
  { label: "text-body-lg", classes: "text-body-lg", content: "آموزش را از اندازه‌گیری و ثبت ابعاد پارچه شروع کنید." },
  { label: "text-body", classes: "text-body", content: "به اندازهٔ ۱۲٫۵ سانتی‌متر برش بزنید و خط دوخت را علامت‌گذاری کنید." },
  { label: "text-label", classes: "text-label", content: "عرض پارچه" },
  { label: "text-caption", classes: "text-caption", content: "نمونهٔ شمارهٔ ۳" },
  { label: "text-helper", classes: "text-helper", content: "اندازه را به سانتی‌متر وارد کنید." },
].map((role) => ({ ...role, properties: typeMetrics }));

const families: readonly FoundationSpecimen[] = [
  { label: "font-sans / font-normal", classes: "font-sans font-normal", properties: familyMetrics, content: "الگو و پارچه ۱۲۳" },
  { label: "font-sans / font-medium", classes: "font-sans font-medium", properties: familyMetrics, content: "الگو و پارچه ۱۲۳" },
  { label: "font-sans / font-bold", classes: "font-sans font-bold", properties: familyMetrics, content: "الگو و پارچه ۱۲۳" },
  { label: "font-sans / Latin", classes: "font-sans font-normal", properties: familyMetrics, content: "Pattern 123", direction: "ltr", language: "en" },
  { label: "font-sans / technical identifier", classes: "font-sans break-all", properties: familyMetrics, content: "/patterns/MSP-0123", direction: "ltr" },
  {
    label: "text-body / mixed direction",
    classes: "text-body tracking-copy",
    properties: typeMetrics,
    content: <>الگوی <bdi dir="ltr">MSP-0123</bdi> با عرض ۱۲٫۵ سانتی‌متر</>,
  },
];

export function TypographyShowcase() {
  return (
    <section aria-labelledby="review-typography" className="space-y-3">
      <h2 id="review-typography" className="text-heading-sm">نوشتار</h2>
      <FoundationSpecimens specimens={roles} />
      <FoundationSpecimens specimens={families} />
    </section>
  );
}
