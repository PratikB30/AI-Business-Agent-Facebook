import random

def auto_distribute_days(frequency):
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return random.sample(all_days, frequency)