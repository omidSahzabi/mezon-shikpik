export const BREAKPOINTS = ["base", "sm", "md", "lg", "xl", "xxl"] as const;
export type Breakpoint = (typeof BREAKPOINTS)[number];
export type Responsive<T> = T | Readonly<Partial<Record<Breakpoint, T>>>;
export type ResolvedResponsive<T> = Readonly<Record<Breakpoint, T>>;

export const TAILWIND_BREAKPOINTS = {
  base: null, sm: "sm", md: "md", lg: "lg", xl: "xl", xxl: "2xl",
} as const satisfies Record<Breakpoint, string | null>;

export const DEFAULT_GRID_COLUMNS = {
  base: 1, sm: 2, md: 4, lg: 6, xl: 8, xxl: 12,
} as const satisfies ResolvedResponsive<number>;

export const SPACING_STEPS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24] as const;
export type SpacingStep = (typeof SPACING_STEPS)[number];
export type Visibility = "visible" | "hidden";
export type ContainerWidth = "page" | "reading" | "fluid";
export type SectionSpacing = "none" | "section" | SpacingStep;

type LayoutStyle = Record<`--layout-${string}`, string | number>;

export function resolveResponsive<T extends string | number>(
  input: Responsive<T> | undefined,
  fallback: T,
): ResolvedResponsive<T> {
  const resolved = {} as Record<Breakpoint, T>;
  let previous = fallback;

  for (const breakpoint of BREAKPOINTS) {
    previous = typeof input === "object" ? (input[breakpoint] ?? previous) : (input ?? previous);
    resolved[breakpoint] = previous;
  }

  return resolved;
}

function assertValid(condition: boolean, property: string, breakpoint: Breakpoint, expected: string) {
  if (!condition) throw new RangeError(`${property} at ${breakpoint}: ${expected}`);
}

function isPositiveInteger(value: number) {
  return Number.isSafeInteger(value) && value > 0;
}

function isSpacingStep(value: SpacingStep) {
  return SPACING_STEPS.includes(value);
}

function toStyle(
  getValues: (breakpoint: Breakpoint) => Record<string, string | number>,
): LayoutStyle {
  const style: LayoutStyle = {};
  for (const breakpoint of BREAKPOINTS) {
    for (const [property, value] of Object.entries(getValues(breakpoint))) {
      style[`--layout-${property}-${breakpoint}`] = value;
    }
  }
  return style;
}

function resolveDisplay(visibility: Responsive<Visibility> | undefined, display: "block" | "grid" | "flex") {
  const resolved = resolveResponsive(visibility, "visible");
  return (breakpoint: Breakpoint) => {
    const value = resolved[breakpoint];
    assertValid(value === "visible" || value === "hidden", "visibility", breakpoint, "use visible or hidden");
    return value === "hidden" ? "none" : display;
  };
}

function resolveGap(gap: Responsive<SpacingStep> | undefined) {
  const resolved = resolveResponsive<SpacingStep>(gap, 4);
  return (breakpoint: Breakpoint) => {
    const value = resolved[breakpoint];
    assertValid(isSpacingStep(value), "gap", breakpoint, "use an approved spacing step");
    return value;
  };
}

export type GridOptions = {
  columns?: Responsive<number>;
  gap?: Responsive<SpacingStep>;
  visibility?: Responsive<Visibility>;
};

export function resolveGrid({ columns, gap, visibility }: GridOptions = {}) {
  const resolvedColumns = resolveResponsive(columns ?? DEFAULT_GRID_COLUMNS, 1);
  const gapAt = resolveGap(gap);
  const displayAt = resolveDisplay(visibility, "grid");
  const style = toStyle((breakpoint) => {
    const count = resolvedColumns[breakpoint];
    assertValid(isPositiveInteger(count), "columns", breakpoint, "use a positive safe integer");
    return { columns: count, gap: gapAt(breakpoint), display: displayAt(breakpoint) };
  });
  return { className: "layout-grid", columns: resolvedColumns, style } as const;
}

export type GridItemOptions = {
  span?: Responsive<number | "full">;
  start?: Responsive<number | "auto">;
  order?: Responsive<number>;
  visibility?: Responsive<Visibility>;
};

export function resolveGridItem(
  parent: Pick<ReturnType<typeof resolveGrid>, "columns">,
  { span, start, order, visibility }: GridItemOptions = {},
) {
  const spans = resolveResponsive(span, 1);
  const starts = resolveResponsive(start, "auto");
  const orders = resolveResponsive(order, 0);
  const displayAt = resolveDisplay(visibility, "block");
  const style = toStyle((breakpoint) => {
    const count = parent.columns[breakpoint];
    const itemSpan = spans[breakpoint];
    const itemStart = starts[breakpoint];
    assertValid(isPositiveInteger(count), "parent columns", breakpoint, "use a positive safe integer");
    assertValid(itemSpan === "full" || (isPositiveInteger(itemSpan) && itemSpan <= count), "span", breakpoint, `use full or an integer from 1 to ${count}`);
    assertValid(itemStart === "auto" || (isPositiveInteger(itemStart) && itemStart <= count), "start", breakpoint, `use auto or an integer from 1 to ${count}`);
    if (itemSpan === "full") {
      assertValid(itemStart === "auto", "start", breakpoint, "full span requires auto");
    } else if (itemStart !== "auto") {
      assertValid(itemSpan <= count - itemStart + 1, "span/start", breakpoint, "placement exceeds the explicit grid");
    }
    assertValid(Number.isSafeInteger(orders[breakpoint]), "order", breakpoint, "use a signed safe integer");
    return {
      start: itemSpan === "full" ? 1 : itemStart,
      end: itemSpan === "full" ? -1 : `span ${itemSpan}`,
      order: orders[breakpoint],
      display: displayAt(breakpoint),
    };
  });
  return { className: "layout-item", style } as const;
}

const DIRECTIONS = ["row", "column"] as const;
const ALIGNMENTS = ["start", "center", "end", "stretch", "baseline"] as const;
const JUSTIFICATIONS = {
  start: "start", center: "center", end: "end", between: "space-between",
  around: "space-around", evenly: "space-evenly",
} as const;
const WRAPS = ["nowrap", "wrap"] as const;

export type FlexOptions = {
  direction?: Responsive<(typeof DIRECTIONS)[number]>;
  align?: Responsive<(typeof ALIGNMENTS)[number]>;
  justify?: Responsive<keyof typeof JUSTIFICATIONS>;
  wrap?: Responsive<(typeof WRAPS)[number]>;
  gap?: Responsive<SpacingStep>;
  visibility?: Responsive<Visibility>;
};

export function resolveFlex({ direction, align, justify, wrap, gap, visibility }: FlexOptions = {}) {
  const directions = resolveResponsive(direction, "row");
  const alignments = resolveResponsive(align, "stretch");
  const justifications = resolveResponsive(justify, "start");
  const wraps = resolveResponsive(wrap, "nowrap");
  const gapAt = resolveGap(gap);
  const displayAt = resolveDisplay(visibility, "flex");
  const style = toStyle((breakpoint) => {
    assertValid(DIRECTIONS.includes(directions[breakpoint]), "direction", breakpoint, "use row or column");
    assertValid(ALIGNMENTS.includes(alignments[breakpoint]), "align", breakpoint, "use a supported alignment");
    assertValid(Object.hasOwn(JUSTIFICATIONS, justifications[breakpoint]), "justify", breakpoint, "use a supported justification");
    assertValid(WRAPS.includes(wraps[breakpoint]), "wrap", breakpoint, "use nowrap or wrap");
    return {
      direction: directions[breakpoint],
      align: alignments[breakpoint],
      justify: JUSTIFICATIONS[justifications[breakpoint]],
      wrap: wraps[breakpoint],
      gap: gapAt(breakpoint),
      display: displayAt(breakpoint),
    };
  });
  return { className: "layout-flex", style } as const;
}

export function resolveVisibility(visibility?: Responsive<Visibility>) {
  const displayAt = resolveDisplay(visibility, "block");
  return { className: "layout-block", style: toStyle((breakpoint) => ({ display: displayAt(breakpoint) })) } as const;
}

const CONTAINER_WIDTHS = {
  page: "max-w-page",
  reading: "max-w-reading",
  fluid: "max-w-none",
} as const satisfies Record<ContainerWidth, string>;

export function resolveContainer(
  { width = "page", gutters = true }: { width?: ContainerWidth; gutters?: boolean } = {},
) {
  return ["mx-auto w-full min-w-0", CONTAINER_WIDTHS[width], gutters && "px-page-gutter"].filter(Boolean).join(" ");
}

export function resolveSection(spacing: SectionSpacing = "section") {
  if (spacing === "section") return { className: "py-section" };
  const step = spacing === "none" ? 0 : spacing;
  assertValid(isSpacingStep(step), "section spacing", "base", "use an approved spacing step");
  return { className: "layout-section", style: { "--layout-section-step": step } satisfies LayoutStyle };
}
