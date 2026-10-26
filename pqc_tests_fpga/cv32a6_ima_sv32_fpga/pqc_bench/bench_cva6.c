// newlib output for the PQC harnesses on CVA6: stdout on the NS16550 UART
// (57600 baud from the 25 MHz clock, as in the other pqc_tests_fpga programs)
#include <stdint.h>
#include <sys/stat.h>

#define UART_BASE 0x10000000
#define THR (*(volatile uint32_t *)(UART_BASE + 0x00))
#define DLL (*(volatile uint32_t *)(UART_BASE + 0x00))
#define DLM (*(volatile uint32_t *)(UART_BASE + 0x04))
#define LCR (*(volatile uint32_t *)(UART_BASE + 0x0C))
#define LSR (*(volatile uint32_t *)(UART_BASE + 0x14))

__attribute__((constructor)) static void uart_init(void)
{
    LCR = 0x80; // divisor latch access
    DLL = 0x1B; // 25 MHz / (16 * 27) = 57870 baud (57600 nominal)
    DLM = 0x00;
    LCR = 0x03; // 8N1
}

static void uart_putchar(char c)
{
    while ((LSR & 0x20) == 0)
        ;
    THR = c;
}

int _write(int fd, const char *buf, int len)
{
    (void)fd;
    for (int i = 0; i < len; i++) {
        if (buf[i] == '\n')
            uart_putchar('\r');
        uart_putchar(buf[i]);
    }
    return len;
}

// a terminal: newlib then flushes stdout at every newline
int _isatty(int fd) { (void)fd; return 1; }
int _fstat(int fd, struct stat *st) { (void)fd; st->st_mode = S_IFCHR; return 0; }
