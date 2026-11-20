# AppButton

```tsx
<AppButton type="submit" loading={saving}>ذخیره</AppButton>
```

Native action. Defaults to type button, primary, fullFilled and medium. Disabled and loading suppress repeat activation. Loading preserves the action's accessible name and the button's dimensions. Toggle actions opt into aria-pressed. Use AppIconButton for icon-only controls.

## Private shadcn integration

The [private Button](../../ui/button.tsx) adapts the [shadcn New York v4 Button](https://github.com/shadcn-ui/ui/blob/main/apps/v4/registry/new-york-v4/ui/button.tsx). It retains the native button or Radix Slot rendering boundary, slot and variant metadata, and nested SVG behavior. It uses the standalone Radix Slot package and CVA's existing class composition helper.

AppButton supplies the production CVA recipe and state policy in place of the registry's default variants, sizes, and theme classes. It always uses the native button branch. The public API does not expose private Slot composition, so button type, disabled behavior, accessible naming, and button refs continue through the native element. AppIconButton composes the same public AppButton. No shadcn theme or registry configuration is required for this checked-in primitive.
