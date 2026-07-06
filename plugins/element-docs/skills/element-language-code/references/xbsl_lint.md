# XBSL CLI Analyzer

`scripts/xbsl_lint.py` validates 1C:Enterprise Element (`XBSL`) source files.

The analyzer is intentionally conservative: it reports syntax, block, scope, local declaration, basic type, and locally declared method-call errors that it can determine from the analyzed files. Platform APIs and unknown external member calls are not treated as errors in this first version.

When files belong to an Element project with adjacent YAML/XBSL metadata, the CLI also runs in conservative project mode. In that mode diagnostics that require a full platform, UI, or YAML model are suppressed to avoid false positives on valid working projects. Standalone files and stdin remain strict.

## Usage

```bash
python3 scripts/xbsl_lint.py PATH...
```

`PATH` can be a file or a directory. Directories are searched recursively for `.XBSL` and `.xbsl` files.

Read from standard input:

```bash
python3 scripts/xbsl_lint.py - --stdin-name sample.XBSL
```

Machine-readable output:

```bash
python3 scripts/xbsl_lint.py src --format json
```

## Exit Codes

- `0` - no diagnostics.
- `1` - analyzer found errors.
- `2` - CLI input or file-reading error.

## Scope Rules

Variables declared inside `если`, `иначе`, `выбор/когда`, `для`, `пока`, `попытка/поймать/вконце`, `область`, or a block lambda are visible only inside that block. To use a value after a block, declare a mutable `пер` before the block and assign it inside the block.
