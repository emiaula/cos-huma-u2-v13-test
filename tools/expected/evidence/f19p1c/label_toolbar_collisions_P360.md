# Name labels under the toolbar on a 360×740 phone (option B, measured with every visible name labelled)

The toolbar is drawn above the labels (z-index 7 over 3) and labels take no taps (`pointer-events: none`), so a
collision can hide part of a label but never blocks a toolbar button or a tap on the model. "Hidden" = share of the
label covered by toolbar buttons. "In the lesson" = whether l04 itself ever shows that label in that view.

| # | View | Label | Hidden | In the lesson? | Effect |
|---|---|---|---|---|---|
| 1 | `cama` | metatars | 4 % | no (cama shows only fèmur, ròtula, tíbia, peroné) | none |
| 2 | `cama` | falanges | 79 % | no | none |
| 3 | `camaCostat` | metatars | 4 % | no (group 1 asks fèmur, ròtula) | none |
| 4 | `camaCostat` | falanges | 87 % | no | none |
| 5 | `camaDarrere` | metatars | 5 % | no (group 2 asks tíbia, peroné) | none |
| 6 | `camaDarrere` | falanges | 89 % | no | none |
| 7 | `tot` | falanges | 57 % | **yes**: review and day-2 «troba» ask falanges in `tot`; after wrong taps the help shows the highlighted bones and the label «falanges» | label partly unreadable (the yellow highlight stays visible); no effect on taps |
| 8 | `cos` | metatars | 38 % | no (`cos` is used by the zones activity; its help labels are the item names, and «metatars» is not an item) | none |
| 9 | `cos` | falanges | 91 % | no: the zones help labels «falanges» at the centre of all left phalanges (hand and foot together), not at the toes; the «tars» help label was measured clear of the toolbar | none |

On 393×851 the same pattern gives 5 collisions (all «falanges»; in the lesson only #7, 38 % hidden).
Not fixed in this round (user instruction: record, do not widen the fix).
