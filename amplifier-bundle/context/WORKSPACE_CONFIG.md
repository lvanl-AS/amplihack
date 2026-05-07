# Workspace Configuration

PMs often work across multiple ADO boards. The workspace config system allows targeting the right board by alias.

## Config File

Location: `~/.azure-devops-tools.json`

```json
{
  "default": "mobile",
  "workspaces": {
    "mobile": {
      "org": "https://dev.azure.com/alaskaair",
      "project": "MobileApp",
      "area_path": "MobileApp\\Team Alpha"
    },
    "web": {
      "org": "https://dev.azure.com/alaskaair",
      "project": "WebPortal",
      "area_path": "WebPortal\\Frontend"
    }
  }
}
```

## Resolution Order

Configuration is resolved in this priority:

1. `--workspace` flag (named alias from config file)
2. `--org` / `--project` flags (explicit override)
3. Flat config file values (backward compatible)
4. Environment variables: `AZURE_DEVOPS_ORG_URL`, `AZURE_DEVOPS_PROJECT`
5. `az devops configure --list` output

## Usage in Recipes

Python wrappers accept `--workspace` as an optional flag:

```yaml
- id: "fetch-story"
  type: "bash"
  command: |
    python .claude/scenarios/az-devops-tools/get_work_item.py \
      --id {{work_item_id}} \
      {{#workspace}}--workspace {{workspace}}{{/workspace}} \
      --format json
  output: "story_data"
```

Recipe context variables:
- `workspace`: optional workspace alias (empty string if not specified)
- Mustache conditional: `{{#workspace}}...{{/workspace}}` only renders if workspace is set

## Available Workspaces

Configure workspaces in `~/.azure-devops-tools.json`. The `default` key sets which workspace is used when no `--workspace` flag is provided.
