import random
import matplotlib.pyplot as plt

nodes_count = 2000
simulation_time_hours = 24 * 365
mtbf_node_years = 0.5
mtbf_node_hours = mtbf_node_years * 24 * 365
mttr_node_days = 20
continue_simulation = True
next_failure_hours = [random.expovariate(1.0 / mtbf_node_hours) for i in range(nodes_count)]
simulation_clock_hours = 0
step = 0
failures = 0
repair_queue = []
availability_chart = []


while continue_simulation:
    step = step + 1

    # find the node with the next failure
    # find the time of the next failure
    node_with_next_failure = next_failure_hours.index(min(next_failure_hours))
    time_of_next_failure = next_failure_hours[node_with_next_failure]
    
    #find the next repair completion time
    if (len(repair_queue) > 0):
        repaired_node, repair_completion_time = min(repair_queue, key=lambda x: x[1])
    else:
        repair_completion_time = float("inf")
        repaired_node = None

    next_change_time = min(time_of_next_failure, repair_completion_time)
    availability_chart.append((next_change_time, nodes_count - len(repair_queue)))

    # check what we are simulating in this cycle - repair completion or another failure
    if time_of_next_failure < repair_completion_time:
        # we are simulating a failure
        # update the next failure time for the failed node
        failures = failures + 1
    
        # update the simulation time to the next event which is the next failure
        simulation_clock_hours = time_of_next_failure

        print(f"Step: {step}, Clock: {simulation_clock_hours}, failed node: {node_with_next_failure}")

        #compute the time to repair the failed node
        time_to_repair = simulation_clock_hours + mttr_node_days * 24
        # add the failed node to the repair queue
        repair_queue.append((node_with_next_failure, time_to_repair))

        # set the node's next failure time to infinity to indicate that it is in the repair queue
        next_failure_hours[node_with_next_failure] = float("inf")
    else:
        # we are simulating a repair completion
        # update the simulation time to the next event which is the next repair completion
        simulation_clock_hours = repair_completion_time

        print(f"Step: {step}, Clock: {simulation_clock_hours}, repaired node: {repaired_node}")

        # remove the repaired node from the repair queue
        repair_queue.remove((repaired_node, repair_completion_time))

        # return the node to the pool of healthy nodes and set its next failure time
        next_failure_hours[repaired_node] = simulation_clock_hours + random.expovariate(1.0 / mtbf_node_hours)
    
    print(f"Step {step}, repair queue count: {len(repair_queue)}")    

    # check if the simulation should continue
    continue_simulation = simulation_clock_hours < simulation_time_hours


print(f"Total failures: {failures}")
print(f"Expected average available cluster size: {nodes_count * mtbf_node_hours / (mtbf_node_hours + mttr_node_days * 24)}")

min_nodes_count = min(availability_chart, key=lambda x: x[1])
print(f"Minimum number of nodes: {min_nodes_count[1]} at time {min_nodes_count[0]}")


plt.plot(*zip(*availability_chart))
plt.xlabel("Time (hours)")
plt.ylabel("Number of healthy nodes")
plt.title("Availability chart")
plt.ylim(0, nodes_count)
plt.show()


# generate accomulated compute hours of the cluster
compute_hours = []
for i in range(1, len(availability_chart)):
    time_start = availability_chart[i - 1][0]
    time_end = availability_chart[i][0]
    nodes_available = availability_chart[i - 1][1]
    compute_hours.append(nodes_available * (time_end - time_start))

import numpy as np

a = compute_hours
p = [50, 90, 95, 99, 99.9]
max_compute_hours = nodes_count * simulation_time_hours
y_ticks = np.arange(0, max_compute_hours, max_compute_hours / 1000)
ax = plt.gca()
lines = [
    ('linear', '-', 'C0'),
    ('inverted_cdf', ':', 'C1')    
    ]
for method, style, color in lines:
    pp = np.percentile(a, p, method=method)
    ax.plot(
        p, pp,
        label=method, linestyle=style, color=color)
ax.set(
    title='Percentiles for compute hours',
    xlabel='Percentile',
    ylabel='Estimated percentile value')
    #yticks=y_ticks)
ax.legend()
plt.show()