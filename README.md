# yec__arbibot

## Setup
* Ensure Python is installed on your machine by running the command `python --version`, you'll get an output similar to thhe image below
  
![image](https://github.com/nultinator/yec__arbibot/assets/72562693/4df98c08-f7fd-492b-8c59-f4d679d5df26)
* If you do not have Python installed, you can get it [here](https://www.python.org/downloads/)
* Clone this repo, you can copy and paste the command below (before you second guess yourself, yes there are two `_`(underscores) in the name:
  ```shell
  git clone https://github.com/nultinator/yec__arbibot
  ```
* Hop into the `yec__arbibot` folder: `cd yec__arbibot`
* Make your setup file an executable, if it is not already, `chmod +x setup.sh`
* Run the setup file `./setup.sh`
* Run the bot: `python arbi_bot.py` (this command uses only one underscore)
* On the first run, you will be prompted to enter your API and SECRET keypairs from SouthXchange and Xeggex:  
![Screenshot from 2023-11-28 12-23-54](https://github.com/nultinator/yec__arbibot/assets/72562693/06f8519d-3f5e-4529-b6ae-9f273df4b504)
* You will now have a hidden file, `.config.json` that contains the following information:
```json
        "southx_api": SOUTHX_API_KEY,
        "southx_secret": SOUTHX_SECRET,
        "xeggex_api": XEGGEX_API_KEY,
        "xeggex_secret": XEGGEX_SECRET,
        "default_arb_amount": 1 
```
* `default_arb_amount` is the amount in YEC, that the bot will buy on one exchange and sell on the other if it doesn't have enough money to entirely fill a bid or ask.  To change this amount, open up `.config.json` in a text editor of your choice and simply change `1` to whatever arbitrary number you'd like to use

---

## Running
* From inside the `yec__arbibot` folder, simply run:
  ```shell
  python arbi_bot.py
  ```

