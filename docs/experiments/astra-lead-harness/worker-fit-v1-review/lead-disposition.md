# Astra 主手配模：兩種工作都完成，額外 skill 未顯示省成本

本批14個真實CLI calls全部有可核對用量，共1653146tokens。Astra/high四組都選Luna/high，沒有為湊階層改用Sol；這是觀察，不是最佳配模證明。每個產品均通過相同外部oracle。

| 題型／條件 | calls | tokens | episode秒 | 主手返工 | 產品驗收 |
|---|---:|---:|---:|---|---|
| 小型／None W1 | 3 | 181177 | 87.190 | 無 | 5/5 |
| 小型／Lab0.1.8 W2 | 3 | 190460 | 99.551 | 無 | 5/5 |
| 多约束／Lab0.1.8 W3 | 5 | 875616 | 729.155 | 1次tests限定 | 54/54 |
| 多約束／None W4 | 3 | 405893 | 339.036 | 無 | 54/54 |

同題差額：小型Lab多9283tokens、12.361秒；多約束Lab多469723tokens、390.119秒。這是一對一樣本，不把秒差或總token差當穩定因果；也不能用未取得的實際帳單報省錢。所有cached tokens是input的子集，reasoning是output的子集，不重加。

W3的主手交回具有實質用途：抓到亂序測試名不副實，只补持久化測試，保留已證明的產品判定。W4沒有額外skill也做了完整派工及獨立回讀，worker第一次即提供有效亂序測試。這兩點同時成立；不把W3的有用修正當作Lab相對勝出，也不把W4一次較順當成通用模型排名。

兩組都有非Git fixture工具摩擦；W3另有登入shell警告、初版整數約束錯用、錯誤probe预期與快取生成／移除。最終產品都正確；各機制的直接因果未由本批單獨隔離。所有來源、命令、file changes及最終產品由主線核對，未拿worker的DONE當驗收。

**判定：在任務已明寫責任分離、授權、worker與完成條件的情境，額外Delegate skill未展現增量效益。保留Delegate解決的所有權與配模目的，但不把它升成Astra每次必載流程。** 這批尚未測「任務書沒有這些契約時skill能否補上」，更未測大型跨回合專案或真人閱讀。

直接Astra政策另做prospective新副本，與本批分開；那會改变實作／驗收責任配置，不能混稱為只有skill差異的A/B。

證據：[完整用量](usage-complete-v1.json)、[W1/W2核對](small-pair-lead-review.md)、[W3核對](W3-lead-review.md)、[W4核對](W4-lead-review.md)、[W3產品真值](W3-oracle.json)、[W4產品真值](W4-oracle.json)。
