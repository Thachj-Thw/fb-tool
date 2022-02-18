from tool import *

ACCOUNT = os.path.join(os.path.dirname(os.path.normcase(__file__)), "accounts")


def save(*args: Account) -> None:
    for account in args:
        if account.n_name:
            os.unlink(os.path.join(ACCOUNT, account.file))
            account.name = account.n_name
            account.file = account.name + ".pkl"
            account.n_name = ''
        with open(os.path.join(ACCOUNT, account.file), mode="wb") as file:
            obj = {"uid": account.uid, "cookies": account.cookies()}
            pickle.dump(obj=obj, file=file, protocol=pickle.HIGHEST_PROTOCOL)
        print(account.name, "Saved!")

def remove(*args: str) -> None:
    accounts = os.listdir(ACCOUNT)
    for name in args:
        account = name + ".pkl"
        if account in accounts:
            os.unlink(os.path.join(ACCOUNT, account))
            print(name, "removed")
        else:
            print(f"Account {name} may not be saved")

def all_account() -> list:
    return [os.path.splitext(file)[0] for file in os.listdir(ACCOUNT)]

def quit(*args: Account) -> None:
    for account in args:
        account.quit()

def save_and_quit(*args: Account) -> None:
    save(*args)
    quit(*args)