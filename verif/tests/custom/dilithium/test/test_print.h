#define UART_REG_TXFIFO ((volatile uint8_t*)(0x10000000))

void print_str(const char *s);

void print_int(int num);