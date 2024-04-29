import random

# constants
READ = 0
WRITE = 1
FETCH = 2

class Cache:
    def __init__(self, size_kb, line_size, associativity, memory_system):
        self.size_kb = size_kb
        self.line_size = line_size
        self.associativity = associativity
        self.num_lines = (size_kb * 1024) // line_size
        self.num_sets = self.num_lines // associativity
        self.cache = {i: [None]*associativity for i in range(self.num_sets)}
        self.memory_system = memory_system

    # evict a line in a given cache
    def evict_line(self, cache, address):
        set_index = (address // cache.line_size) % cache.num_sets
        tag = (address // cache.line_size) // cache.num_sets
        line = cache.cache[set_index]

        for i, entry in enumerate(line):
            if entry and entry['tag'] == tag:
                line[i] = None
                break

    # write data to memory
    def write_back(self, line, address):
        data = line['data']
        self.memory_system.dram[address] = data

    def access(self, address, type, data=None, writeback=False):
        # find indexing information
        set_index = (address // self.line_size) % self.num_sets
        tag = (address // self.line_size) // self.num_sets
        line = self.cache[set_index]
        
        found = False
        empty_slot = None

        # check if this line's tag matches, if not keep track that it is empty
        for i, entry in enumerate(line):
            if entry and entry['tag'] == tag:
                found = True
                break
            elif not entry and empty_slot is None:
                empty_slot = i
       
        if not found:
            # if the line was empty, let's use it
            if empty_slot is not None:
                i = empty_slot
            else:
                # otherwise, select a line at random (for L2) or evict the line
                i = random.randint(0, self.associativity - 1)
                # if we are evicting a dirty line from the L2
                if self == self.memory_system.l2 and line[i]['dirty'] == True:
                    # write back to memory (energy already included in penalty)
                    self.write_back(line[i], address)
                    # evict from the right l1 cache to maintain inclusivity
                    if type in (READ, WRITE):
                        self.evict_line(self.memory_system.l1_data, address)
                    else:
                        self.evict_line(self.memory_system.l1_inst, address)

            # update the line
            line[i] = {'tag': tag, 'data': data, 'dirty': False}

        # set the dirty bit
        if type == WRITE:
            line[i]['dirty'] = True
            
        return (found, line[i]['data'] if line[i] else None)
    
class MemorySystem:
    def __init__(self):
        self.l1_data = Cache(32, 64, 1, self)
        self.l1_inst = Cache(32, 64, 1, self)
        self.l2 = Cache(256, 64, 2, self)
        self.dram = {}
        self.memory_accesses = 0
        self.active_time = {'l1_data': 0, 'l1_inst': 0, 'l2': 0, 'dram': 0}
        self.idle_time = {'l1_data': 0, 'l1_inst': 0, 'l2': 0, 'dram': 0}
        self.hits = {'l1_data': 0, 'l1_inst': 0, 'l2': 0, 'dram': 0}
        self.misses = {'l1_data': 0, 'l1_inst': 0, 'l2': 0, 'dram': 0}
        self.penalties = {'l2': 0, 'dram': 0}
        self.global_clock = 0 

    # energy calculations, where reads/fetches stall the pipeline but writes do not
    def add_time_and_energy(self, cache, type):
        if type == READ or type == FETCH: 
            if cache == 'l1_data':
                self.active_time['l1_data'] += 0.5
                self.idle_time['l1_inst'] += 0.5 
                self.idle_time['l2'] += 0.5
                self.idle_time['dram'] += 0.5
                self.global_clock += 0.5
            elif cache == 'l1_inst':
                self.active_time['l1_inst'] += 0.5
                self.idle_time['l1_data'] += 0.5
                self.idle_time['l2'] += 0.5
                self.idle_time['dram'] += 0.5
                self.global_clock += 0.5
            elif cache == 'l2':
                self.penalties['l2'] += 0.005
                self.active_time['l2'] += 4.5
                self.idle_time['l1_data'] += 4.5 
                self.idle_time['l1_inst'] += 4.5 
                self.idle_time['dram'] += 4.5
                self.global_clock += 4.5
            else:
                self.penalties['dram'] += 0.64
                self.active_time['dram'] += 45
                self.idle_time['l1_data'] += 45
                self.idle_time['l1_inst'] += 45
                self.idle_time['l2'] += 45
                self.global_clock += 45
        else: 
            if cache == 'l1_data':
                self.active_time['l1_data'] += 0.5
            elif cache == 'l1_inst':
                self.active_time['l1_inst'] += 0.5
            elif cache == 'l2':
                self.penalties['l2'] += 0.005
                self.active_time['l2'] += 4.5
            else:
                self.penalties['dram'] += 0.64
                self.active_time['dram'] += 45

    def perform_access(self, type, address, data=None):
        # l1 data cache if read, write/l1 instruction otherwise
        cache = self.l1_data if type in (READ, WRITE) else self.l1_inst
        
        # increment time and energy spent + access the cache
        if type == READ or type == WRITE:
            self.add_time_and_energy('l1_data', type)
        elif type == FETCH:
            self.add_time_and_energy('l1_inst', type)
        hit, fetched_data = cache.access(address, type, data)
    
        # missed in L1, going to L2
        if not hit:
            # update misses respectively
            if type == READ or type == WRITE:
                self.misses['l1_data'] += 1
            else: 
                self.misses['l1_inst'] +=1

            # increment time and energy spent + access caache
            self.add_time_and_energy('l2', type)
            hit, fetched_data = self.l2.access(address, type, data)
            
            # no data transfer here occurring between L1, L2
            self.penalties['l2'] -= 0.005
            
            # missed in L2, going to memory
            if not hit:
                # update hits, misses respectively
                self.misses['l2'] +=1
                self.hits['dram']+=1
            
                # read information from memory
                self.add_time_and_energy('dram', READ)
                fetched_data = self.dram.get(address, None)
                
                # write miss means we have to first bring the old cache line to
                # both caches, then perform a write through from L1 to L2
                if type == WRITE:
                    # bring in old cache line (copying data DRAM -> L2 energy/
                    # time cost included in penalty already)
                    self.l2.access(address, WRITE, fetched_data)
                    self.l1_data.access(address, WRITE, fetched_data)
                    # need to add cost for accessing L1
                    self.add_time_and_energy('l1_data', WRITE)

                    # now, just a regular write to L2 with new data, include cost
                    # and penalty
                    self.add_time_and_energy('l2', WRITE)
                    self.l2.access(address, WRITE, data)
                    # a regular write to L1 with new data, include cost
                    self.add_time_and_energy('l1_data', WRITE)
                    self.l1_data.access(address, WRITE, data)
                    
                # read miss means we have to bring data to both caches
                if type == READ:
                    # energy/time included in penalty when writing from DRAM
                    self.l2.access(address, WRITE, data)
                    # energy/time included in penalty when writing from L2 to L1
                    self.penalties['l2'] += 0.005
                    # data transfer from the L2 to the L1 
                    self.l1_data.access(address, WRITE, data)
               
                # fetch miss means we have to bring data to L2
                if type == FETCH:
                    # energy/time included in penalty when writing from DRAM
                    self.l2.access(address, WRITE, data)

            # L1 miss, L2 hit    
            else:
                self.hits['l2'] += 1
                # on an L1 missed write/read, copy data from L2 to L1
                if type == WRITE or type == READ:
                    self.penalties['l2'] += 0.005
                    # data transfer to the L1 
                    self.l1_data.access(address, WRITE, fetched_data)
        # L1 hit
        else:
            # increment hits respectively
            if type in (READ, WRITE):
                self.hits['l1_data'] +=1
                # if L1 write hit, we need to update in L2
                if type == WRITE:
                    # no penalty to write between L2, L1 because this is the
                    # write through policy
                    self.add_time_and_energy('l2', WRITE)
                    self.penalties['l2'] -= 0.005
                    self.l2.access(address, WRITE, fetched_data)
            else:
                self.hits['l1_inst'] +=1

def simulate_cache(trace_file):
    memory_system = MemorySystem()
    with open(trace_file, 'r') as file:
        for line in file:
            parts = line.split()
            type = int(parts[0])
            address = int(parts[1], 16)
            data = int(parts[2], 16) if type == 1 else None
            memory_system.perform_access(type, address, data)

    # print results
    print("******* HITS/MISSES *******")
    print("L1 Data Cache Hits:", memory_system.hits['l1_data'])
    print("L1 Data Cache Misses:", memory_system.misses['l1_data'])
    print("L1 Instruction Cache Hits:", memory_system.hits['l1_inst'])
    print("L1 Instruction Cache Misses:", memory_system.misses['l1_inst'])
    print("L1 Total Cache Hits:", memory_system.hits['l1_data'] + memory_system.hits['l1_inst'])
    print("L1 Total Cache Misses:", memory_system.misses['l1_data'] + memory_system.misses['l1_inst'])
    print("L2 Cache Hits:", memory_system.hits['l2'])
    print("L2 Cache Misses:", memory_system.misses['l2'])
    print("DRAM Accesses:", memory_system.hits['dram'])
    print()
    print("******* TIME *******")
    print("Total time taken to execute the simulation:", (memory_system.global_clock), "ns")
    print()
    """
    print("******* STATIC ENERGY *******")
    print("Energy spent in L1 Data Cache:", (memory_system.idle_time['l1_data'] * 0.5),"nJ")
    print("Energy spent in L1 Instruction Cache:", (memory_system.idle_time['l1_inst'] * 0.5),"nJ")
    print("Total energy spent in L1 Cache:", (((memory_system.idle_time['l1_inst'] + memory_system.idle_time['l1_data']))* 0.5),"nJ")
    print("Energy spent in L2 Cache:", (memory_system.idle_time['l2'] * 0.8),"nJ")
    print("Energy spent in DRAM:", (memory_system.idle_time['dram'] * 0.8),"nJ")
    print("Total:", (((memory_system.idle_time['dram'])  * 0.8 + (memory_system.idle_time['l1_data']) * 0.5 + (memory_system.idle_time['l1_inst']) * 0.5 + (memory_system.idle_time['l2'] * 0.8))),"nJ")
   """
    print()
    l1_inst_dynamic = memory_system.active_time['l1_data'] * 1
    l1_data_dynamic = memory_system.active_time['l1_inst'] * 1
    l2_dynamic = memory_system.active_time['l2'] * 2 + memory_system.penalties['l2']
    dram_dynamic = memory_system.active_time['dram'] * 4 + memory_system.penalties['dram']
    print("******* TOTAL ENERGY *******")
    print("Energy spent in L1 Data Cache:", l1_inst_dynamic + memory_system.idle_time['l1_data'] * 0.5,"nJ")
    print("Energy spent in L1 Instruction Cache:", l1_data_dynamic + memory_system.idle_time['l1_inst'] * 0.5,"nJ")
    print("Total energy spent in L1 Cache:", l1_data_dynamic + l1_inst_dynamic + (((memory_system.idle_time['l1_inst'] + memory_system.idle_time['l1_data']))* 0.5),"nJ")
    print("Energy spent in L2 Cache:", l2_dynamic + (memory_system.idle_time['l2'] * 0.8),"nJ")
    print("Energy spent in DRAM:", dram_dynamic + (memory_system.idle_time['dram'] * 0.8),"nJ")
    print("Total:", l1_data_dynamic + l1_inst_dynamic + l2_dynamic + dram_dynamic + (((memory_system.idle_time['dram'])  * 0.8 + (memory_system.idle_time['l1_data']) * 0.5 + (memory_system.idle_time['l1_inst']) * 0.5 + (memory_system.idle_time['l2'] * 0.8))),"nJ")
   
simulate_cache('008.espresso.din')