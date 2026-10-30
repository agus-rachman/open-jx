# Point-in-time legislation check

Adapted for open-jx from l0cka/legal-skills (commit 5bfb3d8),
`plugins/legal-skills/references/point-in-time-method.md`. Copyright (c) 2026
l0cka, MIT License (see THIRD-PARTY-NOTICES.md). Extended with New Zealand.

Use this when a task relies on what a provision said on a particular date,
or when the user asks you to check a citation to legislation.

## Publisher and consolidated-text term

Use the pack's rank-1 legislation source. Each publisher names its
consolidated text differently (`consolidated_term` in the pack):

| Jurisdiction | Publisher | Consolidated text |
| --- | --- | --- |
| Commonwealth | legislation.gov.au | compilation |
| ACT | legislation.act.gov.au | republication |
| New South Wales | legislation.nsw.gov.au | version |
| Northern Territory | legislation.nt.gov.au | reprint |
| Queensland | legislation.qld.gov.au | reprint |
| South Australia | legislation.sa.gov.au | version |
| Tasmania | legislation.tas.gov.au | version |
| Victoria | legislation.vic.gov.au | authorised version |
| Western Australia | legislation.wa.gov.au | compilation |
| New Zealand | legislation.govt.nz | version (as at date) |

## Steps

1. **Identify one instrument.** Resolve exactly one official title and type. If
   the title, type or citation is ambiguous, stop and report `NOT VERIFIED`.
2. **Pick the text for the date.** Select the consolidated text whose
   effective range covers the requested date. Record its identifier, effective
   range and exact URL. Don't treat a date in a URL, a registration date or an
   as-made date as the effective start date.
3. **Keep two statuses apart.** The title's present status (in force or
   repealed) is separate from whether the selected text operated on the
   requested date.
4. **Check commencement and currency.** Look at commencement material, the
   amendment history and currency notes for the provision itself. Itemise
   uncommenced or partly commenced provisions, unincorporated amendments and
   update-lag warnings as qualifications. A future commencement is future law.
   A Bill or as-made text does not prove later operation.
5. **Record provenance.** Cite only pages you actually opened. A predicted
   URL is not a source.

## Result

Give exactly one result per provision:

- `VERIFIED` — every item above is supported by an official page you inspected.
- `VERIFIED WITH QUALIFICATIONS` — located, with listed qualifications.
- `NOT VERIFIED` — ambiguous identity, no text covers the date, the publisher
  was unavailable, or a commencement or currency issue couldn't be resolved.

If you can't open the publisher in this session, say so and give the user the
publisher's search page. Never fill the result from memory. Case law is
outside this method; see `case-law-method.md`.
