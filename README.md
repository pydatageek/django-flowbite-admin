# Django Flowbite Admin
A modern Django admin interface styled with Flowbite + TailwindCSS.

## Building the frontend assets

Static CSS and JavaScript are vendored in `flowbite_admin/static/flowbite_admin/`. Whenever you update the templates or need to refresh the Flowbite/Tailwind utilities, run the local build script:

```bash
npm run build
```

This command parses the project templates and regenerates `flowbite_admin/static/flowbite_admin/css/flowbite-admin.css`. The Flowbite drawer logic used by the admin is provided via the bundled `flowbite.min.js` file in the same static directory, so no external CDN dependencies are required when deploying the package.
