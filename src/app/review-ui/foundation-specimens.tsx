"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

export type FoundationSpecimen = {
  label: string;
  classes: string;
  properties: readonly string[];
  content?: ReactNode;
  direction?: "rtl" | "ltr";
  language?: string;
};

export function FoundationSpecimens({
  specimens,
  interactive = false,
}: {
  specimens: readonly FoundationSpecimen[];
  interactive?: boolean;
}) {
  const list = useRef<HTMLUListElement>(null);
  const [metrics, setMetrics] = useState<string[][]>([]);

  useEffect(() => {
    const scope = list.current;
    if (!scope) return;

    let frame = 0;
    let disposed = false;
    function refresh() {
      if (disposed) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const elements = scope?.querySelectorAll<HTMLElement>("[data-specimen]");
        if (!elements) return;
        setMetrics(Array.from(elements, (element, index) => {
          const style = getComputedStyle(element);
          return specimens[index].properties.map((property) => style.getPropertyValue(property).trim());
        }));
      });
    }

    const preferences = [
      matchMedia("(prefers-reduced-motion: reduce)"),
      matchMedia("(prefers-color-scheme: dark)"),
    ];
    preferences.forEach((preference) => preference.addEventListener("change", refresh));
    window.addEventListener("resize", refresh);
    void document.fonts.ready.then(refresh);
    refresh();

    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      preferences.forEach((preference) => preference.removeEventListener("change", refresh));
      window.removeEventListener("resize", refresh);
    };
  }, [specimens]);

  return (
    <ul className="grid gap-3 sm:grid-cols-2">
      {specimens.map(({ label, classes, properties, content, direction, language }, index) => (
        <li key={label} className="min-w-0 space-y-2 rounded-md border border-border bg-card p-3 text-card-foreground">
          <bdi dir="ltr" className="block text-label">{label}</bdi>
          {interactive ? (
            <button type="button" data-specimen="" lang={language} dir={direction} className={classes}>
              {content}
            </button>
          ) : (
            <div data-specimen="" lang={language} dir={direction} className={classes}>
              {content}
            </div>
          )}
          <dl dir="ltr" className="space-y-1 break-all text-left text-caption text-copy-secondary">
            {properties.map((property, propertyIndex) => (
              <div key={property}>
                <dt className="inline">{property}: </dt>
                <dd className="inline">{metrics[index]?.[propertyIndex] || "…"}</dd>
              </div>
            ))}
          </dl>
        </li>
      ))}
    </ul>
  );
}
