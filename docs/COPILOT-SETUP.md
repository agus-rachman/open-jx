# Copilot Cowork setup

## 1. Get the package

Download `open-jx-<version>.zip` from the
[Releases page](https://github.com/agus-rachman/open-jx/releases), or build it:
run `python tools/build_plugin.py` and use `dist/open-jx-<version>.zip`.

## 2. Install

**Individual users (pilot)**

In Copilot Cowork, open the **Customize** menu, add a plugin and upload the zip.
Install it for the pilot reviewers first.

**Whole organisation**

1. In the M365 admin centre, go to Manage apps > Upload custom app.
2. Select the ellipsis (...) > Add agent, and upload the zip.
3. The plugin then appears under **Discover** in Cowork > Sources & Skills > Plugins.

Notes:

- Information Barriers are not supported for plugin sharing. If your tenant
  uses them, check with IT first.
- The built-in legal skills stay as Microsoft ships them. open-jx adds `jx-`
  skills next to them.

## 3. Custom instructions (each user)

Copilot Cowork chooses skills from their descriptions, so add this to
Preferences > Custom instructions to make sure the jurisdiction router runs first:

```
Before any legal task (contracts, deeds, minutes, memos, chronologies,
deadlines, regulatory or jurisdiction questions), run /jx-router first.
Work out the jurisdiction from my request, any governing-law clause, the
court, or company numbers (ACN/ABN/NZBN). Show the "Jurisdiction:" brief line
before any other output. If no jurisdiction can be found and the task depends
on local law, ask me which one to use.
```

To set a default, add one line, for example:
`My default jurisdiction is au-nsw unless a document or I say otherwise.`

Don't set a default during eval runs.

## 4. In each conversation

- Make sure the open-jx plugin is switched on in the Sources picker.
- Naming the jurisdiction is the most reliable trigger: "Using the NZ pack,
  check…".
- If a legal answer has no `Jurisdiction:` line at the top, the packs were not
  used. Ask again with "use the AU pack" or "use the NZ pack".

## 5. Updating

Bump `version` in `build.config.json`, rebuild, and upload the new zip with the
same manifest `id`. Re-run the eval suite after every open-jx release and every
Legal for Cowork update.
