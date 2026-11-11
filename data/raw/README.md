# Raw data

The raw export is not stored in the repository because of its size.

**Download:** https://drive.google.com/drive/folders/16g5XCamrgiFAoqB4RpNYWKVtXEcCUTex?usp=sharing

Save it as `data/raw/raw_flights.json` before running `extraction/preprocess.py`.

## How it was obtained

- **Source:** public flight archive of Compania Națională Aeroporturi București, https://bucharestairports.ro/lista-zboruri/
- **Endpoint:** `https://bucharestairports.ro/wp-json/fds/v1/archive`
- **Parameters:** `airport=henri-coanda`, `type=departure`, `date_from=[...]`, `date_to=[...]`, `per_page=[...]`, `language=ro`
- **Date of download:** [date]
- **Method:** a single request opened manually in a normal browser session and saved as JSON. Automated access is blocked by the site's Cloudflare protection (see the main README).
- **Contents:** [62,652] departure records from 26.10.2025 to 01.10.2026.

The data belongs to CNAB and is used here only for non-commercial academic research.