# SKU catalogue — Acme store

Reference sheet maintained by ops. Live prices are in the store; these are list prices.

| SKU | Product | Category | Supplier | List price |
|---|---|---|---|---|
| APP-TEE-001 | Classic Tee | Apparel | Supplier A | ₹999 |
| APP-TEE-002 | Oversized Tee | Apparel | Supplier A | ₹1,099 |
| APP-SHT-001 | Linen Shirt | Apparel | Supplier A | ₹1,499 |
| APP-JOG-001 | Joggers | Apparel | Supplier A | ₹1,299 |
| APP-HOD-001 | Hoodie | Apparel | Supplier A | ₹1,799 |
| APP-SHO-001 | Shorts | Apparel | Supplier A | ₹899 |
| APP-DRS-001 | Wrap Dress | Apparel | Supplier B | ₹1,599 |
| APP-TOP-001 | Ribbed Top | Apparel | Supplier B | ₹899 |
| APP-TRS-001 | Wide-leg Trousers | Apparel | Supplier B | ₹1,399 |
| FTW-SNK-001 | Everyday Sneaker | Footwear | Supplier C | ₹2,499 |
| FTW-SLD-001 | Slides | Footwear | Supplier C | ₹1,299 |
| FTW-LFR-001 | Loafer | Footwear | Supplier C | ₹2,199 |
| ACC-CAP-001 | Cap | Accessories | Supplier D | ₹499 |
| ACC-BLT-001 | Belt | Accessories | Supplier D | ₹599 |
| ACC-SCK-001 | Crew Socks 3-pack | Accessories | Supplier D | ₹399 |
| ACC-TOT-001 | Tote Bag | Accessories | Supplier D | ₹349 |
| BND-001 | Starter Bundle | Apparel | — | ₹1,299 |
| ACC-SOCK-B | Crew Socks (bundle pack) | Accessories | Supplier D | — |

## Bundles

`BND-001` Starter Bundle = one Classic Tee (Supplier A) + one bundle sock pack
(`ACC-SOCK-B`). The store books the bundle price on the `BND-001` line and adds the sock
pack as a second line at ₹0 on the same order so the warehouse picks both. `ACC-SOCK-B` is
never sold on its own.

## Shipping

Free shipping on orders of ₹999 and above; ₹79 below that. Set at launch in 2023 and not
changed since. Shipped via Courier A (default) or Courier B (overflow).

## Discount codes

`WELCOME10` (first order, 10%), `SALE15` (sale periods, 15%), `FLAT100` (₹100 off),
`APP5` (app orders, 5%). Codes are meant to be single-use per order.
