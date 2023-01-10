# Plotting Tool

Tool for tracking cryptocurrency prices, creating bundles of cryptocurrencies and plotting gathered price data.
Uses [CoinGecko Open Cryptocurrency API](https://www.coingecko.com/en/api) for price data fetching.

## Testing 

To run tests, run the following command in the root folder
```py
# Linux / Mac
python3 -m unittest -v

# Windows
python -m unittest -v
```

## Installing

To install this tool, clone the repository and run the command below in the root folder.

```py
# Linux / Mac
pip3 install .
OR
python3 -m pip install .

# Windows
pip install .
OR
py -m pip install .
```

## Using the application

After installation the application can be started by running command `plottool` in terminal/console.
To see all the available commands and their descriptions, use command `help`.

```console
user@machine:~$ plottool
[12.00.00] >>>>> STARTING THE PROGRAM
[12.00.00] ----- Enter command:
> help
[12.00.05] 
    - help        | Show this message.
    - help basic  | Show basic commands.
    - help cur    | Show cryptocurrency-related commands.
    - help bund   | Show bundle-related commands.
```