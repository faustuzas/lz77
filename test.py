from lz77_1 import LZ77Encoder
from lz77_dec import LZ77Decoder
import commons

offset_size_in_bits = 8
match_len_size_in_bits = 4

with commons.FileRawDataLoader('examples/short.txt') as loader:
    with commons.EncodingFileTripletIngestor('compressed.lz77', offset_size_in_bits, match_len_size_in_bits) as ingestor:
        encoder = LZ77Encoder(
            data_loader=loader,
            result_ingestor=ingestor,
            search_buff_size=commons.search_buff_size_for_bits(offset_size_in_bits),
            look_ahead_buff_size=commons.look_ahead_size_for_bits(match_len_size_in_bits)
        )

        encoder.encode()

with commons.DecodingFileTripletLoader('compressed.lz77') as loader:
    with commons.FileRawDataIngestor('result.txt') as ingestor:
        (offset_size_in_bits, _) = loader.encoding_meta_data

        decoder = LZ77Decoder(
            data_loader=loader,
            result_ingestor=ingestor,
            search_buff_size=commons.search_buff_size_for_bits(offset_size_in_bits)
        )

        decoder.decode()
