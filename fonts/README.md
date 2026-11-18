Subset (printable ASCII, Latin-1 punctuation, em/en dashes, arrows, and star) WOFF builds of Instrument Serif,
Geist, and Geist Mono, embedded as base64 data URIs into the cards by `scripts/render_readme_cards.py`.

Subset command used via `fontTools.subset` (`pyftsubset`):
```bash
pyftsubset <source.ttf> \
  --unicodes="U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201D,U+2022,U+2026,U+2190-2199,U+2605" \
  --flavor=woff \
  --output-file=fonts/<target>.woff
```

All three font families are licensed under the SIL Open Font License 1.1 (https://openfontlicense.org).
