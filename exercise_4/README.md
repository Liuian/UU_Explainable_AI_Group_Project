Your answer is:
['getCoffee', 'getKitchenCoffee', 'getStaffCard', 'getOwnCard', 'gotoKitchen', 'getCoffeeKitchen']
[['C', 'getKitchenCoffee', ['staffCardAvailable']], ['N', 'getAnnOfficeCoffee', 'P(payShop)'], ['N', 'getShopCoffee', 'P(payShop)'], 
['P', 'getOwnCard', ['ownCard']], 
['D', 'getStaffCard'], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], 
['U', [['quality', 'price', 'time'], [1, 2, 0]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getKitchenCoffee', ['staffCardAvailable']], ['F', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getShopCoffee', 'P(payShop)'], 
['C', 'getOwnCard', ['ownCard']], ['F', 'getOthersCard', ['colleagueAvailable']], 
['P', 'getOwnCard', ['ownCard']],
['L', 'getOwnCard', '->', 'getCoffeeKitchen'], 
['D', 'getStaffCard'], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'],
['U', [['quality', 'price', 'time'], [1, 2, 0]]]]

對所有的 OR 都要寫 C，像最上面的分支會有兩次 C

---------------------------------------------------------------------------------------

Your answer is:
['getCoffee', 'getKitchenCoffee', 'getStaffCard', 'getOwnCard', 'gotoKitchen', 'getCoffeeKitchen']
[['C', 'getKitchenCoffee', ['staffCardAvailable']], ['V', 'getKitchenCoffee', [5, 0, 3], '>', 'getAnnOfficeCoffee', [2, 0, 6]], ['V', 'getKitchenCoffee', [5, 0, 3], '>', 'getShopCoffee', [0, 3, 9]], ['C', 'getOwnCard', ['ownCard']], ['V', 'getOwnCard', [5, 0, 3], '>', 'getOthersCard', [0, 0, 2]], ['P', 'getOwnCard', ['ownCard']], ['P', 'getCoffeeKitchen', ['haveCard', 'atKitchen']], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getKitchenCoffee', ['staffCardAvailable']], ['V', 'getKitchenCoffee', [5, 0, 3], '>', 'getAnnOfficeCoffee', [2, 0, 6]], ['V', 'getKitchenCoffee', [5, 0, 3], '>', 'getShopCoffee', [0, 3, 9]], ['C', 'getOwnCard', ['ownCard']], ['V', 'getOwnCard', [0, 0, 0], '>', 'getOthersCard', [0, 0, 2]], ['P', 'getOwnCard', ['ownCard']], ['P', 'getCoffeeKitchen', ['haveCard', 'atKitchen']], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

路徑成本計算錯誤

---------------------------------------------------------------------------------------

Your answer is:
['getCoffee', 'getShopCoffee', 'gotoShop', 'payShop', 'getCoffeeShop']
[['N', 'getKitchenCoffee', 'O(payShop)'], ['N', 'getAnnOfficeCoffee', 'O(payShop)'], ['C', 'getShopCoffee', ['haveMoney']], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[]

如果 action 不在 selected trace，要輸出 null list

---------------------------------------------------------------------------------------

Your answer is:
['getCoffee', 'getShopCoffee', 'gotoShop', 'payShop', 'getCoffeeShop']
[['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['N', 'getAnnOfficeCoffee', 'P(gotoKitchen)'], ['C', 'getShopCoffee', ['haveMoney']], 
['L', 'gotoShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoKitchen, gotoAnnOffice)'], ['N', 'getAnnOfficeCoffee', 'P(gotoKitchen, gotoAnnOffice)'], 
['L', 'gotoShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

C factor 永遠要在第一個

---------------------------------------------------------------------------------------

Your answer is:
['getCoffee', 'getKitchenCoffee', 'getStaffCard', 'getOwnCard', 'gotoKitchen', 'getCoffeeKitchen']
[['C', 'getKitchenCoffee', ['staffCardAvailable']], ['N', 'getAnnOfficeCoffee', 'O(gotoKitchen)'], ['N', 'getShopCoffee', 'O(gotoKitchen)'], ['C', 'getOwnCard', ['ownCard']], ['N', 'getOthersCard', 'O(gotoKitchen)'], ['P', 'getOwnCard', ['ownCard']], ['L', 'gotoKitchen', '->', 'getCoffeeKitchen'], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getKitchenCoffee', ['staffCardAvailable']], ['N', 'getAnnOfficeCoffee', 'O(gotoKitchen)'], ['N', 'getShopCoffee', 'O(gotoKitchen)'], ['C', 'getOwnCard', ['ownCard']], ['V', 'getOwnCard', [0, 0, 0], '>', 'getOthersCard', [0, 0, 2]], ['P', 'getOwnCard', ['ownCard']], ['L', 'gotoKitchen', '->', 'getCoffeeKitchen'], ['D', 'getKitchenCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

N(Obligation) 在最右上，第二個 OR 的地方判斷有誤，因為原本了邏輯是看這個分支的所有後代有沒有包含這個obligation，但是這個 OR 的 parent 是 SEQ ，obligation:gotokitchen 將會在 SEQ 的下一個步驟做到，而不是這個分支的 childrens。

判斷邏輯：  
N (Obligation) 的正確邏輯應該是：「如果選了這個分支，該分支（及其所有後代）是否具備履行義務的能力？」

如果父節點是 OR：  
    這代表分支之間是 互斥 的。  
    如果你選了 A 分支，就絕對不會執行到 B 分支。  
    如果義務動作 O 只存在於 B 分支或 B 之後的序列中，那麼選 A 就是 Violation (N)。  

如果父節點是 SEQ：  
    這代表動作是 連續 的。  
    即使當前這一步（例如 getStaffCard）沒包含義務動作，只要它所屬的 SEQ 後續步驟 包含該動作，就不算違規。  