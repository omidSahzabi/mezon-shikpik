import type { CSSProperties } from "react";
import {
  BREAKPOINTS,
  resolveContainer,
  resolveFlex,
  resolveGrid,
  resolveGridItem,
  resolveSection,
  resolveVisibility,
} from "@/lib/responsive-layout";

const tile = "min-w-0 break-words rounded-md border border-border bg-card p-2 text-label text-card-foreground";
const frame = "min-w-0 space-y-2 rounded-lg border border-border bg-surface p-3 text-foreground";

const defaultGrid = resolveGrid();
const customGrid = resolveGrid({ columns: { sm: 3, lg: 6, xxl: 14 }, gap: { base: 2, lg: 4 } });
const placedItem = resolveGridItem(customGrid, { span: { sm: 2 }, start: { sm: 2 } });
const orderedItem = resolveGridItem(customGrid, { order: { lg: -1 } });
const nestedItem = resolveGridItem(customGrid, { span: "full" });
const nestedGrid = resolveGrid({ columns: { sm: 2 }, gap: 1 });
const directionGrid = resolveGrid({ columns: 2, gap: 2 });
const logicalStart = resolveGridItem(directionGrid, { start: 1 });
const stack = resolveFlex({
  direction: { base: "column", md: "row" },
  align: { base: "stretch", md: "center" },
  justify: { md: "between" },
  wrap: { md: "wrap" },
  gap: { base: 2, md: 4 },
});
const visibleFromMd = resolveVisibility({ base: "hidden", md: "visible" });
const visibleBelowMd = resolveVisibility({ md: "hidden" });
const responsiveSection = resolveSection();
const compactSection = resolveSection(3);

function Columns({ grid }: { grid: ReturnType<typeof resolveGrid> }) {
  return (
    <dl dir="ltr" className="flex flex-wrap gap-2 text-caption text-copy-secondary">
      {BREAKPOINTS.map((breakpoint) => (
        <div key={breakpoint} className="flex gap-1">
          <dt>{breakpoint}</dt>
          <dd>{grid.columns[breakpoint]}</dd>
        </div>
      ))}
    </dl>
  );
}

export function ResponsiveLayoutShowcase() {
  return (
    <section aria-labelledby="review-responsive-layout" className="min-w-0 space-y-4">
      <h2 id="review-responsive-layout" className="text-heading-sm">چیدمان واکنش‌گرا</h2>
      <p className="text-helper">
        نقطهٔ شکست فعال <bdi dir="ltr" className="layout-breakpoint text-label" />
      </p>

      <div className={frame}>
        <h3 className="text-title">شبکهٔ پیش‌فرض</h3>
        <Columns grid={defaultGrid} />
        <p className="text-helper text-copy-secondary">سه آیتم با تعداد ستون مستقل. در عرض کم، آیتم‌ها به ردیف بعد می‌روند.</p>
        <div className={defaultGrid.className} style={defaultGrid.style as CSSProperties}>
          {["۱", "۲", "۳"].map((label) => <div key={label} className={tile}>{label}</div>)}
        </div>
      </div>

      <div className={frame}>
        <h3 className="text-title">بازنویسی پراکنده و شبکهٔ تو در تو</h3>
        <Columns grid={customGrid} />
        <p className="text-helper text-copy-secondary">
          ستون، فاصله و جای‌گذاری تا نقطهٔ شکست بعدی به ارث می‌رسند.
        </p>
        <div className={customGrid.className} style={customGrid.style as CSSProperties}>
          <div className={`${placedItem.className} ${tile}`} style={placedItem.style as CSSProperties}>
            <bdi dir="ltr">sm: start 2 / span 2</bdi>
          </div>
          <div className={`${orderedItem.className} ${tile}`} style={orderedItem.style as CSSProperties}>
            <bdi dir="ltr">lg: order −1</bdi>
          </div>
          <div className={`${nestedItem.className} ${tile}`} style={nestedItem.style as CSSProperties}>
            <p className="mb-2"><bdi dir="ltr">span: full · gap: 1</bdi></p>
            <Columns grid={nestedGrid} />
            <div className={nestedGrid.className} style={nestedGrid.style as CSSProperties}>
              <div className={tile}>الف</div>
              <div className={tile}>ب</div>
            </div>
          </div>
        </div>
        <p dir="ltr" className="text-caption text-copy-secondary">gap: base 2 / lg 4 · nested gap: 1</p>
      </div>

      <div className="grid min-w-0 gap-3 sm:grid-cols-2">
        {(["rtl", "ltr"] as const).map((dir) => (
          <div key={dir} className={frame}>
            <h3 className="text-title"><bdi dir="ltr">{dir.toUpperCase()}</bdi></h3>
            <div dir={dir} className={directionGrid.className} style={directionGrid.style as CSSProperties}>
              <div className={`${logicalStart.className} ${tile}`} style={logicalStart.style as CSSProperties}>
                <bdi dir="ltr">start 1</bdi>
              </div>
              <div className={tile}><bdi dir="ltr">auto</bdi></div>
            </div>
          </div>
        ))}
      </div>

      <div className={frame}>
        <h3 className="text-title">ظرف و فاصلهٔ بخش</h3>
        <div className={resolveContainer()}>
          <div className={responsiveSection.className}>
            <div className={tile}><bdi dir="ltr">page / responsive gutters / section</bdi></div>
          </div>
        </div>
        <div className={resolveContainer({ width: "reading", gutters: false })}>
          <div className={compactSection.className} style={compactSection.style as CSSProperties}>
            <div className={tile}><bdi dir="ltr">reading / no gutters / section step 3</bdi></div>
          </div>
        </div>
        <div className={resolveContainer({ width: "fluid", gutters: false })}>
          <div className={tile}><bdi dir="ltr">fluid / no gutters</bdi></div>
        </div>
      </div>

      <div className={frame}>
        <h3 className="text-title">جریان و نمایش واکنش‌گرا</h3>
        <p dir="ltr" className="text-caption text-copy-secondary">base: column / md: row, wrap, between</p>
        <div className={stack.className} style={stack.style as CSSProperties}>
          <div className={tile}>آیتم اول</div>
          <div className={`${visibleBelowMd.className} ${tile}`} style={visibleBelowMd.style as CSSProperties}>
            <bdi dir="ltr">visible below md</bdi>
          </div>
          <div className={`${visibleFromMd.className} ${tile}`} style={visibleFromMd.style as CSSProperties}>
            <bdi dir="ltr">visible from md</bdi>
          </div>
          <div className={tile}>آیتم آخر</div>
        </div>
      </div>
    </section>
  );
}
