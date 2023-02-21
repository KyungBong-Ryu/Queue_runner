import time
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Argparse Tutorial')
    parser.add_argument("--epoch",  type=int, default=200)
    parser.add_argument("--name", type=str, default="example_2")
    args = parser.parse_args()
    
    _str = args.name
    print("\ninit", _str)
    print("epoch =", args.epoch)
    time.sleep(1)
    print("finish", _str)