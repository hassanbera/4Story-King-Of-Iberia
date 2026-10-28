#include <zlib.h>
#include <cassert>
#include <cstring>
#include <iostream>

int main()
{
    const char input[] = "King Of Iberia legacy-header compression roundtrip";
    Bytef compressed[256] = {0}, restored[256] = {0};
    z_stream encoder = {0};
    assert(deflateInit(&encoder, Z_DEFAULT_COMPRESSION) == Z_OK);
    encoder.next_in = reinterpret_cast<Bytef *>(const_cast<char *>(input));
    encoder.avail_in = sizeof(input);
    encoder.next_out = compressed;
    encoder.avail_out = sizeof(compressed);
    assert(deflate(&encoder, Z_FINISH) == Z_STREAM_END);
    uLong compressedSize = encoder.total_out;
    assert(deflateEnd(&encoder) == Z_OK);
    z_stream decoder = {0};
    assert(inflateInit(&decoder) == Z_OK);
    decoder.next_in = compressed;
    decoder.avail_in = compressedSize;
    decoder.next_out = restored;
    decoder.avail_out = sizeof(restored);
    assert(inflate(&decoder, Z_FINISH) == Z_STREAM_END);
    assert(decoder.total_out == sizeof(input));
    assert(memcmp(restored, input, sizeof(input)) == 0);
    assert(inflateEnd(&decoder) == Z_OK);
    std::cout << "Legacy zlib header and rebuilt library roundtrip passed.\n";
    return 0;
}
