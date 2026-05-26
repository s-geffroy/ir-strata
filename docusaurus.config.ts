import {themes as prismThemes} from 'prism-react-renderer';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const organizationName = process.env.ORGANIZATION_NAME ?? 's-geffroy';
const projectName = process.env.PROJECT_NAME ?? 'ir-strata';
const isUserOrOrgPage = projectName.endsWith('.github.io');

const config: Config = {
  title: 'Pondération historique des théories des RI',
  tagline: 'Atlas analytique 1815–2026',
  favicon: 'img/favicon.svg',
  url: process.env.SITE_URL ?? `https://${organizationName}.github.io`,
  baseUrl: process.env.BASE_URL ?? (isUserOrOrgPage ? '/' : `/${projectName}/`),
  organizationName,
  projectName,
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Feuille de style KaTeX (rendu des formules \[ … \] de la page Papier).
  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css',
      type: 'text/css',
    },
  ],
  i18n: {
    defaultLocale: 'fr',
    locales: ['fr', 'en'],
    localeConfigs: {
      fr: {label: 'Français', direction: 'ltr'},
      en: {label: 'English', direction: 'ltr'},
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'IR Theory Atlas',
      items: [
        {to: '/explorer', label: 'Explorer', position: 'left'},
        {to: '/docs/intro', label: 'Documentation', position: 'left'},
        {to: '/data', label: 'Données', position: 'left'},
        {to: '/coding-console', label: 'Console de codage', position: 'left'},
        {href: 'https://github.com/', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {title: 'Explorer', items: [{label: 'Dashboard', to: '/explorer'}]},
        {title: 'Docs', items: [{label: 'Méthodologie', to: '/docs/methodology/SCORING'}]},
        {title: 'Données', items: [{label: 'Exports', to: '/data'}]},
      ],
      copyright: `Atlas V1 · Révisable · ${new Date().getFullYear()}`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
