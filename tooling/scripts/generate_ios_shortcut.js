#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');

const {
  actionOutput,
  buildShortcut,
  withVariables,
} = require('@joshfarrant/shortcuts-js');
const {
  base64Encode,
  comment,
  date,
  formatDate,
  getContentsOfURL,
  getURLsFromInput,
  showResult,
  text,
} = require('@joshfarrant/shortcuts-js/actions');

const OWNER = process.env.GITHUB_OWNER || 'egeuysall';
const REPO = process.env.GITHUB_REPO || 'brain';
const BRANCH = process.env.GITHUB_BRANCH || 'master';
const TOKEN = process.env.GITHUB_TOKEN || '';
const OUTPUT_DIR = process.env.OUTPUT_DIR || path.resolve(process.cwd(), 'tooling', 'shortcuts');
const OUTPUT_FILE = process.env.OUTPUT_FILE || 'Save to Brain.shortcut';

if (!TOKEN) {
  throw new Error('GITHUB_TOKEN is required');
}

const textToken = (str) => ({
  Value: {
    string: str,
    attachmentsByRange: {},
  },
  WFSerializationType: 'WFTextTokenString',
});

const dictStringItem = (key, value) => ({
  WFItemType: 0,
  WFValue: typeof value === 'string' ? textToken(value) : value,
  WFKey: textToken(key),
});

const sourceUrlOut = actionOutput('Source URL');
const readerUrlOut = actionOutput('Reader URL');
const articleMdOut = actionOutput('Article Markdown');
const nowOut = actionOutput('Now');
const stampOut = actionOutput('Stamp');
const fileBodyOut = actionOutput('File Body');
const b64Out = actionOutput('Base64 Content');
const githubApiUrlOut = actionOutput('GitHub API URL');
const githubResponseOut = actionOutput('GitHub Response');

const uploadAction = {
  WFWorkflowActionIdentifier: 'is.workflow.actions.downloadurl',
  WFWorkflowActionParameters: {
    // Store action output so we can surface API errors in Show Result.
    UUID: githubResponseOut.Value.OutputUUID,
    Advanced: true,
    ShowHeaders: true,
    WFHTTPMethod: 'PUT',
    WFHTTPBodyType: 'JSON',
    WFHTTPHeaders: {
      Value: {
        WFDictionaryFieldValueItems: [
          dictStringItem('Authorization', `Bearer ${TOKEN}`),
          dictStringItem('Accept', 'application/vnd.github+json'),
          dictStringItem('X-GitHub-Api-Version', '2026-03-10'),
        ],
      },
      WFSerializationType: 'WFDictionaryFieldValue',
    },
    WFJSONValues: {
      Value: {
        WFDictionaryFieldValueItems: [
          dictStringItem('message', withVariables`chore(resources): add ${stampOut}.md`),
          dictStringItem('content', withVariables`${b64Out}`),
          dictStringItem('branch', BRANCH),
        ],
      },
      WFSerializationType: 'WFDictionaryFieldValue',
    },
  },
};

const actions = [
  comment({
    text: [
      'Share any URL to this shortcut.',
      'It fetches markdown via r.jina.ai and commits to resources/<timestamp>.md.',
      `Destination: ${OWNER}/${REPO}@${BRANCH}`,
    ].join('\n'),
  }),
  getURLsFromInput({}, sourceUrlOut),
  text({ text: withVariables`https://r.jina.ai/${sourceUrlOut}` }, readerUrlOut),
  getContentsOfURL({ method: 'GET' }, articleMdOut),
  date({ use: 'Current Date' }, nowOut),
  formatDate(
    {
      dateFormat: 'Custom',
      formatString: 'yyyy-MM-dd-HHmmss',
    },
    stampOut,
  ),
  text(
    {
      text: withVariables`Source: ${sourceUrlOut}
Saved: ${stampOut}

---

${articleMdOut}`,
    },
    fileBodyOut,
  ),
  base64Encode(
    {
      encodeMode: 'Encode',
      lineBreakMode: 'None',
    },
    b64Out,
  ),
  // withVariables only accepts magic variables as interpolations.
  // Precompose static owner/repo text into the literal string segments.
  text(
    {
      text: withVariables(
        [`https://api.github.com/repos/${OWNER}/${REPO}/contents/resources/`, '.md'],
        stampOut,
      ),
    },
    githubApiUrlOut,
  ),
  uploadAction,
  showResult({
    text: withVariables(
      [`Saved to ${OWNER}/${REPO}: resources/`, '.md\n\nGitHub API response:\n', ''],
      stampOut,
      githubResponseOut,
    ),
  }),
];

const shortcutBuffer = buildShortcut(actions);

fs.mkdirSync(OUTPUT_DIR, { recursive: true });
const targetPath = path.join(OUTPUT_DIR, OUTPUT_FILE);
fs.writeFileSync(targetPath, shortcutBuffer);

console.log(`Wrote shortcut: ${targetPath}`);
