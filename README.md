# Django Flowbite Admin
A modern Django admin interface styled with Flowbite + TailwindCSS.

## Building the frontend assets

Static CSS and JavaScript are vendored in `flowbite_admin/static/flowbite_admin/`. Whenever you update the templates or need to refresh the Flowbite/Tailwind utilities, run the local build script:

```bash
npm run build
```

This command parses the project templates and regenerates `flowbite_admin/static/flowbite_admin/css/flowbite-admin.css`. The Flowbite drawer logic used by the admin is provided via the bundled `flowbite.min.js` file in the same static directory, so no external CDN dependencies are required when deploying the package.

## Advanced changelist filters

Every changelist rendered by Flowbite Admin now includes an accordion exposing an "Advanced filters" form. The form maps to query string parameters following the pattern `af__<field_name>__<lookup>` and works alongside Django's standard filtering and search tools. Supported lookups vary depending on the field type:

| Field type | Lookups |
| --- | --- |
| Char/Text based fields | `contains`, `icontains`, `exact` |
| Numeric fields | `exact`, `gt`, `gte`, `lt`, `lte` |
| Date/Time fields | `exact`, `gt`, `lt` |
| Boolean & ForeignKey fields | `exact` |

For example, to find books whose title contains "Flow" published after 2021, submit:

```
/admin/admin_tests/book/?af__title__contains=Flow&af__published__gt=2021-01-01
```

The changelist keeps submitted values in the form, ensuring the filters persist across pagination, ordering, and admin actions.
