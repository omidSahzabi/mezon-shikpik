# AppGrid

```tsx
const owner = createAppGridOwner({ columns: { base: 1, md: 4 } });
<AppGrid owner={owner}>{children}</AppGrid>
```

Defaults to 1/2/4/6/8/12 tracks with gap 4. Pass responsive columns, gap or visibility, or pass the owner returned by createAppGridOwner. Use the same owner for AppGridItem. When using an owner, pass layout overrides to createAppGridOwner.
