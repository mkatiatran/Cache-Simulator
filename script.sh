#!/bin/bash

# Array containing all file names
FILE_NAMES_TEST=("008.espresso.din")

# Types of associativies we're testing 
ASSOCS=(2 4 8)

# Function name
FUNCTION_NAME="simulate_cache"

# Formatted output file
OUTPUT_FILE="formatted_output.txt"

# Print what associativity we're testing
echo "THIS IS MY FIRST LINE" > "$OUTPUT_FILE"

for ASSOC in "${ASSOCS[@]}"; do
    # echo which associativity we're texting 
    echo "******************** L2 Associativity of $ASSOC ********************" >> "$OUTPUT_FILE"

    for FILE_NAME in "${FILE_NAMES_TEST[@]}"; do
        echo "---------- Processing trace file: $FILE_NAME ----------" >> "$OUTPUT_FILE"
        l1_i_hits_arr=()
        l1_i_misses_arr=()
        l1_i_energy_arr=()
        l1_d_hits_arr=()
        l1_d_misses_arr=()
        l1_d_energy_arr=()

        l2_hits_arr=()
        l2_misses_arr=()
        l2_energy_arr=()

        dram_access_arr=()

        dram_energy_arr=()
        total_energy_arr=()
        total_time_arr=()
        
        l1_hits_arr=()
        l1_misses_arr=()
        l1_energy_arr=()

        for ((iteration=1; iteration<=10; iteration++)); do
            if [ ! -f "$FILE_NAME" ]; then
                echo "Error: File $FILE_NAME not found!"
                exit 1
            fi

            # execute script then capture it
            output=$(python3 -c "from final import $FUNCTION_NAME; $FUNCTION_NAME('$FILE_NAME', $ASSOC)")
            # Add each value to the respective variable

            current_l1_i_hits=$(echo "$output" | awk '/L1 inst Cache Hits:/ {print $NF}')
            l1_i_hits_arr+=("$current_l1_i_hits")

            current_l1_i_misses=$(echo "$output" | awk '/L1 inst Cache Misses:/ {print $NF}')
            l1_i_misses_arr+=("$current_l1_i_misses")

            current_l1_i_energy=$(echo "$output" | awk '/L1 inst Energy:/ {print $NF}')
            l1_i_energy_arr+=("$current_l1_i_energy")

            current_l1_d_hits=$(echo "$output" | awk '/L1 data Cache Hits:/ {print $NF}')
            l1_d_hits_arr+=("$current_l1_d_hits")

            current_l1_d_misses=$(echo "$output" | awk '/L1 data Cache Misses:/ {print $NF}')
            l1_d_misses_arr+=("$current_l1_d_misses")

            current_l1_d_energy=$(echo "$output" | awk '/L1 data Energy:/ {print $NF}')
            l1_d_energy_arr+=("$current_l1_d_energy")

            current_dram_accesses=$(echo "$output" | awk '/DRAM Accesses:/ {print $NF}')
            dram_access_arr+=("$current_dram_accesses")

            current_l1_hits=$(echo "$output" | awk '/L1 Cache Hits:/ {print $NF}')
            l1_hits_arr+=("$current_l1_hits")

            current_l1_misses=$(echo "$output" | awk '/L1 Cache Misses:/ {print $NF}')
            l1_misses_arr+=("$current_l1_misses")

            current_l2_hits=$(echo "$output" | awk '/L2 Cache Hits:/ {print $NF}')
            l2_hits_arr+=("$current_l2_hits")

            current_l2_misses=$(echo "$output" | awk '/L2 Cache Misses:/ {print $NF}')
            l2_misses_arr+=("$current_l2_misses")

            current_l1_energy=$(echo "$output" | grep "L1 Energy(mJ):" | awk '{print $NF}')
            l1_energy_arr+=("$current_l1_energy")

            current_l2_energy=$(echo "$output" | grep "L2 Energy(mJ):" | awk '{print $NF}')
            l2_energy_arr+=("$current_l2_energy")

            current_dram_energy=$(echo "$output" | grep "DRAM Energy(mJ):" | awk '{print $NF}')
            dram_energy_arr+=("$current_dram_energy")

            current_total_energy=$(echo "$output" | grep "Total Energy(mJ):" | awk '{print $NF}')
            total_energy_arr+=("$current_total_energy")
            
            current_total_time=$(echo "$output" | grep "Total Time(ms):" | awk '{print $NF}')
            total_time_arr+=("$current_total_time")
        done

        printf "%24s %10s %10s\n" " " "MEAN" "STD DEV" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_i_hits_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Inst Cache Hits " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_i_misses_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Inst Cache Misses " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_i_energy_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Inst Energy (mJ) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_d_hits_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Data Cache Hits " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_d_misses_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Data Cache Misses " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_d_energy_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Data Cache Energy(mJ) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${dram_access_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "DRAM Accesses (ms) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_hits_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Cache Hits " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_misses_arr[@]}") 
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Cache Misses " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l2_hits_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L2 Cache Hits " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l2_misses_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L2 Cache Misses " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l1_energy_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L1 Energy (mJ) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${l2_energy_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "L2 Energy (mJ) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${dram_energy_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "DRAM Energy (mJ) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${total_energy_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "Total Energy (mJ) " "$mean" "$std_dev" >> "$OUTPUT_FILE"

        output2=$(python3 mean_std.py "${total_time_arr[@]}")
        mean=$(echo "$output2" | awk '/Mean:/ {printf "%.4f", $2}')
        std_dev=$(echo "$output2" | awk '/Standard deviation:/ {printf "%.4f", $3}')
        printf "%24s: %10s %10s\n" "Total Time (ms) " "$mean" "$std_dev" >> "$OUTPUT_FILE"
    done
done