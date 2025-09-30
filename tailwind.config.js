let flowbitePlugin = () => {};
try {
  flowbitePlugin = require('flowbite/plugin');
} catch (error) {
  flowbitePlugin = () => {};
}

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./flowbite_admin/templates/**/*.html",
    "./flowbite_admin/static/flowbite_admin/js/**/*.js",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {}
  },
  plugins: [flowbitePlugin]
};
