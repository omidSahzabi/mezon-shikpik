import { resolveGrid, type GridOptions } from "@/lib/responsive-layout";

export const createAppGridOwner = resolveGrid;
export type AppGridOwner = ReturnType<typeof createAppGridOwner>;

export function AppGridStyles(input: GridOptions | AppGridOwner) {
  return "style" in input ? input : createAppGridOwner(input);
}
