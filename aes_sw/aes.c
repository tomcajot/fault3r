typedef unsigned char uint8_t;
typedef unsigned int uint32_t;

#define Nb 4   // number of columns (32-bit words) comprising the state
#define Nk 4   // number of 32-bit words comprising the key
#define Nr 10  // number of rounds
#define AES_BLOCK_SIZE 16
#define AES_KEY_SIZE 16

__attribute__((section(".fault_data"))) const unsigned int edit_area[50] = {
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0xFFFFFFFF};

void log_state(volatile uint32_t *addr, uint8_t *state) {
    // Convert 16 bytes to 4 32-bit words
    for (int i = 0; i < 4; i++) {
        uint32_t word = ((uint32_t)state[i * 4] << 24) |
                        ((uint32_t)state[i * 4 + 1] << 16) |
                        ((uint32_t)state[i * 4 + 2] << 8) |
                        ((uint32_t)state[i * 4 + 3]);
        addr[i] = word;
    }
}

// S-box for SubBytes transformation
static const uint8_t sbox[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b,
    0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26,
    0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2,
    0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed,
    0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f,
    0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
    0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14,
    0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d,
    0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f,
    0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11,
    0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f,
    0xb0, 0x54, 0xbb, 0x16};

// Key schedule structure
typedef struct {
    uint32_t words[Nb * (Nr + 1)];
} AESKeySchedule;

// Custom memcpy to avoid using <string.h>
void *memcpy(void *dest, const void *src, int len) {
    uint8_t *d = (uint8_t *)dest;
    const uint8_t *s = (const uint8_t *)src;
    for (int i = 0; i < len; i++) {
        d[i] = s[i];
    }
    return dest;
}

// Custom memset to avoid using <string.h>
void *memset(void *ptr, int value, int len) {
    uint8_t *p = (uint8_t *)ptr;
    for (int i = 0; i < len; i++) {
        p[i] = (uint8_t)value;
    }
    return ptr;
}

static uint32_t rotword(uint32_t a) { return (a >> 24) | (a << 8); }

static uint32_t subword(uint32_t a) {
    return (sbox[(a >> 24) & 0xff] << 24) | (sbox[(a >> 16) & 0xff] << 16) |
           (sbox[(a >> 8) & 0xff] << 8) | (sbox[(a) & 0xff]);
}

static uint8_t double_byte(uint8_t a) { return (a << 1) ^ ((a >> 7) * 0x1b); }

// Key expansion for AES-128
void aes_key_expansion(AESKeySchedule *ks, const uint8_t *key) {
    const uint32_t rcon[11] = {0x00000000, 0x01000000, 0x02000000, 0x04000000,
                               0x08000000, 0x10000000, 0x20000000, 0x40000000,
                               0x80000000, 0x1b000000, 0x36000000};

    // First 4 words are the original key
    for (int i = 0; i < Nk; i++) {
        ks->words[i] =
            ((uint32_t)key[4 * i] << 24) | ((uint32_t)key[4 * i + 1] << 16) |
            ((uint32_t)key[4 * i + 2] << 8) | ((uint32_t)key[4 * i + 3]);
    }

    // Generate remaining words
    for (int i = Nk; i < Nb * (Nr + 1); i++) {
        uint32_t temp = ks->words[i - 1];
        if (i % Nk == 0) {
            temp = subword(rotword(temp)) ^ rcon[i / Nk];
        }
        ks->words[i] = ks->words[i - Nk] ^ temp;
    }
}

// AddRoundKey transformation
static void add_round_key(uint8_t *state, const uint32_t *round_key) {
    for (int i = 0; i < 16; i++) {
        state[i] ^= (round_key[i / 4] >> (24 - 8 * (i % 4))) & 0xff;
    }
}

// SubBytes transformation
static void sub_bytes(uint8_t *state) {
    for (int i = 0; i < 16; i++) {
        state[i] = sbox[state[i]];
    }
}

// ShiftRows transformation
static void shift_rows(uint8_t *state) {
    uint8_t temp[16];

    // Row 0: no shift
    temp[0] = state[0];
    temp[4] = state[4];
    temp[8] = state[8];
    temp[12] = state[12];
    // Row 1: shift left by 1
    temp[1] = state[5];
    temp[5] = state[9];
    temp[9] = state[13];
    temp[13] = state[1];
    // Row 2: shift left by 2
    temp[2] = state[10];
    temp[6] = state[14];
    temp[10] = state[2];
    temp[14] = state[6];
    // Row 3: shift left by 3
    temp[3] = state[15];
    temp[7] = state[3];
    temp[11] = state[7];
    temp[15] = state[11];

    memcpy(state, temp, 16);
}

// MixColumns transformation
static void mix_columns(uint8_t *state) {
    uint8_t temp[16];

    for (int c = 0; c < 4; c++) {
        uint8_t *col = &state[c * 4];
        temp[c * 4 + 0] = double_byte(col[0]) ^ (double_byte(col[1]) ^ col[1]) ^
                          col[2] ^ col[3];
        temp[c * 4 + 1] = col[0] ^ double_byte(col[1]) ^
                          (double_byte(col[2]) ^ col[2]) ^ col[3];
        temp[c * 4 + 2] = col[0] ^ col[1] ^ double_byte(col[2]) ^
                          (double_byte(col[3]) ^ col[3]);
        temp[c * 4 + 3] = (double_byte(col[0]) ^ col[0]) ^ col[1] ^ col[2] ^
                          double_byte(col[3]);
    }

    memcpy(state, temp, 16);
}

void aes_encrypt(uint8_t *output, const uint8_t *input, const uint8_t *key) {
    AESKeySchedule ks;
    uint8_t state[16];

    // Key expansion
    aes_key_expansion(&ks, key);

    // Initialize state with input
    memcpy(state, input, 16);

    log_state((volatile uint32_t *)0x00020000, state);

    // Initial round
    add_round_key(state, &ks.words[0]);

    // Main rounds (9 rounds for AES-128)
    for (int round = 1; round < Nr; round++) {
        sub_bytes(state);
        shift_rows(state);
        mix_columns(state);
        add_round_key(state, &ks.words[round * Nb]);
        log_state((volatile uint32_t *)(0x00020000 + round * 0x10), state);
    }

    // Final round (no MixColumns)
    sub_bytes(state);
    shift_rows(state);
    log_state((volatile uint32_t *)(0x00020000 + Nr * 0x10), state);
    add_round_key(state, &ks.words[Nr * Nb]);
    log_state((volatile uint32_t *)(0x00020000 + (Nr + 1) * 0x10), state);

    // Copy result to output
    memcpy(output, state, 16);

    // Clear
    memset(state, 0, 16);
    memset((uint8_t *)&ks, 0, sizeof(ks));
}

int main() {
    uint8_t key[16] = {0x54, 0x68, 0x61, 0x74, 0x73, 0x20, 0x6D, 0x79,
                       0x20, 0x4B, 0x75, 0x6E, 0x67, 0x20, 0x46, 0x75};

    uint8_t plaintext[16] = {0x54, 0x77, 0x6F, 0x20, 0x4F, 0x6E, 0x65, 0x20,
                             0x4E, 0x69, 0x6E, 0x65, 0x20, 0x54, 0x77, 0x6F};

    uint8_t ciphertext[16];

    aes_encrypt(ciphertext, plaintext, key);

    return 0;
}
