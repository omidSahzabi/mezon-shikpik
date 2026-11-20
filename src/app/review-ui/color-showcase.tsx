"use client";

import { useEffect, useId, useRef, useState } from "react";
import {
  colorIntents,
  colorRoles,
  colorVariants,
  getColorVariantClasses,
} from "@/lib/color-variants";

const uiTokens = [
  "brand-primary", "primary", "secondary", "accent", "destructive",
  "primary-foreground", "secondary-foreground", "accent-foreground",
  "destructive-foreground", "background", "foreground", "surface", "card",
  "card-foreground", "popover", "popover-foreground", "muted",
  "muted-foreground", "border", "input", "ring", "overlay", "text-primary",
  "text-secondary", "text-muted", "text-disabled",
];

function toHex(color: string) {
  const channels = color.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)$/);
  if (!channels) return color;

  const [, red, green, blue, alpha] = channels;
  const bytes = [Number(red), Number(green), Number(blue)];
  if (alpha !== undefined) bytes.push(Math.round(Number(alpha) * 255));
  return "#" + bytes.map((byte) => byte.toString(16).padStart(2, "0")).join("").toUpperCase();
}

function TokenGroup({ title, tokens }: { title: string; tokens: readonly string[] }) {
  const list = useRef<HTMLUListElement>(null);
  const [values, setValues] = useState<Record<string, string>>({});

  useEffect(() => {
    const group = list.current;
    if (!group) return;

    let frame = 0;
    function refresh() {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const nextValues: Record<string, string> = {};
        group?.querySelectorAll<HTMLElement>("[data-token]").forEach((swatch) => {
          const token = swatch.dataset.token;
          if (token) nextValues[token] = toHex(getComputedStyle(swatch).backgroundColor);
        });
        setValues(nextValues);
      });
    }

    const preference = window.matchMedia("(prefers-color-scheme: dark)");
    preference.addEventListener("change", refresh);

    const observer = new MutationObserver(refresh);
    for (let element = group.parentElement; element; element = element.parentElement) {
      observer.observe(element, { attributes: true, attributeFilter: ["class"] });
    }

    refresh();
    return () => {
      cancelAnimationFrame(frame);
      preference.removeEventListener("change", refresh);
      observer.disconnect();
    };
  }, []);

  return (
    <div className="space-y-2">
      <h4 className="font-semibold"><bdi>{title}</bdi></h4>
      <ul ref={list} className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {tokens.map((token) => (
          <li key={token} className="min-w-0 overflow-hidden rounded border border-border">
            <div
              aria-hidden="true"
              data-token={token}
              className="h-6 bg-surface"
              style={{ backgroundColor: `var(--${token})` }}
            />
            <bdi dir="ltr" className="block break-all px-2 text-xs">--{token}</bdi>
            <bdi dir="ltr" className="block px-2 pb-1 text-xs text-copy-muted">
              {values[token] ?? "…"}
            </bdi>
          </li>
        ))}
      </ul>
    </div>
  );
}

const buttonFrame = "rounded border px-2 py-1 text-xs";

function VariantMatrix() {
  const errorId = useId();

  return (
    <div className="space-y-3">
      <h4 className="font-semibold">ترکیب‌های رنگ و واریانت</h4>
      <p className="text-xs text-copy-muted">
        برای دیدن حالت‌های تعاملی از ماوس، کلیک و کلید Tab استفاده کنید.
      </p>
      {colorIntents.map((intent) => (
        <div key={intent} className="space-y-1">
          <h5 className="text-sm font-semibold"><bdi>{intent}</bdi></h5>
          <ul className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {colorVariants.map((variant) => (
              <li key={variant}>
                <button
                  type="button"
                  aria-label={`${intent} / ${variant}`}
                  className={`${buttonFrame} w-full ${getColorVariantClasses({ intent, variant })}`}
                >
                  <bdi>{variant}</bdi>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          aria-pressed="true"
          className={`${buttonFrame} ${getColorVariantClasses({ variant: "filled" })}`}
        >
          <span aria-hidden="true">✓ </span>انتخاب‌شده
        </button>
        <button
          type="button"
          disabled
          className={`${buttonFrame} ${getColorVariantClasses({ disabled: true })}`}
        >
          غیرفعال
        </button>
        <input
          aria-label="نمونهٔ ورودی نامعتبر"
          aria-invalid="true"
          aria-describedby={errorId}
          className={`${buttonFrame} min-w-0 ${getColorVariantClasses({ variant: "outline", invalid: true })}`}
        />
        <span id={errorId} className="text-xs text-error-strong">ورودی نامعتبر است</span>
      </div>
    </div>
  );
}

export function ColorShowcase() {
  return (
    <section aria-labelledby="review-colors">
      <h2 id="review-colors" className="mb-3 font-semibold">رنگ‌ها</h2>
      <div className="grid gap-4 lg:grid-cols-2">
        {(["light", "dark"] as const).map((theme) => (
          <section
            key={theme}
            aria-labelledby={`review-theme-${theme}`}
            className={`${theme} min-w-0 space-y-4 rounded border border-border bg-background p-3 text-foreground`}
          >
            <h3 id={`review-theme-${theme}`} className="font-semibold">
              {theme === "light" ? "تم روشن" : "تم تیره"}
            </h3>
            <VariantMatrix />
            <TokenGroup title="رنگ‌های رابط و متن" tokens={uiTokens} />
            {colorIntents.map((intent) => (
              <TokenGroup
                key={intent}
                title={intent}
                tokens={colorRoles.map((role) => `${intent}-${role}`)}
              />
            ))}
          </section>
        ))}
      </div>
    </section>
  );
}
