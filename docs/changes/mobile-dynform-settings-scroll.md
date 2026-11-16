# Mobile: Reveal Dynamic Form Settings When a Field is Selected

## Summary

This change improves the user experience for mobile users when editing dynamic forms. When a field is selected or added below the large screen breakpoint (lg), the settings heading or label input is automatically scrolled into view without requiring manual searching. This behavior is optimized for mobile viewports (375px and 768px) and respects accessibility preferences for reduced motion.

## What Changed

- **`frontend-vue/src/views/admin/AdminDynformEditor.vue`**: Updated the `selectField` function to:
  - Focus the label input with `preventScroll: true` for desktop widths (≥ 1024px).
  - Scroll the settings heading or label input into view for mobile viewports (width < 1024px) using `scrollIntoView`.
  - Respect reduced motion preferences by using `behavior: 'auto'` when `prefers-reduced-motion: reduce` is active.
  - Gracefully handle cases where elements are missing or `window`/`document` are undefined.

- **`frontend-vue/src/views/admin/AdminDynformEditor.spec.js`**: Added unit tests to verify:
  - Mobile viewport (375px and 768px) behavior: scrollIntoView is called on the settings heading/input.
  - Desktop viewport (≥ 1024px) behavior: scrollIntoView is not called, and preventScroll: true is preserved.
  - Reduced motion behavior: scrollIntoView is called with `behavior: 'auto'` when `prefers-reduced-motion: reduce` is active.
  - Graceful handling of missing elements or undefined `window`/`document`.

## Why It Matters

- **Improved Accessibility**: Users with reduced motion preferences now have a smoother experience without unexpected scrolling.
- **Enhanced Usability**: Mobile users no longer need to manually search for the settings or label input after selecting or adding a field.
- **Consistent Behavior**: Desktop users retain the existing focus behavior without unexpected scroll jumps.

## How to Use or Test

### Testing
- Run the following command to execute the unit tests:
  ```bash
  npx vitest run frontend-vue/src/views/admin/AdminDynformEditor.spec.js
  ```
- Verify the following test cases:
  - Mobile viewport (375px and 768px): scrollIntoView is called on the settings heading/input with `behavior: 'smooth'` (unless reduced motion is active).
  - Desktop viewport (≥ 1024px): scrollIntoView is not called, and preventScroll: true is preserved.
  - Reduced motion: scrollIntoView is called with `behavior: 'auto'` when `prefers-reduced-motion: reduce` is active.
  - Missing elements: no unhandled exceptions are thrown.

### Usage
- This change affects the `AdminDynformEditor` component in the frontend Vue application. It ensures that users on mobile devices can easily access the settings for newly added or selected fields without manual scrolling.
- No changes are required in other parts of the application, as this change is localized to the `AdminDynformEditor.vue` and its associated tests.

## Notes
- This change was made against the `testing` branch and is ready for merge after CI passes and QA verification.
- No breaking changes are expected, as this change is focused on improving the user experience without altering existing behavior on desktop viewports.
- The change is minor and can be merged on green CI after QA.
