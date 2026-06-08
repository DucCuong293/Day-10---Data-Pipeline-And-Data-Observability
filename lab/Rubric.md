# Rubric

## Cach tinh diem

Tong diem co ban: `0-90`

Diem bonus: `90-100`

## Muc 1: Code structure va project organization - 10 diem

- 0-3: Code roi rac, kho doc, khong chia module ro
- 4-7: Co chia module nhung chua nhat quan
- 8-10: Cau truc ro rang, de follow, ten file/ham hop ly

## Muc 2: Raw data ingestion - 15 diem

- 0-5: Chua load duoc data hoac load rat thieu
- 6-10: Load duoc data nhung parse chua on dinh
- 11-15: Load, parse, luu raw response va raw records day du

## Muc 3: Cleaning va data modeling - 15 diem

- 0-5: Cleaning so sai, mat nhieu thong tin
- 6-10: Co cleaned dataset nhung chua chat
- 11-15: Clean ro rang, text_for_embedding hop ly, schema tot

## Muc 4: Embedding va vector store - 10 diem

- 0-3: Chua tao duoc embedding/index
- 4-7: Tao duoc embedding nhung query chua on
- 8-10: ChromaDB + MiniLM hoat dong dung, retrieval hop ly

## Muc 5: Agent va multi-provider LLM - 10 diem

- 0-3: Agent chua chay
- 4-7: Agent chay nhung provider support con it hoac loi
- 8-10: Agent chay tot, provider abstraction ro rang

## Muc 6: Evaluation va scoring - 10 diem

- 0-3: Chua co evaluation
- 4-7: Co metrics nhung chua day du
- 8-10: Co baseline metrics ro rang, answers artifacts day du

## Muc 7: Data observability - 10 diem

- 0-3: Chua co quality/freshness
- 4-7: Co check co ban
- 8-10: Co quality checks, freshness, bao cao ro rang

## Muc 8: Corruption va comparison - 10 diem

- 0-3: Chua simulate corruption
- 4-7: Co corruption nhung chua do duoc impact ro
- 8-10: Co corrupted, repaired, comparison metrics hop ly

## Bonus 90-100

Bonus chi tinh khi bai lam da dat it nhat 90 diem co ban.

Co the cong bonus neu:

- Bao cao markdown rat ro rang, co phan tich thay doi metrics
- Data corruption scenario hop ly va co y nghia
- Co them visualization hoac bang so sanh dep
- Co test hoac validation bo sung
- Co cai dat CLI/use case de de reproduce

## Tru diem

- Khong chay duoc end-to-end
- Commit thieu file quan trong
- Hard-code path hoac key nhay cam
- Bao cao khong match artifact thuc te
