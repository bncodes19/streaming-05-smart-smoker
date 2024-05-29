import time
import csv

def read_tasks_from_csv(filename: str): #, host: str, queue:str):
    data = {'Channel1': [], 'Channel2': [], 'Channel3': []}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        next(reader) #skips header
        for row in reader:
            time_utc = row['Time (UTC)']
            data['Channel1'].append((time_utc, row['Channel1']))
            data['Channel2'].append((time_utc, row['Channel2']))
            data['Channel3'].append((time_utc, row['Channel3']))
            time.sleep(1)
        print(data)
        return data
    
if __name__ == "__main__":  
#    offer_rabbitmq_admin_site()    

    # variable to reference where the task csv is stored
    temp_file = 'smoker-temps.csv'
    #host = 'localhost'
    read_tasks_from_csv(temp_file)