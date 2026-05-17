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
            current_patron_num = int(line.split("=")[1].strip())

        elif line and current_patron_num is not None: 
            parts = line.split(', ')
            rows.append({
                'Algorithm': algorithm, 
                'Num_patrons': current_patron_num, 
                'Patron' : int(parts[0]),
                'Drink' : str(parts[1]),
                'Arrival' : int(parts[2]),
                'Wait' : int(parts[3]),
                'Turnaround' : int(parts[4]),
                'Exec' : int(parts[5])
            })

    return rows

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def plot(df): 

    # Cleanup
    for f in os.listdir(directory):
        if f.endswith('.png'):
            os.remove(os.path.join(directory, f))

    patron_counts = sorted(df['Num_patrons'].unique())

    # Graph 1: Box plot of waiting time - subplot per patron count
    fig, axes = plt.subplots(1, len(patron_counts), figsize=(18, 6), sharey=True)
    for ax, n in zip(axes, patron_counts):
        subset = df[df['Num_patrons'] == n]
        subset.boxplot(column='Wait', by='Algorithm', ax=ax)
        ax.set_title(f'{n} Patrons')
        ax.set_xlabel('')
        ax.set_ylabel('Wait Time (ms)' if ax == axes[0] else '')
    fig.suptitle('Distribution of Waiting Time Across All Patron Counts')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'wait_distribution.png'))
    print("Saved wait_distribution.png")
    plt.close()

    # Graph 2: Box plot of turnaround time - all patron counts
    fig, axes = plt.subplots(1, len(patron_counts), figsize=(18, 6), sharey=True)
    for ax, n in zip(axes, patron_counts):
        subset = df[df['Num_patrons'] == n]
        subset.boxplot(column='Turnaround', by='Algorithm', ax=ax)
        ax.set_title(f'{n} Patrons')
        ax.set_xlabel('')
        ax.set_ylabel('Turnaround Time (ms)' if ax == axes[0] else '')
    fig.suptitle('Distribution of Turnaround Time Across All Patron Counts')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'turnaround_distribution.png'))
    print("Saved turnaround_distribution.png")
    plt.close()

    # Graph 3: Mean vs median wait - subplot per patron count
    fig, axes = plt.subplots(1, len(patron_counts), figsize=(18, 6), sharey=True)
    for ax, n in zip(axes, patron_counts):
        subset = df[df['Num_patrons'] == n]
        summary = subset.groupby('Algorithm')['Wait'].agg(['mean', 'median']).reindex(algorithms)
        summary.plot(kind='bar', ax=ax, legend=(ax == axes[-1]))
        ax.set_title(f'{n} Patrons')
        ax.set_xlabel('')
        ax.set_ylabel('Wait Time (ms)' if ax == axes[0] else '')
        ax.tick_params(axis='x', rotation=0)
    fig.suptitle('Mean vs Median Wait Time Across All Patron Counts')
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'mean_median_wait.png'))
    print("Saved mean_median_wait.png")
    plt.close()

    # Graph 4: line graph - mean wait vs patron count
    scaling = df.groupby(['Algorithm', 'Num_patrons'])['Wait'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Num_patrons', y='Wait', hue='Algorithm',
                 hue_order=algorithms, marker='o', data=scaling)
    plt.title('Mean Wait Time vs Number of Patrons')
    plt.ylabel('Mean Wait Time (ms)')
    plt.xlabel('Number of Patrons')
    plt.grid(True)
    plt.savefig(os.path.join(directory, 'mean_wait.png'))
    print("Saved mean_wait.png")
    plt.close()

    # Graph 5: wait time per patient variance
    fig, axes = plt.subplots(1, len(algorithms), figsize=(20, 6), sharey=True)
    for ax, algo in zip(axes, algorithms):
        subset = df[df['Algorithm'] == algo]
        patron_std = subset.groupby(['Num_patrons', 'Patron'])['Wait'].std().reset_index()
        sns.lineplot(x='Patron', y='Wait', hue='Num_patrons',
             data=patron_std, ax=ax, legend=(ax == axes[0]), palette='viridis')
        ax.set_title(algo)
        ax.set_xlabel('Patron ID')
        ax.set_ylabel('Std Dev of Wait (ms)' if ax == axes[0] else '')
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].get_legend().remove()
    fig.legend(handles, labels, title='Num Patrons', loc='upper center',  ncol=len(patron_counts), bbox_to_anchor=(0.5, 1.02))
    fig.suptitle('Wait Time Variance Per Patron', y=1.06)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, 'wait_variance.png'), bbox_inches='tight')
    print("Saved wait_variance.png")
    plt.close()

    # Throughput: total orders per second per algorithm per patron count
    df['throughput'] = 1  
    throughput = df.groupby(['Algorithm', 'Num_patrons']).agg(
        total_orders=('throughput', 'sum'),
        elapsed=('Turnaround', 'max')
    ).reset_index()
    throughput['orders_per_sec'] = throughput['total_orders'] / (throughput['elapsed'] / 1000)

    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Num_patrons', y='orders_per_sec', hue='Algorithm',
                hue_order=algorithms, marker='o', data=throughput)
    plt.title('Throughput vs Number of Patrons')
    plt.ylabel('Orders per Second')
    plt.xlabel('Number of Patrons')
    plt.grid(True)
    plt.savefig(os.path.join(directory, 'throughput.png'))
    print("Saved throughput.png")
    plt.close()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main(): 

    all_data = []

    for file in filenames: 
        file_contents = read_file(file)
        data = parse_file(file_contents, file)
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    print(f"Loaded {len(df)} rows")
    print(df.groupby(['Algorithm', "Num_patrons"]).size())
    plot(df)

if __name__ == "__main__":
    main()
