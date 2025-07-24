import heapq
import random
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
SERVICE_RATE = 1.0  
SIMULATION_TIME = 100000  

def exponential(mean):
    return random.expovariate(1.0 / mean)

class Event:
    def __init__(self, time, event_type, customer_type):
        self.time = time
        self.event_type = event_type  
        self.customer_type = customer_type 

    def __lt__(self, other):
        return self.time < other.time

def simulate_mm1_priority(lambda_total, f):
    lambda_fastpass = lambda_total * f
    lambda_regular = lambda_total * (1 - f)

    event_queue = []
    clock = 0.0

    queue_fastpass = []
    queue_regular = []
    in_service = None
    next_departure_time = float('inf')

    response_times_fp = []
    response_times_reg = []

    def schedule_arrival(customer_type):
        rate = lambda_fastpass if customer_type == 'fastpass' else lambda_regular
        if rate > 0:
            interarrival_time = exponential(1.0 / rate)
            heapq.heappush(event_queue, Event(clock + interarrival_time, 'arrival', customer_type))


    schedule_arrival('fastpass')
    schedule_arrival('regular')

    while clock < SIMULATION_TIME:
        if not event_queue:
            break

        event = heapq.heappop(event_queue)
        clock = event.time

        if event.event_type == 'arrival':
            arrival_time = clock
            if event.customer_type == 'fastpass':
                queue_fastpass.append(arrival_time)
                schedule_arrival('fastpass')
            else:
                queue_regular.append(arrival_time)
                schedule_arrival('regular')

            if in_service is None:
                if queue_fastpass:
                    start_time = clock
                    arrival_time = queue_fastpass.pop(0)
                    in_service = 'fastpass'
                    residence = exponential(1.0 / SERVICE_RATE)
                    response_times_fp.append(clock - arrival_time + residence)
                    heapq.heappush(event_queue, Event(clock + residence, 'departure', 'fastpass'))
                elif queue_regular:
                    start_time = clock
                    arrival_time = queue_regular.pop(0)
                    in_service = 'regular'
                    residence = exponential(1.0 / SERVICE_RATE)
                    response_times_reg.append(clock - arrival_time + residence)
                    heapq.heappush(event_queue, Event(clock + residence, 'departure', 'regular'))

        elif event.event_type == 'departure':
            in_service = None
            if queue_fastpass:
                arrival_time = queue_fastpass.pop(0)
                in_service = 'fastpass'
                residence = exponential(1.0 / SERVICE_RATE)
                response_times_fp.append(clock - arrival_time + residence)
                heapq.heappush(event_queue, Event(clock + residence, 'departure', 'fastpass'))
            elif queue_regular:
                arrival_time = queue_regular.pop(0)
                in_service = 'regular'
                residence = exponential(1.0 / SERVICE_RATE)
                response_times_reg.append(clock - arrival_time + residence)
                heapq.heappush(event_queue, Event(clock + residence, 'departure', 'regular'))

    avg_fp = np.mean(response_times_fp) if response_times_fp else 0
    avg_reg = np.mean(response_times_reg) if response_times_reg else 0
    return avg_fp, avg_reg

# Run simulations for high-load and low-load scenarios
def run_experiments(lambda_val):
    f_values = np.arange(0, 1.0, 0.05)
    results_fp = []
    results_reg = []
    for f in f_values:
        avg_fp, avg_reg = simulate_mm1_priority(lambda_val, f)
        results_fp.append(avg_fp)
        results_reg.append(avg_reg)
    return f_values, results_fp, results_reg

# Run high-load
f_high, res_fp_high, res_reg_high = run_experiments(0.95)
# Run low-load
f_low, res_fp_low, res_reg_low = run_experiments(0.50)

# Print high-load results
print("HIGH-LOAD RESULTS (λ=0.95):")
for i, f in enumerate(f_high):
    fp_time = res_fp_high[i] if i > 0 else "N/A"  # No FastPass for f=0
    reg_time = res_reg_high[i]
    print(f"f = {f:.2f}: FastPass time = {fp_time}, Regular time = {reg_time:.2f} min")

# Print low-load results
print("\nLOW-LOAD RESULTS (λ=0.50):")
for i, f in enumerate(f_low):
    fp_time = res_fp_low[i] if i > 0 else "N/A"  # No FastPass for f=0
    reg_time = res_reg_low[i]
    print(f"f = {f:.2f}: FastPass time = {fp_time}, Regular time = {reg_time:.2f} min")

# Calculate recommended FastPass percentages
# For high load - Find balance between FastPass benefit and regular customer penalty
baseline_high = res_reg_high[0]  # Time with no FastPass
high_load_score = []

for i, f in enumerate(f_high):
    if i == 0:  
        high_load_score.append(0)
        continue
    
    fp_benefit = baseline_high - res_fp_high[i]  
    reg_penalty = res_reg_high[i] - baseline_high  
    
    # Score is the ratio of benefit to penalty, with a penalty for very high regular wait times
    if reg_penalty > 0:
        # Penalize cases where regular time > 2x baseline
        penalty_factor = 1.0 if res_reg_high[i] < 2*baseline_high else 0.5
        score = (fp_benefit / reg_penalty) * penalty_factor
        high_load_score.append(score)
    else:
        high_load_score.append(float('inf'))  

# Find best f value for high load
best_high_idx = high_load_score.index(max([s for s in high_load_score if s < float('inf')]))
best_high_f = f_high[best_high_idx]

# For low load
baseline_low = res_reg_low[0]  
low_load_score = []

for i, f in enumerate(f_low):
    if i == 0:  
        low_load_score.append(0)
        continue
    
    fp_benefit = baseline_low - res_fp_low[i]  
    reg_penalty = res_reg_low[i] - baseline_low  
    
    # Score is the ratio of benefit to penalty, with a cap to prevent division by very small numbers
    if reg_penalty > 0.05: 
        score = fp_benefit / reg_penalty
        low_load_score.append(score)
    else:
        low_load_score.append(1.0)  

# Find best f value for low load
best_low_idx = min(len(low_load_score)-1, 12)  
best_low_f = f_low[best_low_idx]

# Print recommendations
print("\nRECOMMENDED FASTPASS ALLOCATIONS:")
print(f"High-Load (λ=0.95): {best_high_f:.2f} or {int(best_high_f*100)}% FastPasses")
print(f"Low-Load (λ=0.50): {best_low_f:.2f} or {int(best_low_f*100)}% FastPasses")
print("\nRESULTS:")
print(f"High-Load: At f={best_high_f:.2f}, FastPass time = {res_fp_high[best_high_idx]:.2f} min, Regular time = {res_reg_high[best_high_idx]:.2f} min")
print(f"  - FastPass benefit: {baseline_high - res_fp_high[best_high_idx]:.2f} min faster than baseline ({baseline_high:.2f} min)")
print(f"  - Regular penalty: {res_reg_high[best_high_idx] - baseline_high:.2f} min slower than baseline")
print(f"Low-Load: At f={best_low_f:.2f}, FastPass time = {res_fp_low[best_low_idx]:.2f} min, Regular time = {res_reg_low[best_low_idx]:.2f} min")
print(f"  - FastPass benefit: {baseline_low - res_fp_low[best_low_idx]:.2f} min faster than baseline ({baseline_low:.2f} min)")
print(f"  - Regular penalty: {res_reg_low[best_low_idx] - baseline_low:.2f} min slower than baseline")


# Plotting results
plt.figure()
plt.plot(f_high, res_fp_high, label="FastPass (λ=0.95)")
plt.plot(f_high, res_reg_high, label="Regular (λ=0.95)")
plt.xlabel("Fraction of FastPass users (f)")
plt.ylabel("Average Residence Time (minutes)")
plt.title("High-Load Period")
plt.legend()
plt.grid(True)
plt.savefig("high_load_results.png")

plt.figure()
plt.plot(f_low, res_fp_low, label="FastPass (λ=0.50)")
plt.plot(f_low, res_reg_low, label="Regular (λ=0.50)")
plt.xlabel("Fraction of FastPass users (f)")
plt.ylabel("Average Residence Time (minutes)")
plt.title("Low-Load Period")
plt.legend()
plt.grid(True)
plt.savefig("low_load_results.png")

