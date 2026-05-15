---
name: python-performance-optimization
description: Profile and optimize Python code using cProfile, memory profilers, and performance best practices. Use when debugging slow Python code, optimizing bottlenecks, or improving application performance.
---
# Python Performance Optimization
Comprehensive guide to profiling, analyzing, and optimizing Python code for better performance, including CPU profiling, memory optimization, and implementation best practices.
## When to Use This Skill
- Identifying performance bottlenecks in Python applications
- Reducing application latency and response times
- Optimizing CPU-intensive operations
- Reducing memory consumption and memory leaks
- Improving database query performance
- Optimizing I/O operations
- Speeding up data processing pipelines
- Implementing high-performance algorithms
- Profiling production applications
## Core Concepts
### 1. Profiling Types
- **CPU Profiling**: Identify time-consuming functions
- **Memory Profiling**: Track memory allocation and leaks
- **Line Profiling**: Profile at line-by-line granularity
- **Call Graph**: Visualize function call relationships
### 2. Performance Metrics
- **Execution Time**: How long operations take
- **Memory Usage**: Peak and average memory consumption
- **CPU Utilization**: Processor usage patterns
- **I/O Wait**: Time spent on I/O operations
### 3. Optimization Strategies
- **Algorithmic**: Better algorithms and data structures
- **Implementation**: More efficient code patterns
- **Parallelization**: Multi-threading/processing
- **Caching**: Avoid redundant computation
- **Native Extensions**: C/Rust for critical paths
## Quick Start
### Basic Timing
```python
import time
def measure_time():
    """Simple timing measurement."""
    start = time.time()
    # Your code here
    result = sum(range(1000000))
    elapsed = time.time() - start
    print(f"Execution time: {elapsed:.4f} seconds")
    return result
# Better: use timeit for accurate measurements
import timeit
execution_time = timeit.timeit(
    "sum(range(1000000))",
    number=100
)
print(f"Average time: {execution_time/100:.6f} seconds")
```
## Profiling Tools
### Pattern 1: cProfile - CPU Profiling
```python
import cProfile
import pstats
from pstats import SortKey
def slow_function():
    """Function to profile."""
    total = 0
    for i in range(1000000):
        total += i
    return total
def another_function():
    """Another function."""
    return [i**2 for i in range(100000)]
def main():
    """Main function to profile."""
    result1 = slow_function()
    result2 = another_function()
    return result1, result2
# Profile the code
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)  # Top 10 functions
    # Save to file for later analysis
    stats.dump_stats("profile_output.prof")
```
**Command-line profiling:**
```bash
# Profile a script
python -m cProfile -o output.prof script.py
# View results
python -m pstats output.prof
# In pstats:
# sort cumtime
# stats 10
```
### Pattern 2: line_profiler - Line-by-Line Profiling
```python
# Install: pip install line-profiler
# Add @profile decorator (line_profiler provides this)
@profile
def process_data(data):
    """Process data with line profiling."""
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result
# Run with:
# kernprof -l -v script.py
```
### Pattern 3: memory_profiler - Memory Usage
```python
# Install: pip install memory-profiler
from memory_profiler import profile
@profile
def memory_intensive():
    """Function that uses lots of memory."""
    # Create large list
    big_list = [i for i in range(1000000)]
    # Create large dict
    big_dict = {i: i**2 for i in range(100000)}
    # Process data
    result = sum(big_list)
    return result
if __name__ == "__main__":
    memory_intensive()
# Run with:
# python -m memory_profiler script.py
```
### Pattern 4: py-spy - Production Profiling
```bash
# Install: pip install py-spy
# Profile a running Python process
py-spy top --pid 12345
# Generate flamegraph
py-spy record -o profile.svg --pid 12345
# Profile a script
py-spy record -o profile.svg -- python script.py
# Dump current call stack
py-spy dump --pid 12345
```
## Optimization Patterns
### Pattern 5: List Comprehensions vs Loops
```python
import timeit
# Slow: Traditional loop
def slow_squares(n):
    """Create list of squares using loop."""
    result = []
    for i in range(n):
        result.append(i**2)
    return result
# Fast: List comprehension
def fast_squares(n):
    """Create list of squares using comprehension."""
    return [i**2 for i in range(n)]
# Benchmark
n = 100000
slow_time = timeit.timeit(lambda: slow_squares(n), number=100)
fast_time = timeit.timeit(lambda: fast_squares(n), number=100)
print(f"Loop: {slow_time:.4f}s")
print(f"Comprehension: {fast_time:.4f}s")
print(f"Speedup: {slow_time/fast_time:.2f}x")
```
### Pattern 6: Generator Expressions for Memory
```python
import sys
def list_approach():
    """Memory-intensive list."""
    data = [i**2 for i in range(1000000)]
    return sum(data)
def generator_approach():
    """Memory-efficient generator."""
    data = (i**2 for i in range(1000000))
    return sum(data)
# Memory comparison
list_data = [i for i in range(1000000)]
gen_data = (i for i in range(1000000))
print(f"List size: {sys.getsizeof(list_data)} bytes")
print(f"Generator size: {sys.getsizeof(gen_data)} bytes")
# Generators use constant memory regardless of size
```
### Pattern 7: String Concatenation
```python
import timeit
def slow_concat(items):
    """Slow string concatenation."""
    result = ""
    for item in items:
        result += str(item)
    return result
def fast_concat(items):
    """Fast string concatenation with join."""
    return "".join(str(item) for item in items)
def faster_concat(items):
    """Even faster with list."""
    parts = [str(item) for item in items]
    return "".join(parts)
items = list(range(10000))
# Benchmark
slow = timeit.timeit(lambda: slow_concat(items), number=100)
fast = timeit.timeit(lambda: fast_concat(items), number=100)
faster = timeit.timeit(lambda: faster_concat(items), number=100)
print(f"Concatenation (+): {slow:.4f}s")
print(f"Join (generator): {fast:.4f}s")
print(f"Join (list): {faster:.4f}s")
```
### Pattern 8: Dictionary Lookups vs List Searches
```python
import timeit
# Create test data
size = 10000
items = list(range(size))
lookup_dict = {i: i for i in range(size)}
def list_search(items, target):
    """O(n) search in list."""
    return target in items
def dict_search(lookup_dict, target):
    """O(1) search in dict."""
    return target in lookup_dict
target = size - 1  # Worst case for list
# Benchmark
list_time = timeit.timeit(
    lambda: list_search(items, target),
    number=1000
)
dict_time = timeit.timeit(
    lambda: dict_search(lookup_dict, target),
    number=1000
)
print(f"List search: {list_time:.6f}s")
print(f"Dict search: {dict_time:.6f}s")
print(f"Speedup: {list_time/dict_time:.0f}x")
```
## Best Practices
1. **Profile before optimizing** - Measure to find real bottlenecks
2. **Focus on hot paths** - Optimize code that runs most frequently
3. **Use appropriate data structures** - Dict for lookups, set for membership
4. **Avoid premature optimization** - Clarity first, then optimize
5. **Use built-in functions** - They're implemented in C
6. **Cache expensive computations** - Use lru_cache
7. **Batch I/O operations** - Reduce system calls
8. **Use generators** for large datasets
9. **Consider NumPy** for numerical operations
10. **Profile production code** - Use py-spy for live systems
