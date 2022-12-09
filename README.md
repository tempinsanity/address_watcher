# AddressWatcher

### Setup and Usage:

1) Install python3.6 or above.
2) Install pip. This is your package manager. You'll need it to install dependencies.
3) Once python and pip are installed, go to the terminal, navigate to the directory containing this file
and type in: `pip install -r requirements.txt`
4) Get an Etherscan API key
5) Replace your API key on the bottom of the page where it says `<YOUR_API_KEY>` in quotes.
6) Add addresses you want to follow in the `addrs.txt` file.
7) Go to the terminal, navigate to the directory containing this file and type: `python3 -m address_watcher.py`


### Description:

AddressWatcher will fetch data from Etherscan and updates a file called 'latest_txs.txt'.
latest_txs.txt is in a JSON format (key:value), where the key is the address, and the value is the transaction hash.
Every time this program runs, it checks for the latest ERC20 transaction. 
If the latest transaction is different from what is in the 'latest_txs.txt' file, 
it will print out "New transaction for <wallet_address>, hash: <txs_hash>".

There are two text files:

    addrs.txt - A list of addresses you want to watch. You can add as many addresses as you want. But the more addresses, the slower the program runs. Also, there's a rate limit on how many requests you can send to the Etherscan API (can't fetch data in parallel).
    
    latest_txs.txt - Addresses and their latest transaction hashes. Used to keep track of new transactions.


You can modify what the program does on new transactions, such as trigger a bot to tweet.
In that case, you'll need a Twitter API and account. The default action is just to print out what has changed.

You can also use other attributes such as timeStamp. See `_get_erc20_txs()` method (notice the preceding underscore)
to find out what other attributes are available to you.

The last thing you need is to figure out how to set up cron. You'll have to find the equivalent for
your operating system. Keep in mind that each address in addrs.txt equals one call to the Etherscan API,
so setting a cron job to run every 5 minutes for 30 addresses would be 600 requests/hour. I would recommend setting
the cron job to run once every hour or two hours.