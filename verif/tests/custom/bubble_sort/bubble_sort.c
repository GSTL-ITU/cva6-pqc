#include <stdint.h>
#include "test_print.h"

#define UART_REG_TXFIFO ((volatile uint8_t*)(0x10000000))

// Standard Bubble Sort for floats
void bubble_sort(volatile float* arr, int len) {
    int sort_num;
    do {
        sort_num = 0;
        for(int i = 0; i < len - 1; i++) {
            if(arr[i] > arr[i+1]) {
                float tmp = arr[i];
                arr[i] = arr[i+1];
                arr[i+1] = tmp;
                sort_num++;
            }
        } 
    } while(sort_num != 0);
}

// Verification function
int check_arrays_equal(volatile float* arr1, volatile float* arr2, int len) {
    for (int i = 0; i < len; i++) {
        if (arr1[i] != arr2[i]) {
            return 0;
        }
    }
    return 1;
}

int main() {
    // Test data
    volatile float unsorted_arr[] = {195.5f, 14.1f, 176.8f, 103.0f, 54.4f, 32.2f, 128.9f};
    volatile float sorted_arr[]   = {14.1f, 32.2f, 54.4f, 103.0f, 128.9f, 176.8f, 195.5f};
    int len = 7;

#ifdef PRINT_CYCLES
    uint32_t start_cycles = get_cycles();
#endif

    // Execute the sort using hardware FPU
    bubble_sort(unsorted_arr, len);

#ifdef PRINT_CYCLES
    uint32_t end_cycles = get_cycles();
#endif
    
    // Final result check
    if (check_arrays_equal(unsorted_arr, sorted_arr, len)) {
        print_str("SUCCESS!\n");
    } else {
        print_str("FAILURE!\n");
    }

#ifdef PRINT_CYCLES
    print_str("CYCLES:");
    print_int(end_cycles - start_cycles);
    print_str("\n");
#endif

    return 0;
}