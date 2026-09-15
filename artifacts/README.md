# Artifacts

`artifacts/` separates machine-local execution state from research conclusions
that should travel through Git.

## Machine-Local State

Builds, installs, scratch data, and raw numerical runs are ignored. Put a case
run under:

```text
artifacts/runtime/<case>/<run-id>/
```

That directory may contain generated inputs, logs, checkpoints, fields,
validator output, and failed attempts. It may remain only on the machine that
performed the run.

## Research Records

Put a curated study under:

```text
artifacts/records/<study-id>/
```

Records are Git-tracked and organized by research question, not one-to-one with
runs. Normally keep one `README.md` plus selected figures. Record the purpose,
relevant revisions and setup, important results, interpretation, conclusion,
and limitations. Important numeric values should appear in Markdown even when
shown in a figure.

Start from [`_template/README.md`](_template/README.md) when useful.
