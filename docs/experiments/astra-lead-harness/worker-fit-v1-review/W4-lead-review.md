# W4：複雜事件投影／無額外 skill

狀態：產品與主手交接核對完成；54 項 oracle checks PASS。Astra/high → Luna/high → 同一 Astra/high 收回，3 calls、339.036秒、405893 tokens，無主手返工。全部用量見 [usage-complete-v1.json](usage-complete-v1.json)。

## 實際證據

主線完整讀取三個最終 source/test 檔、worker 最終回覆、主手派工與最後回覆、所有 completed command scopes 與關鍵檢查输出。Luna只改src/normalization.py、src/projector.py、tests/test_projector.py；Astra不改產品；任務與package範圍無漂移。

Worker 的初次既有測試 exit0 但 capture空；後續10 tests及新增全域重送測試後的11 tests都有完整PASS輸出，不能把第一次空紀錄補成特定數目。主手最終重跑11 tests有完整輸出，另有code/output支持1000組各三種排列、123組無效輸入／衝突、201位revision連續投影；驗證過程不改輸入。獨立預封存oracle另核對53行為+1範圍保留，全通過。

回歸測試實際使用逆序事件、完整預期結果、缺口後餘額None、巨大revision、不同歷史／未知／未選帳戶衝突、型別與重送計數。沒有不當要求dict順序或identity。最終來源有局部驗證helper重複，未觀察到產品後果；不把個人風格偏好計為缺陷。

一次git status在非Git fixture失敗，但沒有用它阻斷驗收。未觀察到權限更改、網路、其他模型呼叫、根目錄新檔或刪檔。Worker自行補全域重送測試，主手未要求返工。

最後交接列完成能力、11 tests、生成／反例检查、一次Luna、主手驗收、費用不可取得與隱藏測試未執行。數字在捕捉證據中可核對；不是人類理解／接受證據。

## 不能越過的推論邊界

此None仍有完整TASK.md與相同的主手／worker載體。TASK與主提示都明寫責任分離、便宜task-fit worker、權限與完成條件。因此它只對照「已有清楚契約後的額外skill context」，不是沒有任何指示，更不是證明Delegate原始目的沒有價值。
