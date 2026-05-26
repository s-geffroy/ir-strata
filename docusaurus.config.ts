import {themes as prismThemes} from 'prism-react-renderer';
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
