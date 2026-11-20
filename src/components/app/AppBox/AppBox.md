# AppBox

```tsx
<AppBox color="info" variant="filled" paddingInline={4}>راهنما</AppBox>
```

Neutral div or named semantic wrapper. Defaults to raw color and variant, zero logical padding, and visible. Decorated variants consume production color roles. Use paddingInline and paddingBlock for approved spacing steps, and visibility for responsive display. Preserve semantic landmark names and choose sensible nesting. All color and variant pairs appear in the playground.

Omitting as or using div gives the native div ref type. Article, aside, main, header, and footer use the native HTMLElement ref type associated with those semantic tags.
