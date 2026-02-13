77%
Your answer is:
['getCoffee', 'getAnnOfficeCoffee', 'gotoAnnOffice', 'getPod', 'getCoffeeAnnOffice']
[['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['N', 'getShopCoffee', 'P(gotoKitchen)'], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['L', 'gotoAnnOffice', '->', 'getCoffeeAnnOffice'], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['V', 'getAnnOfficeCoffee', [2, 0, 6], '>', 'getShopCoffee', [0, 3, 9]], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['L', 'gotoAnnOffice', '->', 'getCoffeeAnnOffice'], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]


55%
Your answer is:
['getCoffee', 'getShopCoffee', 'gotoShop', 'payShop', 'getCoffeeShop']
[['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'O(payShop)'], ['N', 'getAnnOfficeCoffee', 'O(payShop)'], ['P', 'gotoShop', []], ['L', 'gotoShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [1, 2, 0]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'O(payShop)'], ['N', 'getAnnOfficeCoffee', 'O(payShop)'], ['P', 'payShop', ['haveMoney']], ['L', 'payShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [1, 2, 0]]]]


59%
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


74%
Your answer is:
['getCoffee', 'getShopCoffee', 'gotoShop', 'payShop', 'getCoffeeShop']
[['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'P(gotoAnnOffice)'], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice)'], ['L', 'gotoShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getShopCoffee', ['haveMoney']], ['F', 'getKitchenCoffee', ['staffCardAvailable']], ['N', 'getAnnOfficeCoffee', 'P(gotoAnnOffice)'], ['L', 'gotoShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]