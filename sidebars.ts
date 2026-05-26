import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    'DATA_PROVENANCE',
    'AUDIT_REFERENCES',
    'AUDIT_ANACHRONISM',
    'CALIBRATION_STATUS',
    'EXTERNAL_ALIGNMENT',
    'ANACHRONISM_SENSITIVITY',
    'PAPER',
    'SPEC_MASTER',
    {
      type: 'category',
      label: 'Méthodologie',
      items: [
        'methodology/TAXONOMY',
        'methodology/SCORING',
        'methodology/CONFIDENCE',
        'methodology/ANTI_ANACHRONISM',
        'methodology/AGGREGATION',
        'methodology/INTERCODER',
        'methodology/SPECIALIST_VALIDATION',
      ],
    },
    {
      type: 'category',
      label: 'Périodes',
      items: [
        'periods/1815-1848',
        'periods/1848-1871',
        'periods/1871-1914',
        'periods/1914-1919',
        'periods/1919-1939',
        'periods/1939-1945',
        'periods/1945-1962',
        'periods/1962-1979',
        'periods/1979-1991',
        'periods/1991-2001',
        'periods/2001-2008',
        'periods/2008-2014',
        'periods/2014-2022',
        'periods/2022-2026',
      ],
    },
    {
      type: 'category',
      label: 'Données et produit',
      items: [
        'data_contracts/JSON_SCHEMAS',
        'data_contracts/CSV_EXPORTS',
        'data_contracts/REFERENCES_FORMAT',
        'product/DOCUSAURUS_SITE',
        'product/GITHUB_PAGES',
        'product/UI_COMPONENTS',
        'implementation/BUILD_PIPELINE',
        'implementation/LLM_IMPLEMENTATION_PROMPT',
      ],
    },
    'references',
  ],
};

export default sidebars;
