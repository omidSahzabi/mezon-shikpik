import { FoundationSpecimens, type FoundationSpecimen } from "./foundation-specimens";

const shapes: readonly FoundationSpecimen[] = [
  ...([
    "rounded-sm", "rounded-md", "rounded-lg", "rounded-xl", "rounded-section", "rounded-pill",
  ] as const).map((utility) => ({
    label: utility,
    classes: `${utility} h-control-sm w-control-xl border border-input bg-surface`,
    properties: ["border-top-left-radius"],
  })),
  ...([
    ["border", "--border-width-default"],
    ["border-2", "--border-width-emphasis"],
    ["border-4", "--border-width-marker"],
  ] as const).map(([utility, variable]) => ({
    label: utility,
    classes: `${utility} h-control-sm w-control-xl rounded-md border-input bg-surface`,
    properties: ["border-top-width", variable],
  })),
];

const surfaces: readonly FoundationSpecimen[] = [
  ...(["shadow-none", "shadow-surface", "shadow-floating", "shadow-modal"] as const).map((utility) => ({
    label: utility,
    classes: `${utility} h-control-sm w-control-xl rounded-md border border-border bg-card`,
    properties: ["box-shadow"],
  })),
  { label: "bg-overlay", classes: "h-control-sm w-control-xl rounded-md bg-overlay", properties: ["background-color"] },
  { label: "opacity-muted", classes: "h-control-sm w-control-xl rounded-md bg-primary-solid opacity-muted", properties: ["opacity"] },
  {
    label: "surface-glass / backdrop-blur-glass",
    classes: "surface-glass rounded-md border border-border p-2",
    properties: ["background-color", "backdrop-filter", "--effect-opacity-glass"],
    content: <div aria-hidden="true" className="backdrop-blur-glass h-2" />,
  },
];

const motion = [
  ["duration-fast", "ease-standard"],
  ["duration-standard", "ease-enter"],
  ["duration-slow", "ease-exit"],
] as const;

const motionSpecimens = motion.flatMap(([duration], index) =>
  motion.map(([, easing]) => ({
    label: `${duration} / ${easing}`,
    classes: `${duration} ${easing} effect-hover-lift effect-active-press transition-transform rounded-md border border-input bg-surface px-3 py-2 text-label focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring`,
    properties: [
      "transition-duration",
      "transition-timing-function",
      ...(index === 0 ? ["--effect-lift", "--effect-press-scale"] : []),
    ],
    content: "نمونهٔ حرکت",
  })),
);

export function ShapeEffectsShowcase() {
  return (
    <section aria-labelledby="review-shape-effects" className="space-y-3">
      <h2 id="review-shape-effects" className="text-heading-sm">شکل و جلوه‌ها</h2>
      <FoundationSpecimens specimens={shapes} />
      <div className="grid gap-4 lg:grid-cols-2">
        {(["light", "dark"] as const).map((theme) => (
          <div key={theme} className={`${theme} space-y-3 rounded-lg bg-background p-3 text-foreground`}>
            <h3 className="text-title">{theme === "light" ? "تم روشن" : "تم تیره"}</h3>
            <FoundationSpecimens specimens={surfaces} />
          </div>
        ))}
      </div>
      <h3 className="text-title">حرکت</h3>
      <p className="text-helper text-copy-secondary">
        نشانگر را روی نمونه ببرید یا آن را فشار دهید. با فعال کردن کاهش حرکت، جابه‌جایی و تغییر اندازه متوقف می‌شوند.
      </p>
      <FoundationSpecimens specimens={motionSpecimens} interactive />
    </section>
  );
}
