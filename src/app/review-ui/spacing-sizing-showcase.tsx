import { FoundationSpecimens, type FoundationSpecimen } from "./foundation-specimens";

const spacingScale = [
  ["0", "w-0"], ["1", "w-1"], ["2", "w-2"], ["3", "w-3"], ["4", "w-4"],
  ["5", "w-5"], ["6", "w-6"], ["8", "w-8"], ["10", "w-10"], ["12", "w-12"],
  ["16", "w-16"], ["20", "w-20"], ["24", "w-24"],
] as const;

const scale = spacingScale.map(([step, width]) => ({
  label: `spacing / ${step}`,
  classes: `${width} h-2 rounded-sm bg-primary-solid`,
  properties: ["width"],
}));

const sizes: readonly FoundationSpecimen[] = [
  { label: "max-w-page", classes: "h-2 w-full max-w-page bg-surface", properties: ["max-width"] },
  { label: "max-w-reading", classes: "h-2 w-full max-w-reading bg-surface", properties: ["max-width"] },
  { label: "w-sidebar", classes: "h-2 w-sidebar max-w-full bg-surface", properties: ["width", "--spacing-sidebar"] },
  { label: "px-page-gutter", classes: "bg-surface px-page-gutter", properties: ["padding-inline-start", "padding-inline-end"], content: <div className="h-2 bg-primary-solid" /> },
  { label: "py-section", classes: "bg-surface py-section", properties: ["padding-block-start", "padding-block-end"], content: <div className="h-2 bg-primary-solid" /> },
  { label: "p-density-compact", classes: "bg-surface p-density-compact", properties: ["padding"], content: <div className="h-2 bg-primary-solid" /> },
  { label: "p-density-regular", classes: "bg-surface p-density-regular", properties: ["padding"], content: <div className="h-2 bg-primary-solid" /> },
  { label: "p-density-roomy", classes: "bg-surface p-density-roomy", properties: ["padding"], content: <div className="h-2 bg-primary-solid" /> },
  ...([
    ["xs", "size-control-xs"], ["sm", "size-control-sm"], ["md", "size-control-md"],
    ["lg", "size-control-lg"], ["xl", "size-control-xl"],
  ] as const).map(([name, classes]) => ({
    label: `control / ${name}`,
    classes: `${classes} rounded-md border border-input bg-surface`,
    properties: ["width", "height"],
  })),
];

export function SpacingSizingShowcase() {
  return (
    <section aria-labelledby="review-spacing" className="space-y-3">
      <h2 id="review-spacing" className="text-heading-sm">فاصله‌گذاری و اندازه‌ها</h2>
      <FoundationSpecimens specimens={scale} />
      <FoundationSpecimens specimens={sizes} />
    </section>
  );
}
