import json
import os
import requests
from json.decoder import JSONDecodeError

"""
AddressWatcher

AddressWatcher will fetch data from Etherscan and updates a file called 'latest_txs.txt'.
latest_txs.txt is in a JSON format (key:value), where the key is the address, and the value is the transaction hash.
Every time this program runs, it checks for the latest ERC20 transaction. 
If the latest transaction is different from what is in the 'latest_txs.txt' file, 
it will print out 'New transaction for <address>, hash: <hash>'.

There are two text files:
    addrs.txt - A list of addresses you want to watch. You can add as many addresses as you want.
                But the more addresses, the slower the program runs. Also, there's a rate limit on
                how many requests you can send to the Etherscan API (can't fetch data in parallel).
    latest_txs.txt - Addresses and their latest transaction hashes. Used to keep track of new transactions.


You can modify what the program does on new transactions, such as trigger a bot to tweet.
In that case, you'll need a Twitter API and account. The default action is just to print out what has changed.

You can also use other attributes such as timeStamp. See _get_erc20_txs() method (notice the preceding underscore)
to find out what other attributes are available to you.

The last thing you need is to figure out how to setup cron. I use a linux. You'll have to find the equivalent for
your operating system. Keep in mind that each address in addrs.txt equals one call to the Etherscan API,
so setting a cron job to run every 5 minutes for 30 addresses would be 600 requests/hour. I would recommend setting
the cron job to run once every hour or two hours.
"""


class AddressWatcher:
    BASE_URL = 'https://api.etherscan.io/api'

    def __init__(self, key: str, addresses: list):
        self.addresses = addresses
        self.api_key = key
        self.history = None
        self.load_history()

    def load_history(self):
        try:
            if os.path.exists('latest_txs.txt'):
                with open('latest_txs.txt') as f:
                    self.history = json.load(f)
            else:
                self.history = {}
        except JSONDecodeError:
            # Create file
            self.history = {}

    def _get_erc20_txs(self,
                       contract_address: str = None,
                       address: str = None,
                       start_block: int = None,
                       end_block: int = None,
                       page: int = 1,
                       offset: int = 10000,
                       sort='asc') -> dict:
        """
        Get ERC20 token transactions for the given address or contract address.
        Either the contract_address or the address must be provided.
        The default parameters returns the results from the very first transaction
        of the given address onwards.

        :param contract_address: (str) The contract address. Defaults to None.
        :param address: (str) The address. Defaults to None.
        :param start_block: (int) (optional) The starting block number. Defaults to None.
        :param end_block: (int) (optional) The ending block number. Defaults to None.
        :param page: (int) (optional) Number of pages to return (for pagination). Defaults to 1.
        :param offset: (int) (optional) The number of results to display per page. Defaults to 10000.
        :param sort: (str) (optional) The sort option. Either 'asc' (ascending) or 'desc' (descending).
            Defaults to 'asc'.
        :return: (dict) The return value from the get request.

            Sample Response:
                {
                   "status":"1",
                   "message":"OK",
                   "result":[
                      {
                         "blockNumber":"4730207",
                         "timeStamp":"1513240363",
                         "hash":"0xe8c208398bd5ae8e4c237658580db56a2a94dfa0ca382c99b776fa6e7d31d5b4",
                         "nonce":"406",
                         "blockHash":"0x022c5e6a3d2487a8ccf8946a2ffb74938bf8e5c8a3f6d91b41c56378a96b5c37",
                         "from":"0x642ae78fafbb8032da552d619ad43f1d81e4dd7c",
                         "contractAddress":"0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2",
                         "to":"0x4e83362442b8d1bec281594cea3050c8eb01311c",
                         "value":"5901522149285533025181",
                         "tokenName":"Maker",
                         "tokenSymbol":"MKR",
                         "tokenDecimal":"18",
                         "transactionIndex":"81",
                         "gas":"940000",
                         "gasPrice":"32010000000",
                         "gasUsed":"77759",
                         "cumulativeGasUsed":"2523379",
                         "input":"deprecated",
                         "confirmations":"7968350"
                      },
                      {
                         "blockNumber":"4764973",
                         "timeStamp":"1513764636",
                         "hash":"0x9c82e89b7f6a4405d11c361adb6d808d27bcd9db3b04b3fb3bc05d182bbc5d6f",
                         "nonce":"428",
                         "blockHash":"0x87a4d04a6d8fce7a149e9dc528b88dc0c781a87456910c42984bdc15930a2cac",
                         "from":"0x4e83362442b8d1bec281594cea3050c8eb01311c",
                         "contractAddress":"0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2",
                         "to":"0x69076e44a9c70a67d5b79d95795aba299083c275",
                         "value":"132520488141080",
                         "tokenName":"Maker",
                         "tokenSymbol":"MKR",
                         "tokenDecimal":"18",
                         "transactionIndex":"167",
                         "gas":"940000",
                         "gasPrice":"35828000000",
                         "gasUsed":"127593",
                         "cumulativeGasUsed":"6315818",
                         "input":"deprecated",
                         "confirmations":"7933584"
                      }
                   ]
                }
        """
        params = {
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': address,
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': sort,
            'apikey': self.api_key
        }
        if not contract_address and not address:
            raise ValueError('Either a contract_address or an address must be provided.')

        if not contract_address:
            params.pop('contractaddress')
        if not address:
            params.pop('address')
        if not start_block:
            params.pop('startblock')
        if not end_block:
            params.pop('endblock')

        r = requests.get(self.BASE_URL, params=params)
        return r.json()

    def get_erc20_txs(self):
        for a in self.addresses:
            # Make sure sort is desc
            try:
                data = self._get_erc20_txs(address=a, offset=1, sort='desc')['result'][0]
                t_hash = data['hash']
                if self.history.get(a) != t_hash:
                    # Do something here to notify user (Twitter bot, etc)
                    print(f'New transaction for {a}, hash: {t_hash}')
                    self.history[a] = t_hash
            except IndexError:
                print(f"No transactions for {a}")
                continue

    def to_file(self):
        # Write data to latest_txs.csv
        with open('latest_txs.txt', 'w') as f:
            f.write(json.dumps(self.history, indent=4))


def run(api_key: str):
    if not os.path.exists('addrs.txt'):
        raise FileNotFoundError('Missing addrs.txt')

    with open('addrs.txt', 'r') as f:
        # Reads and removes duplicate addresses.
        addrs = list(set([a.strip('\n') for a in f.readlines()]))

    ad = AddressWatcher(key=api_key, addresses=addrs)
    ad.get_erc20_txs()
    ad.to_file()


if __name__ == '__main__':
    etherscan_key = '<YOUR_API_KEY>'
    run(etherscan_key)
