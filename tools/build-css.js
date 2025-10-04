const fs = require('fs');
const path = require('path');

const projectRoot = process.cwd();
const configPath = path.resolve(projectRoot, 'tailwind.config.js');
const tailwindConfig = require(configPath);

const outputPath = path.resolve(projectRoot, 'flowbite_admin/static/flowbite_admin/css/flowbite-admin.css');
const inputPath = path.resolve(projectRoot, 'flowbite_admin/static/flowbite_admin/css/input.css');

const responsiveBreakpoints = {
  sm: '(min-width: 640px)',
  md: '(min-width: 768px)',
  lg: '(min-width: 1024px)'
};

const stateSelectors = {
  hover: ':hover',
  focus: ':focus'
};

const baseStyles = `/* Flowbite Admin base styles */
*, ::before, ::after {
  box-sizing: border-box;
  border-width: 0;
  border-style: solid;
  border-color: #e5e7eb;
}
::before, ::after {
  --tw-content: '';
}
html {
  line-height: 1.5;
  -webkit-text-size-adjust: 100%;
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
body {
  margin: 0;
  line-height: inherit;
  background-color: #f9fafb;
  color: #1f2937;
}
h1, h2, h3, h4, h5, h6 {
  font-size: inherit;
  font-weight: inherit;
}
a {
  color: inherit;
  text-decoration: inherit;
}
button, input, optgroup, select, textarea {
  font-family: inherit;
  font-size: 100%;
  line-height: inherit;
  color: inherit;
  margin: 0;
}
button, select {
  text-transform: none;
}
button, [type='button'], [type='reset'], [type='submit'] {
  -webkit-appearance: button;
  background-color: transparent;
  background-image: none;
}
table {
  border-collapse: collapse;
}
th {
  font-weight: 600;
  text-align: inherit;
}
img, svg, video, canvas, audio, iframe, embed, object {
  display: block;
  vertical-align: middle;
}
img, video {
  max-width: 100%;
  height: auto;
}

#logo-sidebar li,
#sidebar-accordion li {
  list-style: none;
}

#sidebar-accordion [data-accordion-icon] {
  transition: transform 0.2s ease;
}

[data-accordion-item] > h3 > button[aria-expanded="true"] [data-accordion-icon] {
  transform: rotate(180deg);
}

/* Topbar component styles */
.topbar-search {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  max-width: 24rem;
  padding: 0.5rem 0.75rem;
  border-radius: 9999px;
  background-color: #f1f5f9;
  border: 1px solid #e5e7eb;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.topbar-search:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}
.topbar-search__input {
  flex: 1 1 auto;
  min-width: 0;
  border: none;
  background-color: transparent;
  font-size: 0.875rem;
  color: #1f2937;
}
.topbar-search__input::placeholder {
  color: #9ca3af;
}
.topbar-icon-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.topbar-icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  border: 1px solid #e5e7eb;
  background-color: #ffffff;
  color: #6b7280;
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}
.topbar-icon-button:hover {
  background-color: #f1f5f9;
  border-color: #d1d5db;
  color: #111827;
}
.topbar-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #ffffff;
  font-weight: 600;
  text-transform: uppercase;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.dark .topbar-search {
  background-color: rgba(17, 24, 39, 0.6);
  border-color: #374151;
}
.dark .topbar-search:focus-within {
  border-color: #60a5fa;
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.15);
}
.dark .topbar-search__input {
  color: #f9fafb;
}
.dark .topbar-search__input::placeholder {
  color: #6b7280;
}
.dark .topbar-icon-button {
  border-color: #374151;
  background-color: rgba(55, 65, 81, 0.4);
  color: #e5e7eb;
}
.dark .topbar-icon-button:hover {
  background-color: rgba(75, 85, 99, 0.5);
  border-color: #4b5563;
  color: #f9fafb;
}
.dark .topbar-avatar {
  background: linear-gradient(135deg, #1d4ed8, #1f2937);
}
.with-sidebar-offset {
  left: 0;
  right: 0;
  width: 100%;
  padding-left: 0;
  margin-left: 0;
  transition: left 0.3s ease, margin-left 0.3s ease, padding-left 0.3s ease;
}
@media (min-width: 640px) {
  .with-sidebar-offset {
    padding-left: 16rem;
  }
}
@media (min-width: 1024px) {
  .with-sidebar-offset {
    padding-left: 0;
    margin-left: 16rem;
    width: calc(100% - 16rem);
  }
}
`;

const colorMap = {
  white: '#ffffff',
  'blue-50': '#eff6ff',
  'blue-100': '#dbeafe',
  'blue-500': '#3b82f6',
  'blue-600': '#2563eb',
  'blue-700': '#1d4ed8',
  'blue-800': '#1e40af',
  'blue-900': '#1e3a8a',
  'blue-200': '#bfdbfe',
  'blue-300': '#93c5fd',
  'blue-400': '#60a5fa',
  'gray-50': '#f9fafb',
  'gray-100': '#f1f5f9',
  'gray-200': '#e5e7eb',
  'gray-300': '#d1d5db',
  'gray-400': '#9ca3af',
  'gray-500': '#6b7280',
  'gray-600': '#4b5563',
  'gray-700': '#374151',
  'gray-800': '#1f2937',
  'gray-900': '#111827',
  'green-50': '#ecfdf5',
  'green-200': '#bbf7d0',
  'green-800': '#065f46',
  'green-900': '#064e3b',
  'red-50': '#fef2f2',
  'red-200': '#fecaca',
  'red-600': '#dc2626',
  'red-700': '#b91c1c',
  'red-800': '#991b1b',
  'red-900': '#7f1d1d',
  'yellow-50': '#fffbeb',
  'yellow-200': '#fde68a',
  'yellow-300': '#fcd34d',
  'yellow-400': '#fbbf24',
  'yellow-800': '#92400e',
  'yellow-900': '#78350f'
};

function rgbaFromHex(color, alpha) {
  const hex = colorMap[color];
  if (!hex) return null;
  const value = parseInt(hex.slice(1), 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

const spacingScale = {
  '0': '0rem',
  '0.5': '0.125rem',
  '1': '0.25rem',
  '1.5': '0.375rem',
  '2': '0.5rem',
  '2.5': '0.625rem',
  '3': '0.75rem',
  '3.5': '0.875rem',
  '4': '1rem',
  '5': '1.25rem',
  '6': '1.5rem',
  '8': '2rem',
  '10': '2.5rem',
  '11': '2.75rem',
  '12': '3rem',
  '16': '4rem',
  '20': '5rem',
  '24': '6rem'
};

const fontSizes = {
  'text-xs': { size: '0.75rem', lineHeight: '1rem' },
  'text-sm': { size: '0.875rem', lineHeight: '1.25rem' },
  'text-base': { size: '1rem', lineHeight: '1.5rem' },
  'text-lg': { size: '1.125rem', lineHeight: '1.75rem' },
  'text-xl': { size: '1.25rem', lineHeight: '1.75rem' },
  'text-2xl': { size: '1.5rem', lineHeight: '2rem' }
};

const ignored = new Set(['alert_color', 'else', 'entry.is_addition', 'entry.is_change', 'entry.is_deletion']);

function escapeClass(name) {
  return name.replace(/([^a-zA-Z0-9_-])/g, match => `\\${match}`);
}

function globToRegex(glob) {
  let pattern = glob.replace(/([.+^=!:${}()|\[\]\\])/g, '\\$1');
  pattern = pattern.replace(/\*\*/g, '.*');
  pattern = pattern.replace(/\*/g, '[^/]*');
  return new RegExp('^' + pattern + '$');
}

function walk(dir, fn) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules' || entry.name.startsWith('.')) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, fn);
    } else {
      fn(full);
    }
  }
}

function collectContentFiles(patterns) {
  const files = new Set();
  for (const pattern of patterns) {
    const normalized = pattern.replace(/^[.\/]+/, '').replace(/\\/g, '/');
    const regex = globToRegex(normalized);
    walk(projectRoot, file => {
      const rel = path.relative(projectRoot, file).replace(/\\\\/g, '/');
      if (regex.test(rel)) {
        files.add(file);
      }
    });
  }
  return Array.from(files);
}

function extractClassesFrom(content) {
  const classRegex = /class=\"([^\"]+)\"/g;
  const stripChars = "{}%\"'";
  const classes = new Set();
  let match;
  while ((match = classRegex.exec(content))) {
    const tokens = match[1].split(/\s+/);
    for (const token of tokens) {
      const cleaned = token.replace(new RegExp('^[' + stripChars + ']+'), '').replace(new RegExp('[' + stripChars + ']+$'), '');
      if (!cleaned) continue;
      if (cleaned.includes('{') || cleaned.includes('}') || cleaned.includes('%')) continue;
      if (cleaned.startsWith('if') || cleaned.startsWith('elif') || cleaned.startsWith('endif') || cleaned.startsWith('for') || cleaned.startsWith('endfor')) continue;
      if (!/^-?[A-Za-z0-9].*[A-Za-z0-9\]]$/.test(cleaned)) continue;
      classes.add(cleaned);
    }
  }
  return classes;
}

function spacing(value) {
  if (spacingScale[value]) return spacingScale[value];
  if (/^\d+$/.test(value)) {
    return (parseInt(value, 10) / 4) + 'rem';
  }
  return null;
}

function baseDeclaration(base) {
  if (fontSizes[base]) {
    const { size, lineHeight } = fontSizes[base];
    return `font-size: ${size}; line-height: ${lineHeight};`;
  }
  switch (base) {
    case 'block': return 'display: block;';
    case 'inline': return 'display: inline;';
    case 'inline-flex': return 'display: inline-flex;';
    case 'flex': return 'display: flex;';
    case 'grid': return 'display: grid;';
    case 'hidden': return 'display: none;';
    case 'flex-col': return 'flex-direction: column;';
    case 'flex-wrap': return 'flex-wrap: wrap;';
    case 'flex-1': return 'flex: 1 1 0%;';
    case 'relative': return 'position: relative;';
    case 'absolute': return 'position: absolute;';
    case 'items-center': return 'align-items: center;';
    case 'justify-between': return 'justify-content: space-between;';
    case 'justify-center': return 'justify-content: center;';
    case 'justify-end': return 'justify-content: flex-end;';
    case 'gap-1': return 'gap: 0.25rem;';
    case 'gap-2': return 'gap: 0.5rem;';
    case 'gap-3': return 'gap: 0.75rem;';
    case 'gap-4': return 'gap: 1rem;';
    case 'gap-6': return 'gap: 1.5rem;';
    case 'gap-8': return 'gap: 2rem;';
    case 'p-1': return 'padding: 0.25rem;';
    case 'p-2': return 'padding: 0.5rem;';
    case 'p-3': return 'padding: 0.75rem;';
    case 'p-4': return 'padding: 1rem;';
    case 'p-6': return 'padding: 1.5rem;';
    case 'p-8': return 'padding: 2rem;';
    case 'px-2': return 'padding-left: 0.5rem; padding-right: 0.5rem;';
    case 'px-3': return 'padding-left: 0.75rem; padding-right: 0.75rem;';
    case 'px-4': return 'padding-left: 1rem; padding-right: 1rem;';
    case 'px-6': return 'padding-left: 1.5rem; padding-right: 1.5rem;';
    case 'py-0.5': return 'padding-top: 0.125rem; padding-bottom: 0.125rem;';
    case 'py-1': return 'padding-top: 0.25rem; padding-bottom: 0.25rem;';
    case 'py-2': return 'padding-top: 0.5rem; padding-bottom: 0.5rem;';
    case 'py-3': return 'padding-top: 0.75rem; padding-bottom: 0.75rem;';
    case 'py-4': return 'padding-top: 1rem; padding-bottom: 1rem;';
    case 'pb-6': return 'padding-bottom: 1.5rem;';
    case 'pl-2': return 'padding-left: 0.5rem;';
    case 'pl-3': return 'padding-left: 0.75rem;';
    case 'pl-6': return 'padding-left: 1.5rem;';
    case 'pl-11': return 'padding-left: 2.75rem;';
    case 'pt-20': return 'padding-top: 5rem;';
    case 'mx-auto': return 'margin-left: auto; margin-right: auto;';
    case 'mx-4': return 'margin-left: 1rem; margin-right: 1rem;';
    case 'mt-1': return 'margin-top: 0.25rem;';
    case 'mt-2': return 'margin-top: 0.5rem;';
    case 'mt-3': return 'margin-top: 0.75rem;';
    case 'mt-4': return 'margin-top: 1rem;';
    case 'mt-6': return 'margin-top: 1.5rem;';
    case 'mt-20': return 'margin-top: 5rem;';
    case 'mt-24': return 'margin-top: 6rem;';
    case 'mb-4': return 'margin-bottom: 1rem;';
    case 'mb-6': return 'margin-bottom: 1.5rem;';
    case 'ml-3': return 'margin-left: 0.75rem;';
    case 'ml-auto': return 'margin-left: auto;';
    case 'min-h-[70vh]': return 'min-height: 70vh;';
    case 'w-full': return 'width: 100%;';
    case 'w-auto': return 'width: auto;';
    case 'w-64': return 'width: 16rem;';
    case 'w-10': return 'width: 2.5rem;';
    case 'w-6': return 'width: 1.5rem;';
    case 'w-5': return 'width: 1.25rem;';
    case 'w-4': return 'width: 1rem;';
    case 'h-10': return 'height: 2.5rem;';
    case 'h-8': return 'height: 2rem;';
    case 'h-6': return 'height: 1.5rem;';
    case 'h-5': return 'height: 1.25rem;';
    case 'h-4': return 'height: 1rem;';
    case 'h-full': return 'height: 100%;';
    case 'h-screen': return 'height: 100vh;';
    case 'max-w-full': return 'max-width: 100%;';
    case 'max-w-md': return 'max-width: 28rem;';
    case 'shrink-0': return 'flex-shrink: 0;';
    case 'overflow-hidden': return 'overflow: hidden;';
    case 'overflow-y-auto': return 'overflow-y: auto;';
    case 'overflow-x-auto': return 'overflow-x: auto;';
    case 'rounded-lg': return 'border-radius: 0.5rem;';
    case 'rounded-2xl': return 'border-radius: 1rem;';
    case 'border': return 'border-width: 1px; border-style: solid;';
    case 'border-b': return 'border-bottom-width: 1px; border-style: solid;';
    case 'border-t': return 'border-top-width: 1px; border-style: solid;';
    case 'border-r': return 'border-right-width: 1px; border-style: solid;';
    case 'border-dashed': return 'border-style: dashed;';
    case '-translate-x-full': return 'transform: translateX(-100%);';
    case 'transition': return 'transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);';
    case 'transition-colors': return 'transition-property: color, background-color, border-color; transition-duration: 0.2s; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);';
    case 'transition-transform': return 'transition-property: transform; transition-duration: 0.2s; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);';
    case 'duration-200': return 'transition-duration: 0.2s;';
    case 'duration-300': return 'transition-duration: 0.3s;';
    case 'ease-in-out': return 'transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);';
    case 'shadow-sm': return 'box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);';
    case 'shadow-xl': return 'box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 10px 10px -5px rgba(15, 23, 42, 0.04);';
    case 'font-medium': return 'font-weight: 500;';
    case 'font-semibold': return 'font-weight: 600;';
    case 'font-bold': return 'font-weight: 700;';
    case 'uppercase': return 'text-transform: uppercase;';
    case 'tracking-wide': return 'letter-spacing: 0.05em;';
    case 'tracking-widest': return 'letter-spacing: 0.1em;';
    case 'text-left': return 'text-align: left;';
    case 'text-center': return 'text-align: center;';
    case 'text-right': return 'text-align: right;';
    case 'backdrop-blur': return 'backdrop-filter: blur(8px);';
    case 'z-30': return 'z-index: 30;';
    case 'z-40': return 'z-index: 40;';
    case 'fixed': return 'position: fixed;';
    case 'top-0': return 'top: 0;';
    case 'left-0': return 'left: 0;';
    case 'inset-x-0': return 'left: 0; right: 0;';
    case 'right-0': return 'right: 0;';
    case 'list-disc': return 'list-style-type: disc;';
    case 'list-none': return 'list-style: none;';
    case 'grid-cols-1': return 'grid-template-columns: repeat(1, minmax(0, 1fr));';
    case 'object-tools': return 'display: flex; gap: 0.5rem; list-style: none; margin: 0; padding: 0;';
    case 'changelist-form-container': return 'overflow-x: auto;';
    case 'cancel-link': return 'display: inline-block; margin-left: 1rem; color: #4b5563;';
    case 'truncate': return 'overflow: hidden; text-overflow: ellipsis; white-space: nowrap;';
  }
  if (base.startsWith('grid-cols-[')) {
    const value = base.slice('grid-cols-['.length, -1);
    return `grid-template-columns: ${value.replace(/,/g, ' ')};`;
  }
  if (base.startsWith('bg-')) {
    if (base.includes('/')) {
      const [color, alpha] = base.replace('bg-', '').split('/');
      const value = rgbaFromHex(color, parseInt(alpha, 10) / 100);
      if (value) return `background-color: ${value};`;
    }
    const color = colorMap[base.replace('bg-', '')];
    if (color) return `background-color: ${color};`;
  }
  if (base.startsWith('text-')) {
    if (base.includes('/')) {
      const [color, alpha] = base.replace('text-', '').split('/');
      const value = rgbaFromHex(color, parseInt(alpha, 10) / 100);
      if (value) return `color: ${value};`;
    }
    const color = colorMap[base.replace('text-', '')];
    if (color) return `color: ${color};`;
  }
  if (base === 'text-white') {
    return 'color: #ffffff;';
  }
  if (base.startsWith('border-')) {
    const color = colorMap[base.replace('border-', '')];
    if (color) return `border-color: ${color};`;
  }
  if (base === 'ring-1') {
    return 'box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.4);';
  }
  if (base === 'ring-2') {
    return 'box-shadow: 0 0 0 2px rgba(148, 163, 184, 0.4);';
  }
  if (base === 'ring-offset-2') {
    return '--fb-focus-ring-offset: 2px;';
  }
  if (base.startsWith('ring-offset-')) {
    const color = colorMap[base.replace('ring-offset-', '')];
    if (color) return `--fb-focus-ring-offset-color: ${color};`;
  }
  if (base.startsWith('ring-')) {
    const colorKey = base.replace('ring-', '');
    const color = colorMap[colorKey];
    const focusColor = rgbaFromHex(colorKey, 0.45);
    if (color) {
      const focusPart = focusColor ? ` --fb-focus-ring-color: ${focusColor};` : '';
      return `box-shadow: 0 0 0 1px ${color};${focusPart}`;
    }
  }
  if (base === 'outline-none') {
    return 'outline: 2px solid transparent; outline-offset: 2px;';
  }
  return null;
}

function buildSpaceRule(selector, axis, value) {
  const child = `${selector} > :not([hidden]) ~ :not([hidden])`;
  if (axis === 'y') return `${child} { margin-top: ${value}; }`;
  return `${child} { margin-left: ${value}; }`;
}

function buildClassRule(cls) {
  if (ignored.has(cls)) return [];
  const segments = cls.split(':');
  const base = segments.pop();
  const prefixes = segments;

  if (base.startsWith('space-y-') || base.startsWith('space-x-')) {
    const amount = base.replace('space-y-', '').replace('space-x-', '');
    const value = spacing(amount);
    if (!value) return [];
    let selector = `.${escapeClass(cls)}`;
    if (prefixes.includes('dark')) selector = `.dark ${selector}`;
    const axis = base.startsWith('space-y-') ? 'y' : 'x';
    let rule = buildSpaceRule(selector, axis, value);
    const responsive = prefixes.find(p => responsiveBreakpoints[p]);
    if (responsive) {
      rule = `@media ${responsiveBreakpoints[responsive]} { ${rule} }`;
    }
    return [rule];
  }

  if (base.startsWith('hover:')) {
    const actual = base.replace('hover:', '');
    const decl = baseDeclaration(actual);
    if (!decl) return [];
    let selector = `.${escapeClass(cls)}`;
    if (prefixes.includes('dark')) selector = `.dark ${selector}`;
    const responsive = prefixes.find(p => responsiveBreakpoints[p]);
    let rule = `${selector}:hover { ${decl} }`;
    if (responsive) rule = `@media ${responsiveBreakpoints[responsive]} { ${rule} }`;
    return [rule];
  }

  if (base.startsWith('dark:hover:')) {
    const actual = base.replace('dark:hover:', '');
    const decl = baseDeclaration(actual);
    if (!decl) return [];
    return [`.dark .${escapeClass(cls)}:hover { ${decl} }`];
  }

  if (prefixes.includes('focus')) {
    const selector = `.${escapeClass(cls)}`;
    const focusRule = `${selector}:focus { outline: none; box-shadow: 0 0 0 var(--fb-focus-ring-offset, 0) var(--fb-focus-ring-offset-color, transparent), 0 0 0 calc(var(--fb-focus-ring-width, 2px) + var(--fb-focus-ring-offset, 0)) var(--fb-focus-ring-color, rgba(59, 130, 246, 0.45)); }`;
    switch (base) {
      case 'outline-none':
        return [`${selector}:focus { outline: none; }`];
      case 'ring-2':
        return [`${selector} { --fb-focus-ring-width: 2px; }`, focusRule];
      case 'ring-offset-2':
        return [`${selector} { --fb-focus-ring-offset: 2px; }`, focusRule];
      case 'ring-blue-500':
        return [`${selector} { --fb-focus-ring-color: rgba(59, 130, 246, 0.45); }`, focusRule];
      case 'ring-red-500':
        return [`${selector} { --fb-focus-ring-color: rgba(239, 68, 68, 0.45); }`, focusRule];
      case 'ring-offset-gray-900':
        if (prefixes.includes('dark')) {
          return [`.dark ${selector} { --fb-focus-ring-offset-color: rgba(17, 24, 39, 1); }`, focusRule];
        }
        break;
      case 'ring-offset-red-900':
        if (prefixes.includes('dark')) {
          return [`.dark ${selector} { --fb-focus-ring-offset-color: rgba(127, 29, 29, 1); }`, focusRule];
        }
        break;
    }
  }

  if (base.startsWith('dark:')) {
    const actual = base.replace('dark:', '');
    const decl = baseDeclaration(actual);
    if (!decl) return [];
    return [`.dark .${escapeClass(cls)} { ${decl} }`];
  }

  const responsive = prefixes.find(p => responsiveBreakpoints[p]);
  const state = prefixes.find(p => stateSelectors[p]);
  const dark = prefixes.includes('dark');

  const decl = baseDeclaration(base);
  if (!decl) {
    if (base === 'grid-cols-[2fr,1fr]') {
      const prefix = prefixes.find(p => responsiveBreakpoints[p]) || 'lg';
      return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { grid-template-columns: 2fr 1fr; } }`];
    }
    if (['sm:flex-row', 'md:flex-row', 'lg:flex-row'].includes(`${prefixes[0] || ''}:${base}`)) {
      const key = prefixes.find(p => ['sm', 'md', 'lg'].includes(p));
      if (key) {
        return [`@media ${responsiveBreakpoints[key]} { .${escapeClass(cls)} { flex-direction: row; } }`];
      }
    }
    if (base === 'block' || base === 'inline' || base === 'flex-row' || base === 'items-center' || base === 'justify-between' || base === 'px-6' || base === 'px-8' || base === 'ml-64' || base === 'translate-x-0' || base === 'w-1/2' || base === 'w-72') {
      const prefix = prefixes.find(p => responsiveBreakpoints[p]);
      if (!prefix) return [];
      const selector = `.${escapeClass(cls)}`;
      switch (base) {
        case 'block':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { display: block; } }`];
        case 'inline':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { display: inline; } }`];
        case 'flex-row':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { flex-direction: row; } }`];
        case 'items-center':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { align-items: center; } }`];
        case 'justify-between':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { justify-content: space-between; } }`];
        case 'px-6':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { padding-left: 1.5rem; padding-right: 1.5rem; } }`];
        case 'px-8':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { padding-left: 2rem; padding-right: 2rem; } }`];
        case 'ml-64':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { margin-left: 16rem; } }`];
        case 'translate-x-0':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { transform: translateX(0); } }`];
        case 'w-1/2':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { width: 50%; } }`];
        case 'w-72':
          return [`@media ${responsiveBreakpoints[prefix]} { ${selector} { width: 18rem; } }`];
      }
    }
    if (base.startsWith('sm:') || base.startsWith('md:') || base.startsWith('lg:')) {
      const [prefix, rest] = base.split(':');
      const dec = baseDeclaration(rest);
      if (rest === 'ml-64') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { margin-left: 16rem; } }`];
      }
      if (rest === 'translate-x-0') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { transform: translateX(0); } }`];
      }
      if (rest === 'px-6') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { padding-left: 1.5rem; padding-right: 1.5rem; } }`];
      }
      if (rest === 'px-8') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { padding-left: 2rem; padding-right: 2rem; } }`];
      }
      if (rest === 'grid-cols-[2fr,1fr]') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { grid-template-columns: 2fr 1fr; } }`];
      }
      if (rest === 'block') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { display: block; } }`];
      }
      if (rest === 'inline') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { display: inline; } }`];
      }
      if (rest === 'flex-row') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { flex-direction: row; } }`];
      }
      if (rest === 'items-center') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { align-items: center; } }`];
      }
      if (rest === 'justify-between') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { justify-content: space-between; } }`];
      }
      if (rest === 'w-1/2') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { width: 50%; } }`];
      }
      if (rest === 'w-72') {
        return [`@media ${responsiveBreakpoints[prefix]} { .${escapeClass(cls)} { width: 18rem; } }`];
      }
    }
    return [];
  }

  let selector = `.${escapeClass(cls)}`;
  if (dark) selector = `.dark ${selector}`;
  if (state) selector += stateSelectors[state];
  let rule = `${selector} { ${decl} }`;
  if (responsive) {
    rule = `@media ${responsiveBreakpoints[responsive]} { ${rule} }`;
  }
  return [rule];
}

function buildCss() {
  if (!fs.existsSync(inputPath)) {
    throw new Error('Missing input file at ' + inputPath);
  }
  const contentFiles = collectContentFiles(tailwindConfig.content || []);
  const classSet = new Set();
  for (const file of contentFiles) {
    const text = fs.readFileSync(file, 'utf8');
    for (const cls of extractClassesFrom(text)) {
      classSet.add(cls);
    }
  }
  const rules = [];
  rules.push(baseStyles);
  rules.push('/* Generated utility classes */');
  rules.push(':root { --fb-focus-ring-width: 2px; --fb-focus-ring-offset: 0; --fb-focus-ring-color: rgba(59, 130, 246, 0.45); --fb-focus-ring-offset-color: transparent; }');
  rules.push('.dark :focus { box-shadow: 0 0 0 var(--fb-focus-ring-width, 2px) var(--fb-focus-ring-color, rgba(59, 130, 246, 0.45)); }');
  for (const cls of Array.from(classSet).sort()) {
    for (const rule of buildClassRule(cls)) {
      if (rule && !rules.includes(rule)) {
        rules.push(rule);
      }
    }
  }
  fs.writeFileSync(outputPath, rules.join('\n'));
  console.log(`Generated ${rules.length - 3} utility rules for ${classSet.size} classes.`);
}

buildCss();
