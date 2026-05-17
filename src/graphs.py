import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

directory = 'results'
filenames = ["FCFS_output.csv", "SJF_output.csv", "PRIORITY_output.csv", "MLFQ_output.csv" ]
algorithms = ["FCFS", "SJF", "PRIORITY", "MLFQ"]

def read_file(filename): 

    path = os.path.join(directory, filename)
    
    with open(path, 'r') as f: 
        return f.readlines()

def parse_file(content, path): 

    algorithm = path.replace("_output.csv", "")
    current_patron_num = None
    rows = []

    for line in content: 

        line=line.strip()

        if line.startswith("#Patrons"): 
            current_patron_num = int(line.split("=")[1])

        elif line and current_patron_num is not None: 
            parts = line.split(', ')
            rows.append({
                'Algorithm': algorithm, 
                'Num_patrons': current_patron_num, 
                'Patron' : int(parts[0]),
                'Drink' : int(parts[1]),
                'Arrival' : int(parts[2]),
                'Wait' : int(parts[3]),
                'Turnaround' : int(parts[4]),
                'Exec' : int(parts[5])
            })

    return rows

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def plot(df): 

    # Graph 1: Box plot of waiting time per algorithm (base case 30 patrons)
    base = df[df['Num_patrons'] == 30]

    if not base.empty:
        plt.figure(figsize=(10, 6))
        base.boxplot(column='Wait', by='Algorithm')
        plt.suptitle('')
        plt.title('Distribution of Waiting Time (30 Patrons)')
        plt.ylabel('Wait Time (ms)')
        plt.xlabel('Algorithm')
        plt.savefig(os.path.join(directory, 'wait_distribution_30.png'))
        print("Saved wait_distribution_30.png")
        plt.close()

    # Graph 2: Box plot of turnaround time per algorithm (base case 30 patrons)
    if not base.empty:
        plt.figure(figsize=(10, 6))
        base.boxplot(column='Turnaround', by='Algorithm')
        plt.suptitle('')
        plt.title('Distribution of Turnaround Time (30 Patrons)')
        plt.ylabel('Turnaround Time (ms)')
        plt.xlabel('Algorithm')
        plt.savefig(os.path.join(directory, 'turnaround_distribution_30.png'))
        print("Saved turnaround_distribution_30.png")
        plt.close()

    # Graph 3: Mean and median wait time per algorithm (base case 30 patrons)
    if not base.empty:
        summary = base.groupby('Algorithm')['Wait'].agg(['mean', 'median']).reindex(algorithms)
        summary.plot(kind='bar', figsize=(10, 6))
        plt.title('Mean vs Median Wait Time (30 Patrons)')
        plt.ylabel('Wait Time (ms)')
        plt.xlabel('Algorithm')
        plt.xticks(rotation=0)
        plt.savefig(os.path.join(directory, 'mean_median_wait_30.png'))
        print("Saved mean_median_wait_30.png")
        plt.close()

    # Graph 4: Line graph mean wait vs patron count per algorithm
    scaling = df.groupby(['Algorithm', 'Num_patrons'])['Wait'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Num_patrons', y='Wait', hue='Algorithm',
                 hue_order=algorithms, marker='o', data=scaling)
    plt.title('Scaling: Mean Wait Time vs Number of Patrons')
    plt.ylabel('Mean Wait Time (ms)')
    plt.xlabel('Number of Patrons')
    plt.grid(True)
    plt.savefig(os.path.join(directory, 'scaling_wait.png'))
    print("Saved scaling_wait.png")
    plt.close()

    # Graph 5: Per-patron total wait (base case 30 patrons)
    if not base.empty:
        patron_totals = base.groupby(['Algorithm', 'Patron'])['Wait'].sum().reset_index()
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Patron', y='Wait', hue='Algorithm',
                    hue_order=algorithms, data=patron_totals)
        plt.title('Total Wait Per Patron by Algorithm (30 Patrons)')
        plt.ylabel('Total Wait Time (ms)')
        plt.xlabel('Patron ID')
        plt.savefig(os.path.join(directory, 'fairness_per_patron.png'))
        print("Saved fairness_per_patron.png")
        plt.close()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main(): 

    for file in filenames: 
        file_contents = read_file(file)
        data = parse_file(file_contents, file)
        plot(data, "results")

if __name__ == "__main__":
    main()
